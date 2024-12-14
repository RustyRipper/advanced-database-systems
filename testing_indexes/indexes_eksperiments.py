import os
import time
import pandas as pd
import oracledb


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

def create_btree_index(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE INDEX idx_reservation_parking_spot_id ON Reservation(parking_spot_id)")
    connection.commit()
    cursor.close()

def create_bitmap_index(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE BITMAP INDEX idx_parkingspot_active ON ParkingSpot(active)")
    connection.commit()
    cursor.close()

def create_functional_index(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE INDEX idx_clientcar_lower_brand ON ClientCar(LOWER(brand))")
    connection.commit()
    cursor.close()

def drop_index(connection, index_name):
    cursor = connection.cursor()
    cursor.execute(f"DROP INDEX {index_name}")
    connection.commit()
    cursor.close()

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

def flush_buffers(connection):
    cursor = connection.cursor()
    cursor.execute("ALTER SYSTEM FLUSH SHARED_POOL")
    cursor.execute("ALTER SYSTEM FLUSH BUFFER_CACHE")
    connection.commit()
    cursor.close()
    print("Database buffers flushed and cleared successfully.")

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
        # "select1": {
        #     "script": load_sql_script("./transactions/select1.sql"),
        #     "params": {
        #         "min_amount": 0,
        #         "registration_number_pattern": "%",
        #         "parking_id": 1,
        #         "min_date": "2020-12-12 12:12:12"
        #     }
        # },
        "select2": {
            "script": load_sql_script("./transactions/select2.sql"),
            "params": {
                "start_date": "2020-05-01 08:06:00",
                "end_date": "2020-05-12 09:12:00"
            }
        },
        # "select3": {
        #     "script": load_sql_script("./transactions/select3.sql"),
        #     "params": {
        #         "PARKING_ID": 10,
        #         "START_DATE": "2020-05-06 12:12:12",
        #         "END_DATE": "2023-05-01 12:12:12"
        #     }
        # }
    }

    # Run experiments without indexes
    print("Running experiments without indexes...")
    results_no_index = run_index_experiments(connection, test_queries, index_type="No Index")

    # Create B-tree index and run experiments
    print("Creating B-tree index...")
    create_btree_index(connection)
    print("Running experiments with B-tree index...")
    results_btree_index = run_index_experiments(connection, test_queries, index_type="B-tree Index")
    print("Dropping B-tree index...")
    drop_index(connection, "idx_reservation_parking_spot_id")

    # Create Bitmap index and run experiments
    print("Creating Bitmap index...")
    create_bitmap_index(connection)
    print("Running experiments with Bitmap index...")
    results_bitmap_index = run_index_experiments(connection, test_queries, index_type="Bitmap Index")
    print("Dropping Bitmap index...")
    drop_index(connection, "idx_parkingspot_active")

    # Create Functional index and run experiments
    print("Creating Functional index...")
    create_functional_index(connection)
    print("Running experiments with Functional index...")
    results_functional_index = run_index_experiments(connection, test_queries, index_type="Functional Index")
    print("Dropping Functional index...")
    drop_index(connection, "idx_clientcar_lower_brand")

    # Combine results
    results = results_no_index + results_btree_index + results_bitmap_index + results_functional_index

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