"""
import_inventory.py

Purpose:
Read the inventory spreadsheet and inspect its columns
before importing data into SQLite.
"""

# Import modules needed for program operation

# Module for reading excel spreadsheets
import pandas as pd
# Module for handling file paths and directories
from pathlib import Path
# Module to work with SQLite
import sqlite3
# Module for working with datetime format
from datetime import datetime

# Establishes the root path for the file tree
root_path = Path(__file__).resolve().parents[2]

# Establishes the location for the excel file
inventory_file = root_path / "data" / "demo" / "Mock-Inventory.xlsx"

# Establishes the location for database file
database_file = root_path / "database" / "inventory.db"

# Function to read spreadsheet file 
def inspect_inventory_file(file_path):
    try:
        # 
        inventory_data = pd.read_excel(file_path, header=1)

        print(f"Inventory file loaded successfully: {file_path.name}")
        # Rename the spreadsheet column names to Python friendly names
        inventory_data = inventory_data.rename(columns={
            "Item No.": "item_no",
            "Description": "description",
            "Qty On Hand": "qty_on_hand",
            "Avg Cost": "avg_cost",
            "Base Price": "base_price",
            "Gross M": "gross_margin_dollars",
            "Gross M %": "gross_margin_percent"
        })

        print("\nCleaned columns:")
        for column in inventory_data.columns:
            print(f"- {column}")

        print("\nFirst 5 rows:")
        print(inventory_data.head())

        return inventory_data

    except FileNotFoundError:
        print(f"File not found: {file_path}")

    except Exception as error:
        print(f"Error reading inventory file: {error}")
        raise

def clean_inventory_data(inventory_data):
    inventory_data = inventory_data.dropna(how="all")

    inventory_data = inventory_data[[
        "item_no",
        "description",
        "qty_on_hand",
        "avg_cost",
        "base_price",
        "gross_margin_dollars",
        "gross_margin_percent"
    ]]

    inventory_data["item_no"] = inventory_data["item_no"].astype("Int64")
    inventory_data["qty_on_hand"] = inventory_data["qty_on_hand"].astype("Int64")

    return inventory_data

def create_connection():
    try:
        connection = sqlite3.connect(database_file)
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    except sqlite3.Error as error:
        print(f"Database connection error: {error}")
        raise

def create_import_batch(connection, file_name, import_type):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO ImportBatch (
            ImportDate,
            FileName,
            ImportType,
            Status
        )
        VALUES (?, ?, ?, ?);
    """, (
        datetime.now().isoformat(),
        file_name,
        import_type,
        "Success"
    ))

    return cursor.lastrowid

def insert_products(connection, inventory_data):
    cursor = connection.cursor()

    products_inserted = 0

    for _, row in inventory_data.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO Product (
                SKU,
                ProductName
            )
            VALUES (?, ?);
        """, (
            int(row["item_no"]),
            row["description"]
        ))

        if cursor.rowcount > 0:
            products_inserted += 1

    return products_inserted

def show_product_count(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Product;
    """)

    product_count = cursor.fetchone()[0]

    print(f"Total products in database: {product_count}")


def main():
    inventory_data = inspect_inventory_file(inventory_file)

    cleaned_inventory_data = clean_inventory_data(inventory_data)

    print("\nCleaned inventory data:")
    print(cleaned_inventory_data.head())

    connection = create_connection()

    import_batch_id = create_import_batch(
        connection,
        inventory_file.name,
        "Inventory"
    )

    products_inserted = insert_products(connection, cleaned_inventory_data)

    connection.commit()

    print(f"\nImport batch created successfully with ID: {import_batch_id}")
    print(f"Products inserted successfully: {products_inserted}")

    show_product_count(connection)

    connection.close()

if __name__ == "__main__":
    main()