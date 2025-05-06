import streamlit as st
import pandas as pd

# Manual date cleaner that avoids pd.to_datetime completely
def manually_clean_date(val):
    val = str(val).strip()

    # Acceptable: '2025-05-04', '24/03/2025', '2021-01-04 00:00:00', etc.
    val = val.split(' ')[0].strip()  # Remove time part
    val = val.replace('-', '/')

    # Now reformat manually if structure is YYYY/MM/DD
    if val.count('/') == 2:
        parts = val.split('/')
        # Handle YYYY/MM/DD or DD/MM/YYYY by checking year size
        if len(parts[0]) == 4:
            # It's YYYY/MM/DD — reorder
            year, month, day = parts
            val = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        elif len(parts[2]) == 4:
            # Already DD/MM/YYYY
            day, month, year = parts
            val = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        else:
            val = ''
    else:
        val = ''

    return "'" + val if val else ''

def split_column(df, column, delimiter, parts):
    if delimiter == 'Manual Date Formatter':
        df['Date'] = df[column].apply(manually_clean_date)
        df['Time'] = df[column].astype(str).apply(lambda x: x.split(' ')[1] if ' ' in x and ':' in x else '')
    else:
        split_data = df[column].astype(str).str.split(delimiter, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Streamlit App UI
st.title("✅ Excel-Proof Date Splitter (Manual Safe Mode)")

uploaded_file = st.file_uploader("📁 Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📄 Preview of Uploaded Data:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Choose column to clean/split", df.columns)

    split_option = st.selectbox(
        "⚙️ Select split method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Manual Date Formatter"]
    )

    delimiter_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Manual Date Formatter": "manual"
    }

    if split_option != "Manual Date Formatter":
        num_parts = st.slider("🔢 Number of parts", 2, 4, value=2)

    if st.button("🚀 Run Split"):
        if split_option == "Manual Date Formatter":
            df = split_column(df, column, "manual", 2)
        else:
            df = split_column(df, column, delimiter_map[split_option], num_parts)

        st.success("✅ Done!")
        st.dataframe(df.head())

        df.to_excel("split_output.xlsx", index=False)
        with open("split_output.xlsx", "rb") as f:
            st.download_button("📥 Download Output Excel", f, file_name="split_output.xlsx")
