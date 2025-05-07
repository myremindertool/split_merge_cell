import streamlit as st
import pandas as pd
import io
import re

# Function to clean and split date values (your logic)
def clean_and_split_date(val):
    val = str(val).strip().replace("-", "/")
    parts = val.split("/")

    # Reverse if it starts with year (YYYY/MM/DD)
    if len(parts[0]) == 4:
        val = f"{parts[2]}/{parts[1]}/{parts[0]}"

    chars = list(val)
    return chars, val

# Standard split by delimiter
def generic_split(val, delimiter, parts):
    chunks = str(val).split(delimiter, maxsplit=parts - 1)
    return chunks + [''] * (parts - len(chunks))

# Write to Excel
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.read()

# Streamlit UI
st.title("🔀 Smart Column Splitter")

uploaded_file = st.file_uploader(📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaed_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Select column to split", df.columns)

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
        num_parts = st.slider("🔢 Number of parts to split into", 2, 5, value=2)

    if st.button("🚀 Process"):
        if is_date:
            char_lists, clean_values = zip(*df[column].apply(clean_and_split_date))
            max_len = max(len(chars) for chars in char_lists)
            char_df = pd.DataFrame([chars + [''] * (max_len - len(chars)) for chars in char_lists])
            char_df.columns = [f"Char{i+1}" for i in range(max_len)]
            char_df["Cleaned_Value"] = clean_values
            output_df = char_df
        else:
            split_data = df[column].apply(lambda x: generic_split(x, delimiter, num_parts))
            output_df = pd.concat([df, pd.DataFrame(split_data.tolist(), columns=[f"{column}_Part{i+1}" for i in range(num_parts)])], axis=1)

        st.success("✅ Done!")
        st.dataframe(output_df.head())

        final_excel = write_excel(output_df)
        st.download_button(
            label="📥 Download Split Excel",
            data=final_excel,
            file_name="split_column_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
