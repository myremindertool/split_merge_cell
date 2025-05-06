import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# ✅ Force all date strings to behave as plain text in Excel using apostrophe
def clean_and_split_datetime(val):
    val = str(val).strip()

    # Detect if there's a time portion
    if ' ' in val and re.search(r'\d{1,2}:\d{2}', val):
        date_part, time_part = val.split(' ', 1)
    else:
        date_part, time_part = val, ""

    # Try converting and formatting date
    try:
        dt = pd.to_datetime(date_part, dayfirst=True, errors='coerce')
        if not pd.isnull(dt):
            date_str = "'" + dt.strftime('%d/%m/%Y')  # ← Add apostrophe for Excel-safe text
            return date_str, time_part.strip()
    except:
        pass

    # If parsing fails, return raw string with apostrophe
    return "'" + date_part.strip(), time_part.strip()

# 🧠 Main split function
def split_column(df, column, method, parts):
    if method == 'Split Date and Time':
        df['DOJ_Part1'], df['DOJ_Part2'] = zip(*df[column].apply(clean_and_split_datetime))
    else:
        split_data = df[column].astype(str).str.split(method, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# 💾 Write to Excel (openpyxl to avoid formula/formatting issues)
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.read()

# 🖼️ Streamlit App
st.title("📅 Excel-Proof Date & Time Splitter")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("🧩 Select column to split", df.columns)

    method = st.selectbox(
        "⚙️ Choose split method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Split Date and Time"]
    )

    method_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Split Date and Time": "datetime"
    }

    if method != "Split Date and Time":
        num_parts = st.slider("🔢 Number of parts", 2, 4, 2)

    if st.button("🚀 Split Now"):
        if method == "Split Date and Time":
            df = split_column(df, column, "datetime", 2)
        else:
            df = split_column(df, column, method_map[method], num_parts)

        st.success("✅ Split Completed!")
        st.dataframe(df.head())

        final_excel = write_excel(df)

        st.download_button(
            label="📥 Download Excel File",
            data=final_excel,
            file_name="split_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
