import pandas as pd   # data handling
import numpy as np    # for creating missing values (NaN)
# Create a small dataset with deliberate problems
data = {
    "Customer  Name": ["Ravi Kumar", "ravi kumar ", "Anu Mathew", "Anu Mathew",
                       "Sreejith", None, "Fathima", "Joseph  T"],   # extra spaces, case, duplicate, missing
    "ORDER Date": ["15/04/2024", "15/04/2024", "20/04/2024", "20/04/2024",
                   "2024-05-01", "03/05/2024", None, "10/05/2024"],  # mixed formats
    "Sales ": ["1200", "1200", "850", "850", "999999", "430", None, "760"],  # text numbers, outlier, missing
    "City": ["Thrissur", "thrissur", "Kochi", "Kochi",
             "CALICUT", "Kochi", "Calicut", "thrissur"],  # inconsistent case
}

df = pd.DataFrame(data)                  # convert dictionary to table
df.to_csv("messy_data.csv", index=False)       # save as CSV
df.to_excel("messy_data.xlsx", index=False)    # save as Excel (needs openpyxl)
print("Messy files created!")