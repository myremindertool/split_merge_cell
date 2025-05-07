import streamlit as st
import pandas as pd
import io
import re

# Clean date function: remove time, normalize slashes, and reverse ISO
def full_clean_date(val):
    val = str(val).strip()
    val = val.split()[0]  # Remove time part
    val = val.replace("-", "/")
    parts = val.split("/")
    if len(parts[0]) == 4:  # If starts with year, reverse
        val = f"{parts[2]}/{parts[1]}/{parts[0]}"
    return val

# Generic split function
def generic_split(val, delimiter, parts):
    chunks = str(val).split(delimiter, maxsplit=parts - 1)
    return chunks + [''] * (parts - len(chunks))

# Save to Excel
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

# UI starts here
st.title("🧼 Multi-Date Column Cleaner & Column Splitter")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    output_df = df.copy()

    st.write("📋 File Preview:")
    st.dataframe(df.head())

    # Allow multiple date columns to clean
    date_columns = st.multiselect("🗓️ Select date column(s) to clean (will replace originals)", df.columns)

    column = None
    delimiter = None
    num_parts = None

    # If no date columns selected, allow regular split
    if not date_columns:
        column = st.selectbox("📌 Select a column to split", df.columns)
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
