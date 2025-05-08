import streamlit as st
import pandas as pd
import io
import re
import requests

# ====================
# Helper Functions
# ====================

def full_clean_date(val):
    val = str(val).strip()
    if not val or val.lower() in ["nan", "none"]:
        return ""
    try:
        val = val.split()[0]
        val = val.replace("-", "/")
        parts = val.split("/")
        if len(parts) == 3 and len(parts[0]) == 4:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        elif len(parts) == 3:
            return f"{parts[0]}/{parts[1]}/{parts[2]}"
        else:
            return val
    except Exception:
        return val

def generic_split(val, delimiter, parts):
    try:
        chunks = str(val).split(delimiter, maxsplit=parts - 1)
        return chunks + [''] * (parts - len(chunks))
    except Exception:
        return [''] * parts

def load_google_sheet(gsheet_url):
    try:
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', gsheet_url)
        if not match:
            return None, "❌ Invalid Google Sheet URL"
        sheet_id = match.group(1)
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
        response = requests.get(csv_url)
        if response.status_code != 200:
            return None, "❌ Unable to fetch Google Sheet. Check link and sharing settings."
        return pd.read_excel(io.BytesIO(response.content)), None
    except Exception as e:
        return None, f"❌ Error: {e}"

def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

def apply_cleaning(val, mode):
    val = str(val)
    if mode == "Keep only digits":
        return ''.join(filter(str.isdigit, val))
    elif mode == "Remove currency symbols (₹, $, €, etc.)":
        return re.sub(r'[₹$€£¥₨]', '', val)
    elif mode == "Remove commas and % signs":
        return val.replace(",", "").replace("%", "")
    elif mode == "Keep only letters and numbers":
        return re.sub(r'[^A-Za-z0-9]', '', val)
    return val

# ====================
# Streamlit App
# ====================

st.title("🧼 Smart Excel + Google Sheet Cleaner & Splitter")

data_source = st.radio("📥 Provide data from:", ["Upload Excel File", "Paste Google Sheet Link"])

df = None
error = None

if data_source == "Upload Excel File":
    uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

elif data_source == "Paste Google Sheet Link":
    gsheet_url = st.text_input("🌐 Paste Google Sheet Link")
    if gsheet_url:
        df, error = load_google_sheet(gsheet_url)
        if error:
            st.error(error)

if df is not None:
    st.success("✅ Data loaded successfully!")
    st.dataframe(df.head())

    # ===== DATE CLEANING =====
    st.markdown("---")
    st.subheader("🗓️ Clean Date Columns")
    date_columns = st.multiselect("Select date column(s) to clean", df.columns)
    if date_columns:
        for col in date_columns:
            df[col] = df[col].apply(full_clean_date)
        st.success(f"✅ Cleaned and replaced date column(s): {', '.join(date_columns)}")
        st.dataframe(df.head())

    # ===== SYMBOL / NUMBER CLEANING =====
    st.markdown("---")
    st.subheader("🧽 Clean Numbers / Symbols")
    clean_cols = st.multiselect("Select column(s) to clean symbols/currency", df.columns)
    if clean_cols:
        clean_option = st.radio("Choose cleaning rule to apply", [
            "Keep only digits",
            "Remove currency symbols (₹, $, €, etc.)",
            "Remove commas and % signs",
            "Keep only letters and numbers"
        ])
        for col in clean_cols:
            df[col] = df[col].apply(lambda x: apply_cleaning(x, clean_option))
        st.success(f"✅ Applied '{clean_option}' to column(s): {', '.join(clean_cols)}")
        st.dataframe(df[clean_cols].head())

    # ===== MULTI-COLUMN SPLIT =====
    st.markdown("---")
    st.subheader("🔤 Split Columns")
    split_columns = st.multiselect("Select column(s) to split", df.columns)
    if split_columns:
        method = st.selectbox("Choose delimiter", ["Space", "Comma", "Hyphen (-)", "Slash (/)", "Underscore (_)"])
        method_map = {
            "Space": " ",
            "Comma": ",",
            "Hyphen (-)": "-",
            "Slash (/)": "/",
            "Underscore (_)": "_"
        }
        delimiter = method_map[method]
        num_parts = st.slider("Number of parts", 2, 5, value=2)
        for col in split_columns:
            split_data = df[col].apply(lambda x: generic_split(x, delimiter, num_parts))
            split_df = pd.DataFrame(split_data.tolist(), columns=[f"{col}_Part{i+1}" for i in range(num_parts)])
            df = pd.concat([df, split_df], axis=1)
        st.success(f"✅ Split {', '.join(split_columns)} into {num_parts} parts each.")
        st.dataframe(df.head())

    # ===== MERGE COLUMNS =====
    st.markdown("---")
    st.subheader("🔗 Merge Multiple Columns")
    merge_cols = st.multiselect("Select 2–5 columns to merge", df.columns)
    if merge_cols and len(merge_cols) > 1:
        separator_option = st.selectbox("Choose a separator", ["Space", "Comma", "Dash", "Custom"])
        if separator_option == "Space":
            separator = " "
        elif separator_option == "Comma":
            separator = ", "
        elif separator_option == "Dash":
            separator = "-"
        else:
            separator = st.text_input("Custom separator", value=" ")

        new_col_name = st.text_input("Name of the merged column", value="Merged_Column")

        if st.button("🧬 Merge Columns"):
            try:
                df[new_col_name] = df[merge_cols].astype(str).apply(lambda row: separator.join(row), axis=1)
                st.success(f"✅ Merged into '{new_col_name}'")
                st.dataframe(df[[*merge_cols, new_col_name]].head())
            except Exception as e:
                st.error(f"❌ Error merging columns: {e}")

    # ===== DOWNLOAD =====
    st.markdown("---")
    st.subheader("📤 Download Cleaned File")
    excel_data = write_excel(df)
    st.download_button(
        label="📥 Download Excel File",
        data=excel_data,
        file_name="cleaned_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
