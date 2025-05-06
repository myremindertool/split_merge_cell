import streamlit as st
import pandas as pd

# Rebuild date string from individual characters
def rebuild_date_from_chars(series):
    result = []
    for val in series.astype(str):
        chars = list(val.strip())
        raw = ''.join(chars).replace('-', '/').replace(' ', '')  # unify separators
        try:
            parsed = pd.to_datetime(raw, dayfirst=True, errors='coerce')
            result.append("'" + parsed.strftime('%d/%m/%Y') if not pd.isnull(parsed) else '')
        except:
            result.append('')
    return result

# Split column based on delimiter or character-based rebuild
def split_column(df, column, delimiter, parts):
    if delimiter == 'Split by Character Rebuild':
        # Rebuild date from char list
        df['Date'] = rebuild_date_from_chars(df[column])

        # Optional: Extract time
        df['Time'] = pd.to_datetime(df[column], errors='coerce').dt.strftime('%I:%M %p')
    else:
        split_data = df[column].astype(str).str.split(delimiter, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Streamlit Interface
st.title("📊 Excel Column Splitter with Clean Date Output")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("🧩 Select the column to split", df.columns)

    split_option = st.selectbox(
        "🧰 Choose split method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Split by Character Rebuild"]
    )

    delimiter_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Split by Character Rebuild": "char"
    }

    if split_option != "Split by Character Rebuild":
        num_parts = st.slider("🔢 Number of parts to split into", 2, 4, value=2)

    if st.button("🚀 Split Now"):
        if split_option == "Split by Character Rebuild":
            df = split_column(df, column, "char", 2)
        else:
            df = split_column(df, column, delimiter_map[split_option], num_parts)

        st.success("✅ Column split successfully!")
        st.dataframe(df.head())

        # Export
        output_file = "split_output.xlsx"
        df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button("📥 Download Result", f, file_name="split_output.xlsx")
