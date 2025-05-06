import streamlit as st
import pandas as pd
import io

# Clean and split datetime into two columns (Date & Time)
def clean_and_split_datetime(val):
    try:
        dt = pd.to_datetime(val, errors='coerce')
        if pd.isnull(dt):
            return "", ""
        date_str = dt.strftime("%d/%m/%Y")
        time_str = dt.strftime("%H:%M:%S") if dt.time() != pd.Timestamp(0).time() else ""
        return date_str, time_str
    except Exception:
        return "", ""

# Apply split to column
def split_column(df, column, method, parts):
    if method == 'Date + Time Split (Text Format)':
        df['DOJ_Part1'], df['DOJ_Part2'] = zip(*df[column].apply(clean_and_split_datetime))
    else:
        split_data = df[column].astype(str).str.split(method, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Save as clean Excel (no formulas)
def write_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.read()

# Streamlit UI
st.title("🧼 Clean Date & Time Splitter (No 00:00:00 Excel Bug)")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("🧩 Choose a column to split", df.columns)

    method = st.selectbox(
        "⚙️ Choose split method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Date + Time Split (Text Format)"]
    )

    method_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Date + Time Split (Text Format)": "datetime"
    }

    if method != "Date + Time Split (Text Format)":
        num_parts = st.slider("🔢 Number of parts", 2, 4, 2)

    if st.button("🚀 Process Now"):
        if method == "Date + Time Split (Text Format)":
            df = split_column(df, column, "datetime", 2)
        else:
            df = split_column(df, column, method_map[method], num_parts)

        st.success("✅ Split Completed!")
        st.dataframe(df.head())

        final_excel = write_excel(df)

        st.download_button(
            label="📥 Download Clean Excel",
            data=final_excel,
            file_name="clean_split_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
