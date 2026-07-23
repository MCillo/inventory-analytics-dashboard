"""
create_database.py

Purpose:
Create the SQLite database file and build the initial database tables
for the Inventory Analytics Dashboard project.
"""

# - sqlite3: built-in Python library for SQLite databases
import sqlite3
# - pathlib.Path: helps build file paths safely across Mac/Windows/Linux
from pathlib import Path 


root_path = Path(__file__).resolve().parents[2]

database_folder = root_path / "database"

database_file = database_folder / "inventory.db"

database_folder.mkdir(exist_ok=True)

def create_connection():
    try:
        connection = sqlite3.connect(database_file)
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    except sqlite3.Error as error:
        print(f"Database connection error: {error}")
        raise

def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Category (
                CategoryId INTEGER PRIMARY KEY AUTOINCREMENT,
                CategoryName TEXT NOT NULL UNIQUE
            );
        """)
        print("Category table created successfully.")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Vendor (
                VendorId INTEGER PRIMARY KEY AUTOINCREMENT,
                VendorName TEXT NOT NULL UNIQUE
            );
        """)
        print("Vendor table created successfully.")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Role (
                RoleId INTEGER PRIMARY KEY AUTOINCREMENT,
                RoleName TEXT NOT NULL UNIQUE
            );
        """)
        print("Role table created successfully.")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ImportBatch (
                ImportBatchId INTEGER PRIMARY KEY AUTOINCREMENT,
                ImportDate DATETIME NOT NULL,
                ReportDate DATETIME NOT NULL,
                FileName TEXT NOT NULL,
                ImportType TEXT NOT NULL,
                Status TEXT NOT NULL
            );
        """)
        print("ImportBatch table created successfully.")

        cursor.execute("""
            create table if not exists SubCategory (
                SubCategoryId INTEGER PRIMARY KEY AUTOINCREMENT,
                SubCategoryName TEXT,
                CategoryId INTEGER NOT NULL,
                FOREIGN KEY (CategoryId) REFERENCES Category(CategoryId)
            );
        """)
        print("SubCategory table created successfully.")

        cursor.execute("""
            create table if not exists SalesRep (
                SalesRepId INTEGER PRIMARY KEY AUTOINCREMENT,
                ContactFirstName TEXT,
                ContactLastName TEXT,
                ContactPhone TEXT,
                ContactEmail TEXT,
                SalesRepPosition TEXT,
                VendorId INTEGER NOT NULL,
                FOREIGN KEY (VendorId) REFERENCES Vendor(VendorId)
            );
        """)
        print("SalesRep table created successfully.")

        cursor.execute("""
            create table if not exists AppUser (
                AppUserId INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT NOT NULL UNIQUE,
                FirstName VARCHAR,
                LastName VARCHAR,
                Email TEXT NOT NULL UNIQUE,
                RoleId INTEGER NOT NULL,
                IsActive INTEGER DEFAULT 1,
                FOREIGN KEY (RoleId) REFERENCES Role(RoleId)
            );
        """)
        print("AppUser table created successfully.")

        cursor.execute("""
            create table if not exists Product (
                ProductId INTEGER PRIMARY KEY AUTOINCREMENT,
                SKU INTEGER UNIQUE,
                ProductName TEXT,
                Size TEXT,
                CasePack INTEGER,
                IsSeasonal INTEGER DEFAULT 0,
                IsDiscontinued INTEGER DEFAULT 0,
                IsInPOS INTEGER DEFAULT 0,
                DealLevel INTEGER,
                SubCategoryId INTEGER,
                VendorId INTEGER,
                SalesRepId INTEGER,
                FOREIGN KEY (SubCategoryId) REFERENCES SubCategory(SubCategoryId),
                FOREIGN KEY (VendorId) REFERENCES Vendor(VendorId),
                FOREIGN KEY (SalesRepId) REFERENCES SalesRep(SalesRepId)
            );
        """)

        print("Product table created successfully.")

        cursor.execute("""
            create table if not exists InventorySnapshot (
                InventorySnapshotId INTEGER PRIMARY KEY AUTOINCREMENT,
                QuantityOnHand INTEGER,
                SnapshotDate DATETIME,
                ImportBatchId INTEGER,  
                ProductId INTEGER,
                FOREIGN KEY (ProductId) REFERENCES Product(ProductId),
                FOREIGN KEY (ImportBatchId) REFERENCES ImportBatch(ImportBatchId)
            );
        """)
        print("InventorySnapshot table created successfully.")

        cursor.execute("""
            create table if not exists SalesHistory (
                SalesHistoryId INTEGER PRIMARY KEY AUTOINCREMENT,
                UnitsSold INTEGER,
                PeriodStartDate DATETIME,
                PeriodEndDate DATETIME,
                ImportBatchId INTEGER,
                ProductId INTEGER,
                FOREIGN KEY (ProductId) REFERENCES Product(ProductId),
                FOREIGN KEY (ImportBatchId) REFERENCES ImportBatch(ImportBatchId)
            );
        """)
        print("SalesHistory table created successfully.")   

        cursor.execute("""
            create table if not exists OrderWeek (
            OrderWeekId INTEGER PRIMARY KEY AUTOINCREMENT,
            WeekStartDate DATETIME,
            BudgetAmount REAL,
            Notes TEXT
            );
        """)
        print("OrderWeek table created successfully.")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS OrderScenario (
            OrderScenarioId INTEGER PRIMARY KEY AUTOINCREMENT,
            ScenarioName TEXT,
            ScenarioDate DATETIME,
            ExpectedDeliveryDate DATETIME,
            Notes TEXT,

            OrderWeekId INTEGER,
            VendorId INTEGER,
            SalesRepId INTEGER,
            AppUserId INTEGER,

            FOREIGN KEY (OrderWeekId) REFERENCES OrderWeek(OrderWeekId),
            FOREIGN KEY (VendorId) REFERENCES Vendor(VendorId),
            FOREIGN KEY (SalesRepId) REFERENCES SalesRep(SalesRepId),
            FOREIGN KEY (AppUserId) REFERENCES AppUser(AppUserId)
            );
        """)
        print("OrderScenario table created successfully.")

        cursor.execute("""
            create table if not exists OrderScenarioDeal (
                OrderScenarioDealId INTEGER PRIMARY KEY AUTOINCREMENT,
                OrderScenarioId INTEGER,
                DealDescription VARCHAR,
                RequiredCases INTEGER,
                FOREIGN KEY (OrderScenarioId) REFERENCES OrderScenario(OrderScenarioId)
            );    
        """)
        print("OrderScenarioDeal table created successfully.")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS OrderScenarioItem (
                OrderScenarioItemId INTEGER PRIMARY KEY AUTOINCREMENT,

                OrderScenarioId INTEGER NOT NULL,
                OrderScenarioDealId INTEGER,
                ProductId INTEGER,

                ProposedCases INTEGER DEFAULT 0,
                ProposedBottles INTEGER DEFAULT 0,
                FreeCases INTEGER DEFAULT 0,
                FreeBottles INTEGER DEFAULT 0,
                ProposedUnitCost REAL,

                TempProductName TEXT,
                TempSize TEXT,
                TempNotes TEXT,

                FOREIGN KEY (OrderScenarioId) REFERENCES OrderScenario(OrderScenarioId),

                FOREIGN KEY (OrderScenarioDealId) REFERENCES OrderScenarioDeal(OrderScenarioDealId),

                FOREIGN KEY (ProductId) REFERENCES Product(ProductId)
            );
        """)
        print("OrderScenarioItem table created successfully.")

        cursor.execute("""
            create table if not exists ProductFinancial (
                ProductFinancialId INTEGER PRIMARY KEY AUTOINCREMENT,
                EffectiveDate DATETIME,
                ProductId INTEGER,
                ImportBatchId INTEGER,
                RetailPrice REAL,
                CostPrice REAL,
                MarginPercent REAL,
                MarginDollars REAL,
                FOREIGN KEY (ProductId) REFERENCES Product(ProductId),
                FOREIGN KEY (ImportBatchId) REFERENCES ImportBatch(ImportBatchId)
            );
        """)
        print("ProductFinancial table created successfully.")

    except sqlite3.Error as error: 
        print(f"Error creating tables: {error}")
        raise




def show_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%';
    """)

    tables = cursor.fetchall()

    print("Tables in database:")
    for table in tables:
        print(table[0])


def main():
    connection = create_connection()

    create_tables(connection)

    connection.commit()
    show_tables(connection) 
    connection.close()

if __name__ == "__main__":
    main()