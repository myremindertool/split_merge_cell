import streamlit as st
import pandas as pd
import re

# Helper to normalize mixed date formats to DD/MM/YYYY
def normalize_date_column(series):
    cleaned = []
    for val in series.astype(str):
        val = val.strip()
        try:
            if '/' in val:
                # DD/MM/YYYY
                parsed = pd.to_datetime(val, dayfirst=True, errors='coerce')
            elif '-' in val:
                # YYYY-MM-DD
                parsed = pd.to_datetime(val, dayfirst=False, errors='coerce')
            else:
                parsed = pd.to_datetime(val, errors='coerce')

            formatted = parsed.strftime('%d/%m/%Y') if not pd.isnull(parsed) else ''
        except:
            formatted = ''
        cleaned.append(formatted)
    return cleaned

# Main column splitting function
def split_column(df, column, delimiter, parts):
    if delimiter == 'Date & Time Split':
        # Normalize full datetime string first
        date_series = pd.to_datetime(df[column], errors='coerce')
        df['Date'] = normalize_date_column(df[column])
        
        # Extract time if present
        times = []
        for val in df[column].astype(str):
            match_time = re.search(r'\d{1,2}:\d{2}(:\d{2})?(\s*[APMapm]{2})?', val)
            if match_time:
                time_str = match_time.group(0)
                parsed_time = pd.to_datetime(time_str, errors='coerce')
                times.append(parsed_time.strftime('%I:%M %p') if not pd.isnull(parsed_time) else '')
            else:
                times.append('')
        df['Time'] = times
    else:
        # General text delimiter split
        split_data = df[column].astype(str).str.split(delimiter, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Streamlit UI
st.title("📊 Excel Column Splitter Tool")

uploaded_file = st.file_uploader("📁 Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("🔍 Preview of Uploaded File:")
    st.dataframe(df.head())

    column = st.selectbox("🧩 Select a column to split", df.columns)

    split_option = st.selectbox(
        "🔣 How do you want to split?",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Date & Time Split"]
    )

    delimiter_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Date & Time Split": "Date & Time Split"
    }

    if split_option != "Date & Time Split":
        num_parts = st.slider("🔢 How many parts to split into?", min_value=2, max_value=4, value=2)

    if st.button("🚀 Split Column"):
        if split_option == "Date & Time Split":
            df = split_column(df, column, "Date & Time Split", 2)
        else:
            df = split_column(df, column, delimiter_map[split_option], num_parts)

        st.success("✅ Column split successfully!")
        st.dataframe(df.head())

        output_file = "split_output.xlsx"
        df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button("📥 Download Result", f, file_name="split_output.xlsx")
