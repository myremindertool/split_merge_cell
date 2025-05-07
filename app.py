import streamlit as st
import pandas as pd
import io
import re

# 🧠 Clean and format date (remove time, reverse if ISO)
def full_clean_date(val):
    val = str(val).strip()

    # Step 1: Remove time part (e.g., ' 00:00:00')
    val = val.split()[0]

    # Step 2: Normalize separator
    val = val.replace("-", "/")

    # Step 3: Reverse if it starts with a year
    parts = val.split("/")
    if len(parts[0]) == 4:
        val = f"{parts[2]}/{parts[1]}/{parts[0]}"

    return val

# 🧩 Generic string split
def generic_split(val, delimiter, parts):
    chunks = str(val).split(delimiter, maxsplit=parts - 1)
    return chunks + [''] * (parts - len(chunks))

# 💾 Save Excel file
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

# 🌐 Streamlit Interface
st.title("🧼 Smart Column Cleaner + Splitter")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 Preview of uploaded file:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Select the column to process", df.columns)

    is_date = st.checkbox("🗓️ Is this a date column with ISO/time format?")

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
        num_parts = st.slider("🔢 Number of parts to split into", 2, 5, value=2)

    if st.button("🚀 Run Processing"):
        if is_date:
            df["Cleaned_Date"] = df[column].apply(full_clean_date)
            output_df = df  # Keep full original data + new cleaned column
        else:
            split_data = df[column].apply(lambda x: generic_split(x, delimiter, num_parts))
            split_df = pd.DataFrame(split_data.tolist(), columns=[f"{column}_Part{i+1}" for i in range(num_parts)])
            output_df = pd.concat([df, split_df], axis=1)

        st.success("✅ Done! Your cleaned/split data is below.")
        st.dataframe(output_df.head())

        excel_data = write_excel(output_df)
        st.download_button(
            label="📥 Download Cleaned Excel",
            data=excel_data,
            file_name="processed_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
