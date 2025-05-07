import streamlit as st
import pandas as pd
import io
import re

# Clean and standardize dates, remove time
def clean_date_only(val):
    val = str(val).strip().replace("-", "/")
    parts = val.split("/")

    # If starts with year, reverse it
    if len(parts[0]) == 4:
        val = f"{parts[2]}/{parts[1]}/{parts[0]}"

    # Extract just the date in DD/MM/YYYY
    match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", val)
    return match.group(1) if match else val

# Generic split for non-date columns
def generic_split(val, delimiter, parts):
    chunks = str(val).split(delimiter, maxsplit=parts - 1)
    return chunks + [''] * (parts - len(chunks))

# Save DataFrame to Excel
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.read()

# Streamlit App
st.title("🧼 jo Clean Date Splitter or Column Split Tool")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Select column to process", df.columns)

    is_date = st.checkbox("🗓️ Is this a date column (e.g. 2022-03-15)?")

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

    if st.button("🚀 Process"):
        if is_date:
            df["Cleaned_Date"] = df[column].apply(clean_date_only)
            output_df = df[["Cleaned_Date"]]
        else:
            split_data = df[column].apply(lambda x: generic_split(x, delimiter, num_parts))
            split_df = pd.DataFrame(split_data.tolist(), columns=[f"{column}_Part{i+1}" for i in range(num_parts)])
            output_df = pd.concat([df, split_df], axis=1)

        st.success("✅ Processing complete.")
        st.dataframe(output_df.head())

        final_excel = write_excel(output_df)
        st.download_button(
            label="📥 Download Result",
            data=final_excel,
            file_name="column_split_cleaned.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
