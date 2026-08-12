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

# Function to read teh spreadsheet and prepare the data for the database file
def inspect_product_master_file(file_path):
    try:
        # Read data from spreadsheet
        product_data = pd.read_excel(file_path, header=0, engine="openpyxl")

        return product_data

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise

    except Exception as error:
        print(f"Error reading Product Data File: {error}")
        raise