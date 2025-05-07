import streamlit as st
import pandas as pd
import io
import re

# 🔁 Full cleaning: remove time, normalize, and reverse if needed
def full_clean_date(val):
    val = str(val).strip()
    val = val.split()[0]  # remove time part
    val = val.replace("-", "/")

    parts = val.split("/")
    if len(parts[0]) == 4:  # reverse YYYY/MM/DD
        val = f"{parts[2]}/{parts[1]}/{parts[0]}"
    return val

# 🪓 Generic split function
def generic_split(val, delimiter, parts):
    chunks = str(val).split(delimiter, maxsplit=parts - 1)
    return chunks + [''] * (parts - len(chunks))

# 💾 Write Excel to buffer
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

# 🧠 Start Streamlit UI
st.title("🧼 Multi-Date Column Cleaner & Splitter")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    # 🔘 Select multiple date columns
    date_columns = st.multiselect("🗓️ Select date column(s) to clean", df.columns)

    output_df = df.copy()

    if not date_columns:
        # Fallback to regular split
        column = st.selectbox("📌 Select a column to split (if not cleaning date)", df.columns)
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
        if date_columns:
            for col in date_columns:
                output_df[col] = output_df[col].apply(full_clean_date)
            st.success(f"✅ Cleaned date columns: {', '.join(date_columns)}")
        else:
            split_data = df[column].apply(lambda x: generic_split(x, delimiter, num_parts))
            split_df = pd.DataFrame(split_data.tolist(), columns=[f"{column}_Part{i+1}" for i in range(num_parts)])
            output_df = pd.concat([df, split_df], axis=1)
            st.success(f"✅ Split '{column}' into {num_parts} parts.")

        st.dataframe(output_df.head())

        excel_data = write_excel(output_df)
        st.download_button(
            label="📥 Download Cleaned Excel",
            data=excel_data,
            file_name="cleaned_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
