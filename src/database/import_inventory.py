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
        # Read data from Spreadsheet and use second row as column headers
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

        """
        print("\nCleaned columns:")
        for column in inventory_data.columns:
            print(f"- {column}")

        print("\nFirst 5 rows:")
        print(inventory_data.head())
        """

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

    inventory_data = inventory_data[
        ~inventory_data["description"].astype(str).str.startswith("XX")
    ]

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

def show_import_batch_count(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM ImportBatch;
    """)

    import_batch_count = cursor.fetchone()[0]

    print(f"Total import batches in database: {import_batch_count}")

def insert_products(connection, inventory_data):
    cursor = connection.cursor()

    products_inserted = 0

    for row in inventory_data.itertuples(index=False):
        cursor.execute("""
            INSERT OR IGNORE INTO Product (
                SKU,
                ProductName
            )
            VALUES (?, ?);
        """, (
            int(row.item_no),
            row.description
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

"""
Function to test lookup product may be used later for search by sku function
def test_product_lookup(connection):
    product_id = get_product_id_by_sku(connection, 216750)

    print(f"Product ID for SKU 216750: {product_id}")
"""

def insert_inventory_snapshots(connection, inventory_data, import_batch_id):
    cursor = connection.cursor()

    snapshots_inserted = 0

    for row in inventory_data.itertuples(index=False):
        sku = row.item_no
        quantity_on_hand = row.qty_on_hand

        product_id = get_product_id_by_sku(connection, sku)

        if product_id:
            cursor.execute("""
                INSERT INTO InventorySnapshot (
                    QuantityOnHand,
                    SnapshotDate,
                    ImportBatchId,
                    ProductId
                )
                VALUES (?, ?, ?, ?);
            """, (
                int(quantity_on_hand),
                datetime.now().isoformat(),
                import_batch_id,
                product_id
            ))

            snapshots_inserted += 1

        else:
            print(f"No product was found for SKU: {sku}")

    return snapshots_inserted

def show_inventory_snapshots_count(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM InventorySnapshot;
    """)

    inventory_snapshots_count = cursor.fetchone()[0]

    print(f"Total Inventory Snapshots in database: {inventory_snapshots_count}")

def insert_product_financials(connection, inventory_data, import_batch_id):

    cursor = connection.cursor()

    financials_inserted = 0

    for row in inventory_data.itertuples(index=False):

        sku = row.item_no
        product_id = get_product_id_by_sku(connection, sku)

        if product_id:
            cursor.execute("""
                INSERT INTO ProductFinancial (
                    EffectiveDate,
                    ProductId,
                    ImportBatchId,
                    RetailPrice,
                    CostPrice,
                    MarginPercent,
                    MarginDollars
                )
                VALUES (?,?,?,?,?,?,?);
            """, (
                datetime.now().isoformat(),
                product_id,
                import_batch_id,
                row.base_price,
                row.avg_cost,
                row.gross_margin_percent,
                row.gross_margin_dollars
            ))
           
            financials_inserted += 1

        else:
            print(f"No product was found for SKU: {sku} ")

    return financials_inserted

def show_product_financials_count(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM ProductFinancial;
    """)

    product_financials_count = cursor.fetchone()[0]

    print(f"Total Product Financials in database: {product_financials_count}")


def main():
    inventory_data = inspect_inventory_file(inventory_file)

    cleaned_inventory_data = clean_inventory_data(inventory_data)

    #print("\nCleaned inventory data:")
    #print(cleaned_inventory_data.head())

    duplicate_skus = cleaned_inventory_data[
        cleaned_inventory_data.duplicated(subset=["item_no"], keep=False)
    ]

    if duplicate_skus.empty:
        print("\nDuplicate SKUs found: None")
    else:
        print("\nDuplicate SKUs found:")
        print(duplicate_skus)

    connection = create_connection()

    import_batch_id = create_import_batch(
        connection,
        inventory_file.name,
        "Inventory"
    )

    products_inserted = insert_products(connection, cleaned_inventory_data)

    snapshots_inserted = insert_inventory_snapshots(
        connection,
        cleaned_inventory_data,
        import_batch_id
    )

    financials_inserted = insert_product_financials(
        connection,
        cleaned_inventory_data,
        import_batch_id
    )

    connection.commit()

    print(f"\nImport batch created successfully with ID: {import_batch_id}")
    print(f"Products inserted successfully: {products_inserted}")
    print(f"Inventory snapshots inserted successfully: {snapshots_inserted}")
    print(f"Product financial records inserted successfully: {financials_inserted}")

    show_product_count(connection)
    # test_product_lookup(connection)
    show_import_batch_count(connection)
    show_inventory_snapshots_count(connection)
    show_product_financials_count(connection)
    connection.close()

if __name__ == "__main__":
    main()