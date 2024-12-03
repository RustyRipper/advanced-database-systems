import os
import time
import pandas as pd
import oracledb
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DSN = "localhost:1521/ORCLPDB1"

# Establish connection to the database
connection = oracledb.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    dsn=DSN
)

# Set the date format for the session
cursor = connection.cursor()
cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
cursor.close()

def create_indexes(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE INDEX idx_clientcar_registration_number ON ClientCar(registration_number)")
    cursor.execute("CREATE INDEX idx_reservation_registration_number ON Reservation(registration_number)")
    # cursor.execute("CREATE INDEX idx_reservation_user_id ON Reservation(user_id)")
    cursor.execute("CREATE BITMAP INDEX idx_clientcar_brand ON ClientCar(brand)")
    # cursor.execute("CREATE INDEX idx_reservation_parking_spot_id ON Reservation(parking_spot_id)")
    # cursor.execute("CREATE INDEX idx_reservation_dates ON Reservation(start_date, end_date)")
    connection.commit()
    cursor.close()
    print("Indexes created successfully.")

def drop_indexes(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("DROP INDEX idx_clientcar_registration_number")
        cursor.execute("DROP INDEX idx_reservation_registration_number")
        # cursor.execute("DROP INDEX idx_reservation_user_id")
        cursor.execute("DROP INDEX idx_clientcar_brand")
        # cursor.execute("DROP INDEX idx_reservation_parking_spot_id")
        # cursor.execute("DROP INDEX idx_reservation_dates")
        connection.commit()
    except:
        pass
    cursor.close()
    print("Indexes dropped successfully.")

def flush_buffers(connection):
    cursor = connection.cursor()
    cursor.execute("ALTER SYSTEM FLUSH SHARED_POOL")
    cursor.execute("ALTER SYSTEM FLUSH BUFFER_CACHE")
    connection.commit()
    cursor.close()
    print("Database buffers flushed and cleared successfully.")

def load_sql_script(filename):
    with open(filename, 'r') as file:
        return file.read()

def measure_query_time(connection, query, params):
    start_time = time.time()
    cursor = connection.cursor()
    cursor.execute(query, params)
    cursor.fetchall()
    end_time = time.time()
    cursor.close()
    return end_time - start_time

def run_index_experiments(connection, queries, iterations=10, index_type="No Index"):
    results = []

    for query_name, query_data in queries.items():
        for i in range(iterations):
            flush_buffers(connection)
            execution_time = measure_query_time(connection, query_data["script"], query_data["params"])
            results.append((query_name, i + 1, execution_time, index_type))
            print(f"{query_name} - Iteration {i + 1}: {execution_time:.4f} seconds")

    return results

if __name__ == "__main__":
    
    test_queries = {
        "select2": {
            "script": load_sql_script("./transactions/select2.sql"),
            "params": {
                "start_date": "2020-05-11 08:06:00",
                "end_date": "2020-05-12 09:12:00"
            }
        }
    }
    drop_indexes(connection)

    # Run experiments without indexes
    print("Running experiments without indexes...")
    results_no_index = run_index_experiments(connection, test_queries, index_type="No Index")

    # Create indexes and run experiments
    print("Creating indexes...")

    create_indexes(connection)
    print("Running experiments with indexes...")
    results_with_index = run_index_experiments(connection, test_queries, index_type="With Index")
    print("Dropping indexes...")
    drop_indexes(connection)

    # Combine results
    results = results_no_index + results_with_index

    # Save results to a file
    results_df = pd.DataFrame(results, columns=["Query", "Run", "Execution Time (s)", "Index Type"])
    results_df.to_csv("index_experiment_results.csv", index=False)
    print("\nResults saved to 'index_experiment_results.csv'.")

    # Calculate and print summary
    print("\nSummary:")
    summary_df = results_df.groupby(["Query", "Index Type"])["Execution Time (s)"].agg(["min", "max", "mean"]).reset_index()
    print(summary_df)

    # Save detailed report with index types
    detailed_report = results_df.pivot(index="Run", columns=["Query", "Index Type"], values="Execution Time (s)")
    detailed_report.to_csv("detailed_index_experiment_results.csv")
    print("\nDetailed results saved to 'detailed_index_experiment_results.csv'.")
    print("\nDetailed Report:")
    print(detailed_report)

    connection.close()