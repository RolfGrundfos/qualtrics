import pandas as pd

def fix_csv_with_proper_headers(input_file, output_file=None):
    """
    Fix Qualtrics CSV by using proper headers and skipping validation text
    """
    if not output_file:
        output_file = input_file.replace('.csv', '_fixed.csv')

    print(f"Fixing {input_file}...")

    try:
        # Read the first row which contains the proper technical headers
        headers_df = pd.read_csv(input_file, nrows=1)
        proper_headers = headers_df.columns.tolist()

        print(f"Found {len(proper_headers)} proper column headers")

        # Read the actual data starting from row 11 (0-indexed row 10)
        # Skip validation text and use proper headers
        df = pd.read_csv(input_file, skiprows=10, header=None, low_memory=False)

        # Assign proper headers
        if len(df.columns) == len(proper_headers):
            df.columns = proper_headers
        else:
            print(f"WARNING: Column count mismatch. Data has {len(df.columns)} columns, headers have {len(proper_headers)}")
            # Use available headers and fill missing ones
            df.columns = proper_headers[:len(df.columns)] + [f"Extra_Col_{i}" for i in range(len(proper_headers), len(df.columns))]

        # Remove any rows that might still contain validation text or import config
        validation_patterns = [
            'Please confirm this is correct',
            'You have logged in as',
            'Is this correct?',
            'ImportId',
            'startDate',
            'endDate',
            'timeZone'
        ]

        # Filter out rows containing validation text in any column
        initial_rows = len(df)
        for pattern in validation_patterns:
            mask = df.astype(str).apply(lambda x: x.str.contains(pattern, case=False, na=False)).any(axis=1)
            df = df[~mask]

        print(f"Removed {initial_rows - len(df)} rows containing validation/config text")

        # Save fixed CSV
        df.to_csv(output_file, index=False)

        print(f"SUCCESS: Fixed CSV saved as: {output_file}")
        print(f"   Final file has {len(df)} responses with {len(df.columns)} columns")

        # Show first few column names to verify
        print(f"   Sample columns: {proper_headers[:5]}...")

        return output_file

    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    fixed_file = fix_csv_with_proper_headers("EMS_survey_responses.csv")

    if fixed_file:
        print(f"\nSUCCESS: EMS survey data has been fixed!")
        print(f"Use the fixed file: {fixed_file}")

        # Quick verification
        try:
            test_df = pd.read_csv(fixed_file, nrows=5)
            print(f"\nVerification - First 5 rows loaded successfully")
            print(f"Columns include: {list(test_df.columns[:10])}")
        except Exception as e:
            print(f"Verification failed: {e}")