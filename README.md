# CleanSheet: Smart Data Cleaning Tool

Upload a messy CSV or Excel file and get a clean one in seconds.

## Features
- Standardizes column names
- Fixes inconsistent text (spaces, capitalization)
- Removes duplicate rows
- Converts mixed-format dates and text numbers
- Fills missing values (median or mean)
- Flags outliers with IQR + Isolation Forest (ML)
- Cleaning report + cleaned file download

## Run
pip install -r requirements.txt
streamlit run app.py

## Tech Stack
Python | Pandas | Scikit-learn | Streamlit