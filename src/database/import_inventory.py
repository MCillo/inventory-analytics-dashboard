"""
import_inventory.py

Purpose:
Read the mock inventory spreadsheet and inspect its columns
before importing data into SQLite.
"""

import pandas as pd
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]

inventory_file = root_path / "data" / "demo" / "Mock-Inventory.xlsx"

def inspect_inventory_file(file_path):
    try:
        inventory_data = pd.read_excel(file_path, header=1)

        print(f"Inventory file loaded successfully: {file_path.name}")

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

def main():
    inventory_data = inspect_inventory_file(inventory_file)

    cleaned_inventory_data = clean_inventory_data(inventory_data)

    print("\nCleaned inventory data:")
    print(cleaned_inventory_data.head())

if __name__ == "__main__":
    main()