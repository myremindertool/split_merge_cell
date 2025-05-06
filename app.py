
import streamlit as st
import pandas as pd

def split_column(df, column, delimiter, parts):
    if delimiter == 'Date & Time Split':
        df['Date'] = pd.to_datetime(df[column], errors='coerce').dt.date
        df['Time'] = pd.to_datetime(df[column], errors='coerce').dt.time
    else:
        split_data = df[column].astype(str).str.split(delimiter, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

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

        # Download option
        output_file = "split_output.xlsx"
        df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button("📥 Download Result", f, file_name="split_output.xlsx")
