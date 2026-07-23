import sqlite3
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
database_file = root_path / "database" / "inventory.db"


def create_connection():
    connection = sqlite3.connect(database_file)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def create_order_week(connection):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO OrderWeek (
            WeekStartDate,
            BudgetAmount,
            Notes
        )
        VALUES (?, ?, ?);
    """, (
        "2026-07-20",
        40000.00,
        "Test weekly ordering budget"
    ))

    return cursor.lastrowid

def create_order_scenario(connection, order_week_id):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO OrderScenario (
            ScenarioName,
            ScenarioDate,
            ExpectedDeliveryDate,
            Notes,
            OrderWeekId
        )
        VALUES (?, ?, ?, ?, ?);
    """, (
        "United Distributors Weekly Order",
        "2026-07-20",
        "2026-07-23",
        "Test distributor order scenario",
        order_week_id
    ))

    return cursor.lastrowid

def create_order_deal(connection, order_scenario_id):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO OrderScenarioDeal (
            OrderScenarioId,
            DealDescription,
            RequiredCases
        )
        VALUES (?, ?, ?);
    """, (
        order_scenario_id,
        "Woodford buy 25 cases, receive 3 cases free",
        25
    ))

    return cursor.lastrowid

def insert_order_items(
    connection,
    order_scenario_id,
    order_scenario_deal_id
):
    cursor = connection.cursor()

    items = [
        (
            order_scenario_id,
            order_scenario_deal_id,
            5,
            15,
            0,
            0,
            0,
            54.00
        ),
        (
            order_scenario_id,
            order_scenario_deal_id,
            53,
            10,
            0,
            3,
            0,
            28.00
        )
    ]

    cursor.executemany("""
        INSERT INTO OrderScenarioItem (
            OrderScenarioId,
            OrderScenarioDealId,
            ProductId,
            ProposedCases,
            ProposedBottles,
            FreeCases,
            FreeBottles,
            ProposedUnitCost
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, items)

def main():
    connection = create_connection()

    try:
        order_week_id = create_order_week(connection)

        order_scenario_id = create_order_scenario(
            connection,
            order_week_id
        )

        order_scenario_deal_id = create_order_deal(
            connection,
            order_scenario_id
        )

        insert_order_items(
            connection,
            order_scenario_id,
            order_scenario_deal_id
        )

        connection.commit()

        print(f"OrderWeek created: {order_week_id}")
        print(f"OrderScenario created: {order_scenario_id}")
        print(f"OrderScenarioDeal created: {order_scenario_deal_id}")

    except Exception as error:
        connection.rollback()
        print(f"Error creating test order data: {error}")
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()