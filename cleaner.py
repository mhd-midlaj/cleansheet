import pandas as pd   # data handling
from sklearn.ensemble import IsolationForest   # ML model for outlier detection

def load_file(path):
    # Read CSV or Excel depending on file extension
    if path.endswith(".csv"):
        return pd.read_csv(path, encoding="latin-1")
    elif path.endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    else:
        raise ValueError("Only CSV and Excel files supported")

def clean_column_names(df):
    # strip spaces at ends -> lowercase -> turn inner spaces into underscore
    df.columns = (df.columns.str.strip()
                            .str.lower()
                            .str.replace(r"\s+", "_", regex=True))
    return df

def clean_text(df):
    for col in df.columns:                       # check every column
        if pd.api.types.is_string_dtype(df[col]):    # only touch text columns
            df[col] = (df[col].str.strip()                        # remove edge spaces
                              .str.replace(r"\s+", " ", regex=True)  # many spaces -> one
                              .str.title())                       # "CALICUT" -> "Calicut"
    return df
def remove_duplicates(df):
    before = len(df)                  # row count before
    df = df.drop_duplicates()         # drop rows that are fully identical
    print(f"Removed {before - len(df)} duplicate rows")
    return df

def missing_report(df):
    # count missing values per column, show only columns that have some
    missing = df.isnull().sum()
    return missing[missing > 0]

def fill_missing(df, number_strategy="median"):
    for col in df.columns:                              # check every column
        if df[col].isnull().sum() == 0:                 # nothing missing here
            continue                                    # skip to next column
        if "date" in col:                               # dates are fixed on Day 4
            continue                                    # leave them for now
        if pd.api.types.is_numeric_dtype(df[col]):      # number column
            if number_strategy == "mean":
                df[col] = df[col].fillna(df[col].mean())      # fill with average
            else:
                df[col] = df[col].fillna(df[col].median())    # fill with middle value
        else:                                           # text column
            df[col] = df[col].fillna("Unknown")         # fill with "Unknown"
    return df

def convert_dates(df):
    for col in df.columns:                          # check every column
        if "date" in col:                           # only columns with "date" in the name
            # pass 1: read ONLY rows in YYYY-MM-DD format, everything else becomes NaT
            iso = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
            # pass 2: read the remaining rows as DD/MM/YYYY (day first)
            other = pd.to_datetime(df[col], format="mixed",
                                   dayfirst=True, errors="coerce")
            # use pass 1 result where it worked, otherwise use pass 2
            df[col] = iso.fillna(other)
    return df

def convert_numbers(df):
    for col in df.columns:                          # check every column
        if "date" in col:                           # skip date columns
            continue
        if pd.api.types.is_string_dtype(df[col]):   # only text columns
            cleaned = df[col].str.replace(r"[₹$,]", "", regex=True)   # remove currency symbols and commas
            converted = pd.to_numeric(cleaned, errors="coerce")       # try converting to numbers
            filled = df[col].notna().sum()                            # how many real values exist
            # convert only if at least 80% of the values became numbers
            if filled > 0 and converted.notna().sum() >= 0.8 * filled:
                df[col] = converted
    return df

def detect_outliers_iqr(df, col):
    q1 = df[col].quantile(0.25)          # value below which 25% of data falls
    q3 = df[col].quantile(0.75)          # value below which 75% of data falls
    iqr = q3 - q1                        # spread of the middle 50%
    low = q1 - 1.5 * iqr                 # lower limit
    high = q3 + 1.5 * iqr                # upper limit
    return (df[col] < low) | (df[col] > high)   # True where value is outside limits

def detect_outliers_ml(df, col, contamination=0.2):
    model = IsolationForest(contamination=contamination,   # expected share of outliers (set by user)
                            random_state=42)               # same result every run
    labels = model.fit_predict(df[[col]])                  # -1 = outlier, 1 = normal
    return labels == -1                                    # True where model says outlier

def clean_all(df, number_strategy="median", contamination=0.2):
    df = clean_column_names(df)                 # fix column names
    df = clean_text(df)                         # fix text
    df = remove_duplicates(df)                  # remove duplicates
    df = convert_dates(df)                      # text -> real dates
    df = convert_numbers(df)                    # text -> real numbers
    df = fill_missing(df, number_strategy)      # fill missing values
    # flag outliers in every numeric column (flag only, never delete)
    for col in df.select_dtypes(include="number").columns:
        df[f"{col}_outlier_iqr"] = detect_outliers_iqr(df, col)
        df[f"{col}_outlier_ml"] = detect_outliers_ml(df, col, contamination)
    return df

if __name__ == "__main__":                      # runs ONLY when you run cleaner.py directly
    df = load_file("messy_data.csv")            # test file
    df = clean_all(df)                          # run the full cleaning pipeline
    print(df)