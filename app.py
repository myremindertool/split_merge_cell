import streamlit as st
import pandas as pd
import re

def clean_and_format_date(raw_value):
    # Ensure string format
    val = str(raw_value).strip()

    # Extract only date part: supports YYYY-MM-DD or DD/MM/YYYY or any messy mix
    # Cut at 10 characters if it looks like date
    possible_date = val[:10].replace('-', '/')

    try:
        parsed = pd.to_datetime(possible_date, dayfirst=True, errors='coerce')
        return "'" + parsed.strftime('%d/%m/%Y') if not pd.isnull(parsed) else ''
    except:
        return ''

def split_column(df, column, delimiter, parts):
    if delimiter == 'Robust Date Cleaner':
        df['Date'] = df[column].apply(clean_and_format_date)

        # Optional Time — only extract if truly separate from date
        df['Time'] = df[column].astype(str).apply(
            lambda x: pd.to_datetime(x, errors='coerce').strftime('%I:%M %p') if ' ' in x or ':' in x else ''
        )
    else:
        split_data = df[column].astype(str).str.split(delimiter, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Streamlit Interface
st.title("📊 Robust Excel Date Splitter (Safe from 00:00:00 Bug)")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("🧩 Select a column", df.columns)

    split_option = st.selectbox(
        "🧰 Choose method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Robust Date Cleaner"]
    )

    delimiter_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Robust Date Cleaner": "clean"
    }

    if split_option != "Robust Date Cleaner":
        num_parts = st.slider("🔢 How many parts?", 2, 4, 2)

    if st.button("🚀 Split Column"):
        if split_option == "Robust Date Cleaner":
            df = split_column(df, column, "clean", 2)
        else:
            df = split_column(df, column, delimiter_map[split_option], num_parts)

        st.success("✅ Processed successfully!")
        st.dataframe(df.head())

        df.to_excel("split_output.xlsx", index=False)
        with open("split_output.xlsx", "rb") as f:
            st.download_button("📥 Download Excel", f, file_name="split_output.xlsx")
