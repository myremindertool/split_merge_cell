import streamlit as st
import pandas as pd
import io
import re

# Function: clean date, convert ISO to DD/MM/YYYY, remove time
def clean_date_only(val):
    val = str(val).strip().replace("-", "/")
    parts = val.split("/")

    # Reverse if starts with year (e.g., 2022/02/03)
    if len(parts[0]) == 4:
        val = f"{parts[2]}/{parts[1]}/{parts[0]}"

    # Remove time if present
    val = re.sub(r'\s*\d{1,2}:\d{2}:\d{2}.*', '', val)

    # Extract only valid date part
    match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", val)
    return match.group(0) if match else val

# Fallback: split normally by delimiter
def generic_split(val, delimiter, parts):
    chunks = str(val).split(delimiter, maxsplit=parts - 1)
    return chunks + [''] * (parts - len(chunks))

# Export to Excel
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

# UI
st.title("🧼 Clean Date Column or Split Any Column")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 Preview of uploaded file:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Select column to process", df.columns)

    is_date = st.checkbox("🗓️ Is this a date column with mixed formats?")

    if not is_date:
        method = st.selectbox("✂️ Choose delimiter", ["Space", "Comma", "Hyphen (-)", "Slash (/)", "Underscore (_)"])
        method_map = {
            "Space": " ",
            "Comma": ",",
            "Hyphen (-)": "-",
            "Slash (/)": "/",
            "Underscore (_)": "_"
        }
        delimiter = method_map[method]
        num_parts = st.slider("🔢 Number of parts", 2, 5, value=2)

    if st.button("🚀 Run Processing"):
        if is_date:
            df["Cleaned_Date"] = df[column].apply(clean_date_only)
            output_df = df[["Cleaned_Date"]]
        else:
            split_data = df[column].apply(lambda x: generic_split(x, delimiter, num_parts))
            split_df = pd.DataFrame(split_data.tolist(), columns=[f"{column}_Part{i+1}" for i in range(num_parts)])
            output_df = pd.concat([df, split_df], axis=1)

        st.success("✅ Done!")
        st.dataframe(output_df.head())

        excel_data = write_excel(output_df)
        st.download_button(
            label="📥 Download Output Excel",
            data=excel_data,
            file_name="processed_column_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
