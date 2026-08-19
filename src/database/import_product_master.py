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
            "Vendor": "vendor",
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

# function to Clean up the data read form the spreadsheet to work better with the database
def clean_product_master_data(product_data):
    # Work with a copy so the original DataFrame is not modified
    product_data = product_data.copy()

    # Remove completely empty rows
    product_data = product_data.dropna(how="all")

    # Keep only the columns required for this import
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
    ]].copy()

    # Treat cells containing only spaces as missing values
    product_data = product_data.replace(
        r"^\s*$",
        pd.NA,
        regex=True
    )

    required_columns = [
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
    ]

    missing_values = (
        product_data[required_columns]
        .isna()
        .any(axis=1)
    )

    if missing_values.any():
        print("\nRows containing missing required values:")
        print(
            product_data.loc[
                missing_values,
                required_columns
            ]
        )

        raise ValueError(
            "Product Master contains missing required values."
        )

    # Remove leading and trailing spaces from text columns
    text_columns = [
        "description",
        "size",
        "category",
        "sub_category",
        "vendor",
        "contact_first_name",
        "contact_last_name"
    ]

    for column in text_columns:
        product_data[column] = (
            product_data[column]
            .astype("string")
            .str.strip()
        )

    # Normalize and validate Boolean columns
    boolean_columns = [
        "seasonal",
        "discontinued",
        "pos_status"
    ]

    for column in boolean_columns:
        product_data[column] = (
            product_data[column]
            .astype("string")
            .str.strip()
            .str.upper()
        )

        invalid_values = ~product_data[column].isin(
            ["Y", "N"]
        )

        if invalid_values.any():
            bad_values = (
                product_data.loc[invalid_values, column]
                .tolist()
            )

            raise ValueError(
                f"Invalid values in {column}: {bad_values}. "
                "Only Y or N are allowed."
            )

    # Convert Y/N values into SQLite Boolean values
    boolean_mapping = {
        "Y": 1,
        "N": 0
    }

    for column in boolean_columns:
        product_data[column] = (
            product_data[column]
            .map(boolean_mapping)
            .astype("Int64")
        )

    # Convert numeric fields
    product_data["sku"] = pd.to_numeric(
        product_data["sku"],
        errors="raise"
    ).astype("Int64")

    product_data["case_pack"] = pd.to_numeric(
        product_data["case_pack"],
        errors="raise"
    ).astype("Int64")

    # Validate case-pack quantities
    if (product_data["case_pack"] <= 0).any():
        raise ValueError(
            "Case Pack must be greater than zero."
        )

    # Validate SKU uniqueness
    duplicate_skus = product_data[
        product_data["sku"].duplicated(keep=False)
    ]

    if not duplicate_skus.empty:
        print("\nRows containing duplicate SKUs:")
        print(
            duplicate_skus[[
                "sku",
                "description",
                "size"
            ]]
        )

        raise ValueError(
            "Product Master contains duplicate SKUs."
        )

    print(
        f"Product Master data cleaned successfully: "
        f"{len(product_data)} products"
    )

    return product_data



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
        # Read and rename the spreadsheet columns
        product_data = inspect_product_master_file(
            product_master_file
        )

        # Validate and normalize the spreadsheet data
        product_data = clean_product_master_data(
            product_data
        )

        # Connect after the spreadsheet passes validation
        connection = create_connection()

        print("\nFirst Five Cleaned Products:")
        print(product_data.head())

    except Exception as error:
        print(f"\nProduct Master import failed: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()