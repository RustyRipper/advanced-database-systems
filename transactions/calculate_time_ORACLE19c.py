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

def load_sql_script(filename):
    with open(filename, 'r') as file:
        return file.read()

def execute_transaction(connection, sql_script, params):
    cursor = connection.cursor()
    start_time = time.time()

    cursor.execute(sql_script, params)
    connection.commit()

    end_time = time.time()
    cursor.close()

    return end_time - start_time

def reset_database():
    # Implement the logic to reset the database to a consistent state
    pass

def run_load_test(connection, iterations=10):
    sql_script = load_sql_script("select3.sql")
    params = {
        "PARKING_ID": 10,
        "START_DATE": "2020-12-12 12:12:12",
        "END_DATE": "2023-12-12 12:12:12"
    }  # Example parameters

    execution_times = []
    for i in range(iterations):
        # Ensure database state is consistent by re-running the SQL script
        reset_database()

        # Run the transaction and measure time
        execution_time = execute_transaction(connection, sql_script, params)
        execution_times.append(execution_time)
        print(f"Iteration {i + 1}: {execution_time:.4f} seconds")

    # Save results to a file
    results_df = pd.DataFrame({
        "Run": list(range(1, iterations + 1)),
        "Execution Time (s)": execution_times
    })

    results_df.to_csv("load_test_results.csv", index=False)
    print("\nResults saved to 'load_test_results.csv'.")

    # Calculate and print summary
    print("\nSummary:")
    print(f"Minimum Time: {min(execution_times):.4f} seconds")
    print(f"Maximum Time: {max(execution_times):.4f} seconds")
    print(f"Average Time: {sum(execution_times) / len(execution_times):.4f} seconds")


if __name__ == "__main__":
    # Oracle 19c
    connection = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DSN
    )
    
    run_load_test(connection, iterations=10)
    
    connection.close()