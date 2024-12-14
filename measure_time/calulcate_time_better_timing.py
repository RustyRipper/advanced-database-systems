import time
from datetime import datetime

import oracledb
import pandas as pd

ddl_file_path = './db.ddl'
db_remove_file_path = './remove_db.ddl'

connection = oracledb.connect(
    user="system",
    password="welcome123",
    dsn="localhost:1521/XE"
)


def load_sql_script(filename):
    with open(filename, 'r') as file:
        return file.read()


def execute_transaction(sql_script, params):
    cursor = connection.cursor()
    cursor.execute(
        "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
    start_time = time.time()

    cursor.execute(sql_script, params)
    connection.commit()

    end_time = time.time()
    cursor.close()

    return end_time - start_time


def reset_database():
    try:
        cursor = connection.cursor()
        # Flush shared pool and buffer cache
        cursor.execute("ALTER SYSTEM FLUSH SHARED_POOL")
        cursor.execute("ALTER SYSTEM FLUSH BUFFER_CACHE")
        connection.commit()
        print("Database buffers flushed and cleared successfully.")
    except Exception as e:
        print(f"An error occurred while resetting the database: {e}")
    finally:
        cursor.close()


def load_indexes():
    cursor = connection.cursor()
    cursor.execute(load_sql_script("./transactions/index1_select3.sql"))
    cursor.execute(load_sql_script("./transactions/index2_select3.sql"))
    connection.commit()
    cursor.close()


def remove_indexes():
    cursor = connection.cursor()
    cursor.execute(load_sql_script("./transactions/index1_select3_remove.sql"))
    cursor.execute(load_sql_script("./transactions/index2_select3_remove.sql"))
    connection.commit()
    cursor.close()


def run_load_test(test_queries, iterations=10):
    execution_times = []
    load_indexes()
    for i in range(iterations):
        reset_database()
        for query_name, query_data in test_queries.items():
            execution_time = execute_transaction(query_data["script"],
                                                 query_data["params"])
            execution_times.append((query_name, i + 1, execution_time))
            print(
                f"{query_name} - Iteration {i + 1}: {execution_time:.4f} seconds")

    remove_indexes()
    results_df = pd.DataFrame(execution_times,
                              columns=["Query", "Run", "Execution Time (s)"])
    results_df.to_csv("load_test_results.csv", index=False)
    print("\nResults saved to 'load_test_results.csv'.")

    print("\nSummary:")
    summary_df = results_df.groupby("Query")["Execution Time (s)"].agg(
        ["min", "max", "mean"]).reset_index()
    print(summary_df)

    detailed_report = results_df.pivot(index="Run", columns="Query",
                                       values="Execution Time (s)")
    detailed_report.to_csv("detailed_load_test_results.csv")
    print("\nDetailed results saved to 'detailed_load_test_results.csv'.")
    print("\nDetailed Report:")
    print(detailed_report)


if __name__ == "__main__":
    test_queries = {
        "select1": {
            "script": load_sql_script("./transactions/select1.sql"),
            "params": {
                "min_amount": 0,
                "registration_number_pattern": "%",
                "parking_id": 1,
                "min_date": "2020-12-12 12:12:12"
            }
        },
        "select1_deoptimized": {
            "script": load_sql_script("./transactions/select1_deoptimized.sql"),
            "params": {
                "min_amount": 0,
                "registration_number_pattern": "%",
                "parking_id": 1,
                "min_date": "2020-12-12 12:12:12"
            }
        },
        "select3": {
            "script": load_sql_script("./transactions/select3.sql"),
            "params": {
                "PARKING_ID": 10,
                "START_DATE": datetime(2020, 12, 12, 12, 12, 12),
                "END_DATE": datetime(2023, 12, 12, 12, 12, 12)
            }
        },
        "insert_alone": {
            "script": load_sql_script("./transactions/insert_alone.sql"),
            "params": {
                "PARKING_ID": 10,
                "USER_ID": 10,
                "new_end_date": "2022-12-12 18:12:12",
                "new_start_date": "2022-12-12 06:12:12",
                "reference_date": "2020-11-27"
            }
        },
        "delete": {
            "script": load_sql_script("./transactions/delete.sql"),
            "params": {
                "discard_date_min": "2021-12-1 12:12:12",
                "discard_date_max": "2021-12-5 12:12:12"
            }
        },
        "delete_deoptimized": {
            "script": load_sql_script("./transactions/delete_deoptimized.sql"),
            "params": {
                "discard_date_min": "2021-12-1 12:12:12",
                "discard_date_max": "2021-12-5 12:12:12"
            }
        },
        "update": {
            "script": load_sql_script("./transactions/update.sql"),
            "params": {
                "p_min_age": 18,
                "p_color_toyota": "Red",
                "p_color_bmw": "Black",
                "p_color_honda": "Green",
                "p_days_since_reservation": 30,
                "p_color_admin": "Gold",
                "p_color_default": "White"
            }
        }
    }
    #load_indexes()
    #remove_indexes()
    run_load_test(test_queries, iterations=5)

    connection.close()
