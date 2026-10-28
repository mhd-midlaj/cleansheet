import streamlit as st          # web app library
import pandas as pd             # data handling
from cleaner import clean_all   # reuse our cleaning pipeline

# Browser tab title, icon and full-width layout
st.set_page_config(page_title="CleanSheet", page_icon="🧹", layout="wide")

st.title("🧹 CleanSheet — Smart Data Cleaning Tool")      # main title
st.write("Upload a messy CSV or Excel file and get a clean one in seconds")

# Sidebar settings the user can change
st.sidebar.header("Settings")
strategy = st.sidebar.selectbox("Fill missing numbers with", ["median", "mean"])   # fill method
contamination = st.sidebar.slider("Outlier sensitivity", 0.01, 0.5, 0.1, 0.01)     # ML setting

# File upload button (CSV or Excel)
uploaded = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded is not None:                                   # run only after a file is uploaded
    if uploaded.name.endswith(".csv"):                     # CSV file
        raw = pd.read_csv(uploaded, encoding="latin-1")
    else:                                                  # Excel file
        raw = pd.read_excel(uploaded)

    cleaned = clean_all(raw.copy(), strategy, contamination)   # clean a COPY so the original stays untouched
    # show dates as YYYY-MM-DD without the fake 00:00:00 time

    for col in cleaned.select_dtypes(include="datetime").columns:
        cleaned[col] = cleaned[col].dt.strftime("%Y-%m-%d")

    # ---- build the cleaning report ----
    flag_cols = [c for c in cleaned.columns if "_outlier_" in c]          # outlier flag columns
    data_cols = [c for c in cleaned.columns if c not in flag_cols]        # real data columns
    missing_before = int(raw.isnull().sum().sum())                        # missing values in original
    missing_after = int(cleaned[data_cols].isnull().sum().sum())          # still missing after cleaning
    outlier_rows = int(cleaned[flag_cols].any(axis=1).sum()) if flag_cols else 0   # rows with any flag

    st.subheader("📋 Cleaning Report")
    st.write(f"- ✅ Column names standardized: **{len(raw.columns)}** columns")
    st.write(f"- ✅ Duplicate rows removed: **{len(raw) - len(cleaned)}**")
    st.write(f"- ✅ Missing values filled: **{missing_before - missing_after}**")
    st.write(f"- ⚠️ Missing values left for review (dates): **{missing_after}**")
    st.write(f"- ⚠️ Rows flagged as suspicious outliers: **{outlier_rows}**")

    # Summary numbers
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows before", len(raw))
    c2.metric("Rows after", len(cleaned))
    c3.metric("Duplicates removed", len(raw) - len(cleaned))

        # Before and after side by side
    left, right = st.columns(2)
    with left:
            st.subheader("Before")
            st.dataframe(raw)
    with right:
            st.subheader("After")
            st.dataframe(cleaned)

        # Show rows that contain at least one outlier flag
    if flag_cols:
            suspicious = cleaned[cleaned[flag_cols].any(axis=1)]           # rows with any True flag
            st.subheader("⚠️ Suspicious values (please review)")
            if len(suspicious) > 0:
                st.dataframe(suspicious)
            else:
                st.success("No outliers found")

        # Download the cleaned file
    csv = cleaned.to_csv(index=False).encode("utf-8")      # convert table to downloadable bytes
    st.download_button("📥 Download Cleaned CSV", csv, "cleaned_data.csv", "text/csv")