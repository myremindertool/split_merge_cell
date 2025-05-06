import streamlit as st
import pandas as pd
import io

# Extract date parts from various formats
def extract_date_parts(val):
    val = str(val).strip().split(' ')[0].replace('-', '/')
    parts = val.split('/')
    if len(parts) == 3:
        if len(parts[0]) == 4:
            # Format: YYYY/MM/DD
            year, month, day = parts
        else:
            # Format: DD/MM/YYYY
            day, month, year = parts
        if all(x.isdigit() for x in [day, month, year]):
            return int(year), int(month), int(day)
    return None, None, None

# Manual cleaner — outputs "dd/mm/yyyy" as string for preview
def clean_date_as_preview(val):
    y, m, d = extract_date_parts(val)
    if y and m and d:
        return f"{str(d).zfill(2)}/{str(m).zfill(2)}/{str(y)}"
    return ""

# Split logic (normal or special)
def split_column(df, column, method, parts):
    if method == 'Excel-Safe Date':
        df['Date'] = df[column].apply(clean_date_as_preview)
        df['Time'] = df[column].astype(str).apply(lambda x: x.split(' ')[1] if ' ' in x and ':' in x else '')
    else:
        split_data = df[column].astype(str).str.split(method, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Write Excel using =TEXT(DATE(...)) formula to avoid datetime formatting
def write_excel_with_safe_formula(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']
        date_col_index = df.columns.get_loc('Date')

        for row_idx, val in enumerate(df['Date'], start=1):
            y, m, d = extract_date_parts(val)
            if y and m and d:
                formula = f'=TEXT(DATE({y},{m},{d}),"dd/mm/yyyy")'
                worksheet.write_formula(row_idx, date_col_index, formula)
            else:
                worksheet.write(row_idx, date_col_index, '')

        writer.save()
        return output.getvalue()

# Streamlit UI
st.title("📅 Excel-Safe Date Splitter (No 00:00:00 Bug)")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 File Preview:")
    st.dataframe(df.head())

    column = st.selectbox("🧩 Choose a column to process", df.columns)

    method = st.selectbox(
        "⚙️ Choose processing method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Excel-Safe Date"]
    )

    method_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Excel-Safe Date": "safe"
    }

    if method != "Excel-Safe Date":
        num_parts = st.slider("🔢 How many parts to split into?", 2, 4, 2)

    if st.button("🚀 Process Now"):
        if method == "Excel-Safe Date":
            df = split_column(df, column, "safe", 2)
        else:
            df = split_column(df, column, method_map[method], num_parts)

        st.success("✅ Processing complete!")
        st.dataframe(df.head())

        # Download with Excel-safe formula
        processed_data = write_excel_with_safe_formula(df)
        st.download_button(
            label="📥 Download Final Excel (Text Format Date)",
            data=processed_data,
            file_name="safe_date_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
