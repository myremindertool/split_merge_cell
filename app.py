import streamlit as st
import pandas as pd

def reconstruct_date(row_chars):
    # Join characters, sanitize, and match proper date
    raw = ''.join(row_chars).strip()

    # Fix common separator issues
    raw = raw.replace('-', '/').replace(' ', '')

    # Handle known length and format only
    try:
        parsed = pd.to_datetime(raw, dayfirst=True, errors='coerce')
        return "'" + parsed.strftime('%d/%m/%Y') if not pd.isnull(parsed) else ''
    except:
        return ''

def split_column(df, column, delimiter, parts):
    if delimiter == 'Date & Time Split (By Char)':
        char_df = df[column].astype(str).apply(lambda x: pd.Series(list(x)))
        df['Reconstructed_Date'] = char_df.apply(reconstruct_date, axis=1)

        # Optional: Extract time if needed (keeping original method)
        times = []
        for val in df[column].astype(str):
            parsed_time = pd.to_datetime(val, errors='coerce')
            times.append(parsed_time.strftime('%I:%M %p') if not pd.isnull(parsed_time) else '')
        df['Time'] = times

    else:
        split_data = df[column].astype(str).str.split(delimiter, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Streamlit UI
st.title("📊 Robust Excel Column Splitter (Safe for Date Glitches)")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 Preview:")
    st.dataframe(df.head())

    column = st.selectbox("🔍 Select a column", df.columns)

    split_option = st.selectbox(
        "🛠️ How do you want to split?",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Date & Time Split (By Char)"]
    )

    delimiter_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Date & Time Split (By Char)": "CHAR"
    }

    if split_option != "Date & Time Split (By Char)":
        num_parts = st.slider("How many parts?", 2, 4, 2)

    if st.button("✅ Split Now"):
        if split_option == "Date & Time Split (By Char)":
            df = split_column(df, column, "CHAR", 2)
        else:
            df = split_column(df, column, delimiter_map[split_option], num_parts)

        st.success("Done!")
        st.dataframe(df.head())

        df.to_excel("split_output.xlsx", index=False)
        with open("split_output.xlsx", "rb") as f:
            st.download_button("📥 Download Result", f, "split_output.xlsx")
