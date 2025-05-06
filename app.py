import streamlit as st
import pandas as pd
import io

# Smart parser that splits into date + optional time
def clean_and_split_datetime(val):
    val = str(val).strip()
    dt = pd.to_datetime(val, errors='coerce')
    if pd.isnull(dt):
        return val, ""
    # Keep original format or use DD-MM-YYYY
    date_out = dt.strftime("%d-%m-%Y")
    time_out = dt.strftime("%H:%M:%S") if dt.time() != pd.Timestamp(0).time() else ""
    return date_out, time_out

# Apply logic
def split_column(df, column, method, parts):
    if method == 'Split Date and Time':
        df['DOJ_Part1'], df['DOJ_Part2'] = zip(*df[column].apply(clean_and_split_datetime))
    else:
        split_data = df[column].astype(str).str.split(method, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Write file with openpyxl
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.read()

# Streamlit App
st.title("📅 Date & Time Splitter (Excel-Safe)")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Choose column to split", df.columns)

    method = st.selectbox(
        "⚙️ Choose split method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Split Date and Time"]
    )

    method_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Split Date and Time": "smart"
    }

    if method != "Split Date and Time":
        num_parts = st.slider("🔢 Number of parts", 2, 4, 2)

    if st.button("🚀 Run Split"):
        if method == "Split Date and Time":
            df = split_column(df, column, "smart", 2)
        else:
            df = split_column(df, column, method_map[method], num_parts)

        st.success("✅ Done!")
        st.dataframe(df.head())

        final_excel = write_excel(df)

        st.download_button(
            label="📥 Download Clean Excel",
            data=final_excel,
            file_name="split_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
