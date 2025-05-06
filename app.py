import streamlit as st
import pandas as pd
import io

# Manual cleaning: parse only the date part and format as DD/MM/YYYY (but NOT datetime)
def clean_date_as_text(val):
    val = str(val).strip().split(" ")[0]  # Remove time
    val = val.replace("-", "/")

    # Format: DD/MM/YYYY or YYYY/MM/DD
    parts = val.split("/")
    if len(parts) == 3:
        if len(parts[0]) == 4:
            year, month, day = parts
        else:
            day, month, year = parts
        if all(x.isdigit() for x in [day, month, year]):
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
    return ""

# Split logic
def split_column(df, column, method, parts):
    if method == 'Manual Date Formatter':
        df['Date'] = df[column].apply(clean_date_as_text)
        df['Time'] = df[column].astype(str).apply(lambda x: x.split(' ')[1] if ' ' in x and ':' in x else '')
    else:
        split_data = df[column].astype(str).str.split(method, n=parts-1, expand=True)
        for i in range(parts):
            df[f"{column}_Part{i+1}"] = split_data[i]
    return df

# Streamlit UI
st.title("📊 Excel Date Cleaner (No 00:00:00 Issue)")

uploaded_file = st.file_uploader("📁 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📋 Preview:")
    st.dataframe(df.head())

    column = st.selectbox("📌 Choose column", df.columns)

    method = st.selectbox(
        "⚙️ Split method",
        ["Space", "Comma", "Hyphen (-)", "Underscore (_)", "Manual Date Formatter"]
    )

    method_map = {
        "Space": " ",
        "Comma": ",",
        "Hyphen (-)": "-",
        "Underscore (_)": "_",
        "Manual Date Formatter": "manual"
    }

    if method != "Manual Date Formatter":
        num_parts = st.slider("🔢 Number of parts", 2, 4, 2)

    if st.button("🚀 Process"):
        if method == "Manual Date Formatter":
            df = split_column(df, column, "manual", 2)
        else:
            df = split_column(df, column, method_map[method], num_parts)

        st.success("✅ Split complete!")
        st.dataframe(df.head())

        # Export using Excel-safe formulas to preserve format
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']

            if 'Date' in df.columns:
                col_index = df.columns.get_loc('Date')
                for row_idx, val in enumerate(df['Date'], start=1):  # Skip header row
                    safe_val = val.replace("'", "")
                    worksheet.write_formula(row_idx, col_index, f'="{safe_val}"')

            writer.save()
            processed_data = output.getvalue()

        st.download_button(
            label="📥 Download Clean Excel",
            data=processed_data,
            file_name="final_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
