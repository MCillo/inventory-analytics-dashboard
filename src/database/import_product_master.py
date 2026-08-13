"""
import_product_master.py

Purpose:
Read the Product_Master spreadsheet and inspect its columns
before importing data into SQLite.
"""

import pandas as pd
from pathlib import Path
import sqlite3
from datetime import datetime
import re

# Establish root path for file tree
root_path = Path(__file__).resolve().parents[2]

# Establish location for Product_Master file
product_master_file = root_path / "data" / "demo" / "Product_Master.xlsx"

# Establish location of database
database_file = root_path / "database" / "inventory.db"

# Function to read the spreadsheet and prepare the data for the database file
def inspect_product_master_file(file_path):
    try:
        # Read data from spreadsheet
        product_data = pd.read_excel(file_path, header=0, engine="openpyxl")

        print(f"Product Data File loaded Successfully: {file_path.name}")

        product_data = product_data.rename(columns={
            "SKU": "sku",
            "Description": "description",
            "Size": "size",
            "Case Pack": "case_pack",
            "Category": "category",
            "Sub Category": "sub_category",
            "Vendor": "vendor"
            "Contact First Name": "contact_first_name",
            "Contact Last Name": "contact_last_name",
            "Seasonal": "seasonal",
            "Discontinued": "discontinued",
            "POS Status": "pos_status"
        })

        product_data = product_data[[
            "sku",
            "description",
            "size",
            "case_pack",
            "category",
            "sub_category",
            "vendor",
            "contact_first_name",
            "contact_last_name",
            "seasonal",
            "discontinued",
            "pos_status"
        ]]

        print("\nCleaned columns:")
        for column in product_data.columns:
            print(f"- {column}")

        return product_data

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise

    except Exception as error:
        print(f"Error reading Product Data File: {error}")
        raise

# Function to create a connection to the database
def create_connection():
    try:
        connection = sqlite3.connect(database_file)
        connection.execute("Pragma foreign_keys = ON;")
        return connection
    except sqlite3.Error as error:
        print(f"Database Connection Error: {error}")
        raise

def main():
    connection = None

    try:
        product_data = inspect_product_master_file(product_master_file)
        connection = create_connection()

        print("\nProduct Master Columns:")
        print(product_data.columns.tolist())

        print("\nFirst Five Products:")
        print(product_data.head())

    finally:
        if connection is not None:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()