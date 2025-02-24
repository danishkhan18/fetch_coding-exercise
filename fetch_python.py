import pandas as pd
import json
import re

# Function to load JSON data and handle potential issues
def load_json(file_path):
    with open(file_path, 'r') as file:
        try:
            # Attempt to load as a single JSON object
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Couldn't load {file_path} as a single JSON object: {e}")
            # Fallback: handle multiple JSON objects (line by line)
            file.seek(0)
            data = []
            for idx, line in enumerate(file, start=1):
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {idx} in {file_path}: {e}")
    if not data:
        print(f"Warning: No valid JSON data found in {file_path}")
    return pd.json_normalize(data)

# Load datasets
brands_df = load_json('brands.json')
receipts_df = load_json('receipts.json')
users_df = load_json('users.json')

# Check for missing values in DataFrame
def check_missing_values(df, df_name):
    print(f"\nChecking for missing values in {df_name}:")
    missing = df.isnull().sum()
    print(missing)
    total_missing = missing.sum()
    print(f"Total missing values in {df_name}: {total_missing}")

# Find duplicate rows in DataFrame
def check_duplicates(df, df_name):
    df_copy = df.copy()
    # Convert lists/dicts to strings for hashing
    for col in df_copy.columns:
        if df_copy[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df_copy[col] = df_copy[col].astype(str)
    duplicates = df_copy.duplicated().sum()
    print(f"\nDuplicate records found in {df_name}: {duplicates}")

# Display data types of each column
def check_data_types(df, df_name):
    print(f"\nData types in {df_name}:")
    print(df.dtypes)

# Check for invalid foreign key references
def check_invalid_references(receipts_df, users_df, brands_df):
    print("\nChecking foreign key references...")
    print("Available columns in users_df:", users_df.columns.tolist())

    # Handle user IDs
    user_id_col = '_id.$oid' if '_id.$oid' in users_df.columns else '_id'
    invalid_users = receipts_df[~receipts_df['userId'].isin(users_df[user_id_col])]
    print(f"Invalid user references in receipts: {len(invalid_users)}")

    # Handle barcodes
    receipt_items = pd.json_normalize(receipts_df['rewardsReceiptItemList'].explode())
    invalid_barcodes = receipt_items[~receipt_items['barcode'].isin(brands_df['barcode'])]
    print(f"Invalid barcode references in receipt items: {len(invalid_barcodes)}")

# Detect outliers in numeric columns
def check_outliers(df, df_name, numeric_columns):
    print(f"\nOutlier detection in {df_name}:")
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].dropna().empty:
                print(f"{col}: No valid numeric data found.")
                continue

            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
            print(f"{col}: {len(outliers)} outliers detected")

# Identify invalid formats using regex
def check_invalid_formats(df, df_name, column, pattern, format_name):
    print(f"\nChecking for invalid {format_name} formats in {df_name}:")
    invalid = df[~df[column].astype(str).str.match(pattern, na=False)]
    print(f"{len(invalid)} invalid {format_name} entries found.")

# Check for inconsistent categorical values
def check_inconsistent_categories(df, df_name, column):
    print(f"\nUnique values in '{column}' of {df_name}:")
    print(df[column].unique())

# ----- Running Data Quality Checks ----- #

# Missing values
check_missing_values(brands_df, 'Brands')
check_missing_values(receipts_df, 'Receipts')
check_missing_values(users_df, 'Users')

# Duplicates
check_duplicates(brands_df, 'Brands')
check_duplicates(receipts_df, 'Receipts')
check_duplicates(users_df, 'Users')

# Data types
check_data_types(brands_df, 'Brands')
check_data_types(receipts_df, 'Receipts')
check_data_types(users_df, 'Users')

# Invalid references
check_invalid_references(receipts_df, users_df, brands_df)

# Outlier detection
check_outliers(receipts_df, 'Receipts', ['totalSpent', 'bonusPointsEarned', 'pointsEarned'])
check_outliers(pd.json_normalize(receipts_df['rewardsReceiptItemList'].explode()), 'Receipt Items', ['finalPrice', 'itemPrice', 'quantityPurchased'])

# Invalid email formats (if column exists)
if 'email' in users_df.columns:
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    check_invalid_formats(users_df, 'Users', 'email', email_pattern, 'email')

# Inconsistent categorical values
check_inconsistent_categories(users_df, 'Users', 'state')
check_inconsistent_categories(receipts_df, 'Receipts', 'rewardsReceiptStatus')

print("\nData quality checks completed successfully!")







'''
OUTPUT: 

Couldn't load brands.json as a single JSON object: Extra data: line 2 column 1 (char 229)
Couldn't load receipts.json as a single JSON object: Extra data: line 2 column 1 (char 871)
Couldn't load users.json as a single JSON object: Extra data: line 2 column 1 (char 186)

Checking for missing values in Brands:
barcode           0
category        155
categoryCode    650
name              0
topBrand        612
_id.$oid          0
cpg.$id.$oid      0
cpg.$ref          0
brandCode       234
dtype: int64

Total missing values in Brands: 1651

Checking for missing values in Receipts:
bonusPointsEarned          575
bonusPointsEarnedReason    575
pointsEarned               510
purchasedItemCount         484
rewardsReceiptItemList     440
rewardsReceiptStatus         0
totalSpent                 435
userId                       0
_id.$oid                     0
createDate.$date             0
dateScanned.$date            0
finishedDate.$date         551
modifyDate.$date             0
pointsAwardedDate.$date    582
purchaseDate.$date         448
dtype: int64

Total missing values in Receipts: 4600

Checking for missing values in Users:
active                0
role                  0
signUpSource         48
state                56
_id.$oid              0
createdDate.$date     0
lastLogin.$date      62
dtype: int64
Total missing values in Users: 166
Duplicate records found in Brands: 0
Duplicate records found in Receipts: 0
Duplicate records found in Users: 283
Data types in Brands:
barcode         object
category        object
categoryCode    object
name            object
topBrand        object
_id.$oid        object
cpg.$id.$oid    object
cpg.$ref        object
brandCode       object
dtype: object

Data types in Receipts:
bonusPointsEarned          float64
bonusPointsEarnedReason     object
pointsEarned                object
purchasedItemCount         float64
rewardsReceiptItemList      object
rewardsReceiptStatus        object
totalSpent                  object
userId                      object
_id.$oid                    object
createDate.$date             int64
dateScanned.$date            int64
finishedDate.$date         float64
modifyDate.$date             int64
pointsAwardedDate.$date    float64
purchaseDate.$date         float64
dtype: object

Data types in Users:
active                  bool
role                  object
signUpSource          object
state                 object
_id.$oid              object
createdDate.$date      int64
lastLogin.$date      float64
dtype: object

Checking foreign key references...

Available columns in users_df: ['active', 'role', 'signUpSource', 'state', '_id.$oid', 'createdDate.$date', 'lastLogin.$date']
Invalid user references in receipts: 148
Invalid barcode references in receipt items: 7299

Outlier detection in Receipts:
totalSpent: 55 outliers detected
bonusPointsEarned: 0 outliers detected
pointsEarned: 36 outliers detected

Outlier detection in Receipt Items:
finalPrice: 476 outliers detected
itemPrice: 476 outliers detected
quantityPurchased: 1139 outliers detected

Unique values in 'state' of Users:
['WI' 'KY' 'AL' 'CO' 'IL' nan 'OH' 'SC' 'NH']

Unique values in 'rewardsReceiptStatus' of Receipts:
['FINISHED' 'REJECTED' 'FLAGGED' 'SUBMITTED' 'PENDING']

Data quality checks completed successfully!

'''