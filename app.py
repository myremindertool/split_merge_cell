import streamlit as st
import pandas as pd
import io

# ✅ Robust date cleaner: handles empty, malformed, or ISO dates
def full_clean_date(val):
    val = str(val).strip()

    if not val or val.lower() in ["nan", "none"]:
        return ""

    try:
        val = val.split()[0]  # Remove time
        val = val.replace("-", "/")
        parts = val.split("/")

        if len(parts) == 3 and len(parts[0]) == 4:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"  # Reverse ISO
        elif len(parts) == 3:
            return f"{parts[0]}/{parts[1]}/{parts[2]}"
        else:
            return val
    except Exception:
        return val

# ✅ Safe generic split for any string column
def generic_split(val, delimiter, parts):
    try:
        chunks = str(val).split(delimiter, maxsplit=parts - 1)
        return chunks + [''] * (parts - len(chunks))
    except Exception:
        return [''] * parts

# 💾 Export as Excel
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

# 🚀 Streamlit UI
st.title("🧼 Clean & Split Columns Tool")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    output_df = df.copy()

    st.write("📋 Preview of uploaded file:")
    st.dataframe(df.head())

    # 🔁 Clean multiple date columns
    date_columns = st.multiselect("🗓️ Select column(s) to clean as date (DD/MM/YYYY)", df.columns)

    # ✂️ Split multiple string columns
    split_columns = st.multiselect("🔤 Select column(s) to split by delimiter", df.columns)

    if split_columns:
        method = st.selectbox("✂️ Choose delimiter", ["Space", "Comma", "Hyphen (-)", "Slash (/)", "Underscore (_)"])
        method_map = {
            "Space": " ",
            "Comma": ",",
            "Hyphen (-)": "-",
            "Slash (/)": "/",
            "Underscore (_)": "_"
        }
        delimiter = method_map[method]
        num_parts = st.slider("🔢 Number of parts to split each into", 2, 5, value=2)

    if st.button("🚀 Run Processing"):
        try:
            # Clean date columns
            if date_columns:
                for col in date_columns:
                    output_df[col] = output_df[col].apply(full_clean_date)
                st.success(f"✅ Cleaned and replaced date column(s): {', '.join(date_columns)}")

            # Split selected text columns
            if split_columns:
                for col in split_columns:
                    split_data = output_df[col].apply(lambda x: generic_split(x, delimiter, num_parts))
                    split_df = pd.DataFrame(split_data.tolist(), columns=[f"{col}_Part{i+1}" for i in range(num_parts)])
                    output_df = pd.concat([output_df, split_df], axis=1)
                st.success(f"✅ Split column(s): {', '.join(split_columns)} into {num_parts} parts.")

            if not date_columns and not split_columns:
                st.warning("⚠️ Please select at least one column to clean or split.")

            st.dataframe(output_df.head())

            excel_data = write_excel(output_df)
            st.download_button(
                label="📥 Download Final Excel",
                data=excel_data,
                file_name="cleaned_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")
