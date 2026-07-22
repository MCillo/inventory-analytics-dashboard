"""
import_sales.py

Purpose:
Read the sales history spreadsheet and inspect its columns
before importing data into SQLite.
"""

import pandas as pd
from pathlib import Path
import sqlite3
from datetime import datetime
import re

# Establish root path for file tree
root_path = Path(__file__).resolve().parents[2]
# Establish location for the files to import
sales_files = [
    root_path / "data" / "demo" / "sales_reports" / "SalesByItem1.xls",
    root_path / "data" / "demo" / "sales_reports" / "SalesByItem2.xls",
    root_path / "data" / "demo" / "sales_reports" / "SalesByItem3.xls",
    root_path / "data" / "demo" / "sales_reports" / "SalesByItem4.xls",
]
#sales_file = root_path / "data" / "demo" / "sales_reports" / "SalesByItem1.xls"

# Establish location of database
database_file = root_path / "database" / "inventory.db"

# Function to read the spreadsheet and prepare the data for the database
def inspect_sales_file(file_path):
    try:
        # Read data from spreadsheet and use Excel row 4 as column headers
        sales_data = pd.read_excel(file_path, header=3, engine="xlrd")

        print(f"Sales file loaded successfully: {file_path.name}")

        sales_data = sales_data.rename(columns={
            "Description": "description",
            "Item No.": "item_no",
            "Qty Sold": "qty_sold"
        })

        sales_data = sales_data[[
            "description",
            "item_no",
            "qty_sold"
        ]]

        print("\nCleaned columns:")
        for column in sales_data.columns:
            print(f"- {column}")

        print("\nFirst 5 rows:")
        print(sales_data.head())

        return sales_data

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise

    except Exception as error:
        print(f"Error reading sales file: {error}")
        raise

# Function to get the sales history start and end date from the spreadsheet
def get_sales_period(file_path):
    # Read the spreadsheet without treating any row as headers
    raw_data = pd.read_excel(file_path, header=None, engine="xlrd")

    # Cell B3 = row index 2, column index 1
    valuation_text = str(raw_data.iloc[2, 1])

    date_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})"

    dates_found = re.findall(date_pattern, valuation_text)

    if len(dates_found) >= 2:
        period_start_date = dates_found[0]
        period_end_date = dates_found[1]

        return period_start_date, period_end_date

    raise ValueError(f"Could not find start and end dates in: {valuation_text}")

# Function to clean up the data read from the spreadsheet to work better with the database
def clean_sales_data(sales_data):
    sales_data = sales_data.dropna(how="all")

    sales_data = sales_data[[
        "description",
        "item_no",
        "qty_sold"
    ]]

    sales_data = sales_data.dropna(subset=["item_no", "qty_sold"])

    sales_data = sales_data[
        ~sales_data["description"].astype(str).str.startswith("XX")
    ]

    sales_data["item_no"] = sales_data["item_no"].astype("Int64")
    sales_data["qty_sold"] = sales_data["qty_sold"].astype("Int64")

    sales_data = sales_data[sales_data["qty_sold"] != 0]

    return sales_data

# Function to create a connection to the database
def create_connection():
    try:
        connection = sqlite3.connect(database_file)
        connection.execute("Pragma foreign_keys = ON;")
        return connection
    except sqlite3.Error as error:
        print(f"Database connection error: {error}")
        raise

# Function to create an Import Batch
def create_import_batch(connection, file_name, import_type, report_date):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO ImportBatch (
            ImportDate,
            ReportDate,
            FileName,
            ImportType,
            Status
        )
        VALUES (?, ?, ?, ?, ?);
    """, (
        datetime.now().isoformat(),
        report_date,
        file_name,
        import_type,
        "Success"
    ))

    return cursor.lastrowid

# Function to show count for import batch
def show_import_batch_count(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM ImportBatch;
    """)

    import_batch_count = cursor.fetchone()[0]

    print(f"Total import batches in database: {import_batch_count}")

# Function to match product_id to SKU
def get_product_id_by_sku(connection, sku):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT ProductId
        FROM Product
        WHERE SKU = ?;
    """, (
        int(sku),
    ))

    result = cursor.fetchone()

    if result:
        return result[0]

    return None

# Function to insert sales history into database
def insert_sales_history(connection, sales_data, import_batch_id, period_start_date, period_end_date):
    cursor = connection.cursor()

    sales_inserted = 0

    for row in sales_data.itertuples(index=False):
        sku = row.item_no
        units_sold = row.qty_sold

        product_id = get_product_id_by_sku(connection, sku)

        if product_id:
            cursor.execute("""
                INSERT INTO SalesHistory (
                    UnitsSold,
                    PeriodStartDate,
                    PeriodEndDate,
                    ImportBatchId,
                    ProductId
                )
                VALUES (?, ?, ?, ?, ?);
            """, (
                int(units_sold),
                period_start_date,
                period_end_date,
                import_batch_id,
                product_id
            ))

            sales_inserted += 1

        else:
            print(f"No product was found for SKU: {sku}")

    return sales_inserted

# Function to show a sales history count
def show_sales_history_count(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM SalesHistory;
    """)

    sales_history_count = cursor.fetchone()[0]

    print(f"Total sales history records in database: {sales_history_count}")

def main():
    connection = create_connection()

    try:
        for sales_file in sales_files:
            print("\n" + "=" * 80)
            print(f"Starting import for: {sales_file.name}")
            print("=" * 80)

            sales_data = inspect_sales_file(sales_file)

            cleaned_sales_data = clean_sales_data(sales_data)

            returns = cleaned_sales_data[
                cleaned_sales_data["qty_sold"] < 0
            ]

            if returns.empty:
                print("\nReturned items found: None")
            else:
                print("\nReturned items found:")
                print(returns)

            duplicate_skus = cleaned_sales_data[
                cleaned_sales_data.duplicated(
                    subset=["item_no"],
                    keep=False
                )
            ]

            if duplicate_skus.empty:
                print("\nDuplicate SKUs found: None")
            else:
                print("\nDuplicate SKUs found:")
                print(duplicate_skus)

            # Get this file's sales period
            period_start_date, period_end_date = get_sales_period(
                sales_file
            )

            print(f"Sales period start: {period_start_date}")
            print(f"Sales period end: {period_end_date}")

            # Create a separate import batch for this file
            import_batch_id = create_import_batch(
                connection,
                sales_file.name,
                "SalesHistory",
                period_end_date
            )

            sales_inserted = insert_sales_history(
                connection,
                cleaned_sales_data,
                import_batch_id,
                period_start_date,
                period_end_date
            )

            connection.commit()

            print(f"\nImport completed for: {sales_file.name}")
            print(
                f"Import Batch created successfully with ID: "
                f"{import_batch_id}"
            )
            print(
                f"Sales history records inserted: {sales_inserted}"
            )

        print("\n" + "=" * 80)
        print("Final Database Counts")
        print("=" * 80)

        show_import_batch_count(connection)
        show_sales_history_count(connection)

    except Exception as error:
        connection.rollback()
        print(f"\nSales import failed: {error}")
        raise

    finally:
        connection.close()

if __name__ == "__main__":
    main()