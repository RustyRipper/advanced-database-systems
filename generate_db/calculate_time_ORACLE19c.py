import os
import time
import pandas as pd
import oracledb
from dotenv import load_dotenv

load_dotenv()

# Set up environment variables for user credentials
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DSN = "localhost:1521/ORCLPDB1"

ddl_file_path = '../db.ddl'
db_remove_file_path = './remove_db.ddl'

connection = oracledb.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    dsn=DSN
)

def load_sql_script(filename):
    with open(filename, 'r') as file:
        return file.read()

def execute_transaction( sql_script, params):
    cursor = connection.cursor()
    start_time = time.time()

    cursor.execute(sql_script, params)
    connection.commit()

    end_time = time.time()
    cursor.close()

    return end_time - start_time

def insert_data_from_csv(table_name, csv_file, encoding='utf-8'):
    try:
        cursor = connection.cursor()
        data = pd.read_csv(csv_file, encoding=encoding)
        if 'ID' in data.columns:
            data.drop(columns=['ID'], inplace=True)

        timestamp_columns = ['OPEN_TIME', 'CLOSE_TIME', 'START_DATE',
                             'END_DATE', 'CREATED_AT', 'ADDITION_TIME']
        date_columns = ['DATE_OF_BIRTH', 'ADDITION_TIME']

        columns = ', '.join(data.columns)
        placeholders = []

        for i, col in enumerate(data.columns):
            if col in timestamp_columns:
                placeholders.append(
                    f"TO_TIMESTAMP(:{i + 1}, 'YYYY-MM-DD HH24:MI:SS')")
            elif col in date_columns:
                placeholders.append(f"TO_DATE(:{i + 1}, 'YYYY-MM-DD')")
            else:
                placeholders.append(f":{i + 1}")

        sql = f"INSERT INTO {table_name.upper()} ({columns}) VALUES ({', '.join(placeholders)})"

        # Convert relevant columns to the appropriate datetime format
        for col in timestamp_columns:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col],
                                           errors='coerce').dt.strftime(
                    '%Y-%m-%d %H:%M:%S')

        print(sql)
        rows = [tuple(row) for row in data.to_numpy()]
        cursor.executemany(sql, rows)
        connection.commit()
        print(f"Data from {csv_file} inserted successfully into {table_name}.")
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}. Trying with a different encoding.")
        insert_data_from_csv(table_name, csv_file, encoding='ISO-8859-1')

def execute_ddl(file_path):
    cursor = connection.cursor()
    with open(file_path, 'r') as ddl_file:
        ddl_statements = ddl_file.read().split(';')
        for statement in ddl_statements:
            if statement.strip():
                print(f"Executing: {statement.strip()}")
                cursor.execute(statement)
    connection.commit()
    print(f"Executed DDL statements from {file_path} successfully.")


def reset_database():
    try:
        cursor = connection.cursor()
        # Flush shared pool and buffer cache
        
        # try:
        #     execute_ddl(db_remove_file_path)
        # except Exception as e:
        #     print(e)
        #     print("Can't")
        # execute_ddl(ddl_file_path)
        # insert_data_from_csv("Parking", '../Parking.csv')
        # insert_data_from_csv("ParkingUser", '../ParkingUser.csv')
        # insert_data_from_csv("ClientCar", '../ClientCar.csv')
        # insert_data_from_csv("ParkingSpot", '../ParkingSpot.csv')
        # insert_data_from_csv("Reservation", '../Reservation.csv')
        # insert_data_from_csv("Payment", '../Payment.csv')
        # insert_data_from_csv("StripeCharge", '../StripeCharge.csv')

        cursor.execute("ALTER SYSTEM FLUSH SHARED_POOL")
        cursor.execute("ALTER SYSTEM FLUSH BUFFER_CACHE")

        connection.commit()
        print("Database buffers flushed and cleared successfully.")
    except Exception as e:
        print(f"An error occurred while resetting the database: {e}")
    finally:
        cursor.close()
        
def run_load_test(test_queries, iterations=10):
    execution_times = []
    for i in range(iterations):
        for query_name, query_data in test_queries.items():
            reset_database()
            execution_time = execute_transaction(query_data["script"], query_data["params"])
            execution_times.append((query_name, i + 1, execution_time))
            print(f"{query_name} - Iteration {i + 1}: {execution_time:.4f} seconds")

    results_df = pd.DataFrame(execution_times, columns=["Query", "Run", "Execution Time (s)"])
    results_df.to_csv("load_test_results.csv", index=False)
    print("\nResults saved to 'load_test_results.csv'.")

    print("\nSummary:")
    summary_df = results_df.groupby("Query")["Execution Time (s)"].agg(["min", "max", "mean"]).reset_index()
    print(summary_df)

    detailed_report = results_df.pivot(index="Run", columns="Query", values="Execution Time (s)")
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
        # "select2": {
        #     "script": load_sql_script("./transactions/select2.sql"),
        #     "params": {
        #         "start_date": "2024-12-11 12:12:12",
        #         "end_date": "2024-12-12 12:12:12"
        #     }
        # },
        "select3": {
            "script": load_sql_script("./transactions/select3.sql"),
            "params": {
                "PARKING_ID": 10,
                "START_DATE": "2020-5-6 12:12:12",
                "END_DATE": "2023-5-1 12:12:12"
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
    
    run_load_test(test_queries, iterations=10)
    
    connection.close()