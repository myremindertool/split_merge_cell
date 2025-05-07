import streamlit as st
import pandas as pd
import io
import re

# ✅ Force consistent date + optional time, as text (Excel-safe)
def clean_and_split_datetime(val):
    val = str(val).strip()

    try:
        dt = pd.to_datetime(val, errors='coerce', dayfirst=True)
        if pd.isnull(dt):
            return "'" + val, ""  # fallback raw text
        date_str = "'" + dt.strftime('%d/%m/%Y')  # force uniform date format with apostrophe
        time_str = dt.strftime('%H:%M:%S') if dt.time() != pd.Timestamp(0).time() else ""
        return date_str, time_str
    except Exception:
        return "'" + val, ""

# Apply logic to the selected column
def split_column(df, column, method, parts):
    if method == 'Split Date and Time':
        df['DOJ_Part1'], df['DOJ_Part2'] = zip(*df[column].apply(clean_and_split_datetime))
    else:
        split_data = df[column].astype(str).str.split(method, n=parts - 1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Save Excel as openpyxl (string-safe)
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.read()

# Streamlit UI
st.title("📅 Uniform Date + Time Splitter (Excel-Proof Output)")

uploaded_file = st.file_uploader("📁 Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Select the column to split", df.columns)

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
        num_parts = st.slider("🔢 How many parts to split into?", 2, 4, value=2)

    if st.button("🚀 Run Split"):
        if method == "Split Date and Time":
            df = split_column(df, column, "datetime", 2)
        else:
            df = split_column(df, column, method_map[method], num_parts)

        st.success("✅ Done! Uniform date format applied.")
        st.dataframe(df.head())

        # Optional: add format check column
        df['Date_Format_Flag'] = df['DOJ_Part1'].apply(
            lambda x: 'OK' if re.match(r"'\d{2}/\d{2}/\d{4}", str(x)) else 'BAD'
        )

        excel_data = write_excel(df)

        st.download_button(
            label="📥 Download Clean Excel File",
            data=excel_data,
            file_name="clean_split_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
