import streamlit as st
import pandas as pd
import io

# ✅ Safe & robust date cleaner
def full_clean_date(val):
    val = str(val).strip()
    
    if not val or val.lower() in ["nan", "none"]:
        return ""

    try:
        # Remove time if present
        val = val.split()[0]
        val = val.replace("-", "/")
        parts = val.split("/")

        if len(parts) == 3 and len(parts[0]) == 4:
            # Reverse YYYY/MM/DD to DD/MM/YYYY
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        elif len(parts) == 3:
            return f"{parts[0]}/{parts[1]}/{parts[2]}"
        else:
            return val
    except Exception:
        return val

# ✂️ Robust splitter
def generic_split(val, delimiter, parts):
    try:
        chunks = str(val).split(delimiter, maxsplit=parts - 1)
        return chunks + [''] * (parts - len(chunks))
    except Exception:
        return [''] * parts

# 💾 Save processed output to Excel
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

# 🎛️ Streamlit App
st.title("🧼 Clean & Split Excel Columns")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    output_df = df.copy()

    st.write("📋 File Preview:")
    st.dataframe(df.head())

    # Date column cleaner
    date_columns = st.multiselect("🗓️ Select date column(s) to clean (DD/MM/YYYY)", df.columns)

    # Fallback: Column Splitter
    column = None
    delimiter = None
    num_parts = None

    if not date_columns:
        column = st.selectbox("📌 Select a column to split (if not date)", df.columns)
        method = st.selectbox("✂️ Choose delimiter", ["Space", "Comma", "Hyphen (-)", "Slash (/)", "Underscore (_)"])
        method_map = {
            "Space": " ",
            "Comma": ",",
            "Hyphen (-)": "-",
            "Slash (/)": "/",
            "Underscore (_)": "_"
        }
        delimiter = method_map[method]
        num_parts = st.slider("🔢 Number of parts to split into", 2, 5, value=2)

    if st.button("🚀 Run Processing"):
        try:
            if date_columns:
                for col in date_columns:
                    output_df[col] = output_df[col].apply(full_clean_date)
                st.success(f"✅ Cleaned and replaced date column(s): {', '.join(date_columns)}")

            elif column:
                split_data = df[column].apply(lambda x: generic_split(x, delimiter, num_parts))
                split_df = pd.DataFrame(split_data.tolist(), columns=[f"{column}_Part{i+1}" for i in range(num_parts)])
                output_df = pd.concat([df, split_df], axis=1)
                st.success(f"✅ Split column '{column}' into {num_parts} parts.")

            else:
                st.warning("⚠️ Please select at least one column to clean or split.")

            st.dataframe(output_df.head())

            excel_data = write_excel(output_df)
            st.download_button(
                label="📥 Download Cleaned Excel",
                data=excel_data,
                file_name="cleaned_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")
