import os
import time
import subprocess
import oracledb
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()

ddl_file_path = './db.ddl'
db_remove_file_path = './remove_db.ddl'

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
# DSN = "localhost:1521/ORCLPDB1"

DSN = "localhost:1521/ORCLCDB"

connection = oracledb.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    dsn=DSN,
    mode=oracledb.SYSDBA
)

def load_sql_script(filename):
    with open(filename, 'r') as file:
        return file.read()

def execute_transaction(sql_script, params):
    cursor = connection.cursor()
    cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
    start_time = time.time()

    cursor.execute(sql_script, params)
    connection.commit()

    end_time = time.time()
    cursor.close()

    return end_time - start_time

def generate_explain_plan(sql_script, params):
    cursor = connection.cursor()
    explain_sql = f"EXPLAIN PLAN FOR {sql_script}"
    cursor.execute(explain_sql, params)
    cursor.execute("SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY())")
    plan = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    plan_df = pd.DataFrame(plan, columns=columns)
    cursor.close()
    return plan_df

def reset_database():
    try:
        cursor = connection.cursor()
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
    cursor.execute(load_sql_script("./transactions/index1_delete.sql"))
    cursor.execute(load_sql_script("./transactions/SELECT2_index1.sql"))
    cursor.execute(load_sql_script("./transactions/SELECT2_index2.sql"))
    connection.commit()
    cursor.close()

def remove_indexes():
    cursor = connection.cursor()
    cursor.execute(load_sql_script("./transactions/index1_select3_remove.sql"))
    cursor.execute(load_sql_script("./transactions/index2_select3_remove.sql"))
    cursor.execute(load_sql_script("./transactions/index1_delete_remove.sql"))
    cursor.execute(load_sql_script("./transactions/SELECT2_index1_remove.sql"))
    cursor.execute(load_sql_script("./transactions/SELECT2_index2_remove.sql"))
    connection.commit()
    cursor.close()

def run_load_test(test_queries, iterations=10, indexes=False, filename_prefix="load_test"):
    execution_times = []
    
    # Tworzenie folderu na wyniki testów
    test_results_dir = os.path.join("etap10", filename_prefix)
    os.makedirs(test_results_dir, exist_ok=True)
    
    if indexes:
        load_indexes()
    
    # Generowanie EXPLAIN PLAN tylko raz dla każdego zapytania
    for query_name, query_data in test_queries.items():
        execute_transaction(query_data["script"], query_data["params"])
        explain_plan = generate_explain_plan(query_data["script"], query_data["params"])
        # Zapis EXPLAIN PLAN
        explain_plan.to_csv(os.path.join(test_results_dir, f"{query_name}_explain_plan.csv"), index=False)
        print(f"Explain plan saved for {query_name}")
            
    for i in range(iterations):
        for query_name, query_data in test_queries.items():
            # Wykonanie zapytania
            execution_time = execute_transaction(query_data["script"], query_data["params"])
            execution_times.append((query_name, i + 1, execution_time))
            print(f"{query_name} - Iteration {i + 1}: {execution_time:.4f} seconds")
        
        # Zbieranie danych pamięciowych po każdej iteracji
        # query_memory_usage(filename_prefix=filename_prefix + f"_iteration_{i + 1}")
    
    # query_memory_usage(filename_prefix=filename_prefix + f"_memory" )
                       
    if indexes:
        remove_indexes()
    
    results_df = pd.DataFrame(execution_times, columns=["Query", "Run", "Execution Time (s)"])
    results_df.to_csv(os.path.join(test_results_dir, f"{filename_prefix}_results.csv"), index=False)
    print(f"\nResults saved to '{test_results_dir}/{filename_prefix}_results.csv'.")
    
    print("\nSummary:")
    summary_df = results_df.groupby("Query")["Execution Time (s)"].agg(["min", "max", "mean"]).reset_index()
    print(summary_df)
    
    # Zapisanie tabeli ze średnimi czasami wykonania
    average_times_df = summary_df.rename(columns={"mean": "Average Execution Time (s)"})[["Query", "Average Execution Time (s)"]]
    average_times_df.to_csv(os.path.join(test_results_dir, f"{filename_prefix}_average_execution_times.csv"), index=False)
    print(f"\nAverage execution times saved to '{test_results_dir}/{filename_prefix}_average_execution_times.csv'.")
    
    detailed_report = results_df.pivot(index="Run", columns="Query", values="Execution Time (s)")
    detailed_report.to_csv(os.path.join(test_results_dir, f"{filename_prefix}_detailed_results.csv"))
    print(f"\nDetailed results saved to '{test_results_dir}/{filename_prefix}_detailed_results.csv'.")
    print("\nDetailed Report:")
    print(detailed_report)
    
    # Generowanie wykresów zmian pamięci
    # generate_memory_plots(test_results_dir, filename_prefix)
    
def remove_inmemory_compression(table):
    cursor = connection.cursor()
    cursor.execute(f"ALTER TABLE {table} NO INMEMORY")
    connection.commit()
    cursor.close()

def set_inmemory_compression(table, compression):
    remove_inmemory_compression(table)
    cursor = connection.cursor()
    cursor.execute(f"ALTER TABLE {table} INMEMORY {compression}")
    # Execute the DBMS_INMEMORY.POPULATE procedure
    plsql_block = f"""
    BEGIN
    DBMS_INMEMORY.POPULATE(
        schema_name => NULL,
        table_name => '{table}',
        subobject_name => NULL
    );
    END;
    """
    cursor.execute(plsql_block)
    connection.commit()
    cursor.close()
    
def generate_memory_plots(test_results_dir, filename_prefix):
    import glob

    # Ścieżka do plików session_level_statistics.csv
    stats_files = glob.glob(os.path.join(test_results_dir, f"{filename_prefix}_iteration_*", "session_level_statistics.csv"))
    
    # Lista statystyk do wykresów
    selected_stats = [
        "IM scan rows optimized",
        "IM scan rows projected",
        "IM scan CUs memcompress for *",
        "IM scan EU bytes in-memory"
    ]
    
    memory_data = {}
    
    for file in stats_files:
        iteration = int(os.path.basename(os.path.dirname(file)).split("_")[-1])
        df = pd.read_csv(file)
        for stat in selected_stats:
            value = df[df['name'] == stat]['total_value'].values
            if len(value) > 0:
                memory_data.setdefault(stat, []).append(value[0])
            else:
                memory_data.setdefault(stat, []).append(0)
    
    # Tworzenie DataFrame
    memory_df = pd.DataFrame(memory_data, index=range(1, len(stats_files)+1))
    memory_df.index.name = 'Iteration'
    
    # Generowanie wykresów
    plt.figure(figsize=(12, 8))
    for stat in selected_stats:
        plt.plot(memory_df.index, memory_df[stat], marker='o', label=stat)
    
    plt.xlabel('Iteration')
    plt.ylabel('Total Value')
    plt.title('Session Level Statistics Over Iterations')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(test_results_dir, f"{filename_prefix}_memory_statistics_plot.png")
    plt.savefig(plot_path)
    plt.show()
    print(f"Memory statistics plot saved to '{plot_path}'.")

def query_memory_usage(filename_prefix="load_test_user_compression"):

    cursor = connection.cursor()
    
    # Tworzenie ścieżki do folderu na wyniki pamięciowe
    test_results_dir = os.path.join("etap10", filename_prefix)
    os.makedirs(test_results_dir, exist_ok=True)
    
    # Sprawdzenie użycia pamięci SGA
    cursor.execute("SELECT * FROM V$SGA")
    sga_results = cursor.fetchall()
    sga_columns = [desc[0] for desc in cursor.description]
    sga_df = pd.DataFrame(sga_results, columns=sga_columns)
    sga_df.to_csv(os.path.join(test_results_dir, "sga_memory_usage.csv"), index=False)
    
    # Sprawdzenie efektywności ustawienia parametrów PGA
    cursor.execute("SELECT * FROM V$PGA_TARGET_ADVICE")
    pga_results = cursor.fetchall()
    pga_columns = [desc[0] for desc in cursor.description]
    pga_df = pd.DataFrame(pga_results, columns=pga_columns)
    pga_df.to_csv(os.path.join(test_results_dir, "pga_target_advice.csv"), index=False)
    
    # Sprawdzenie użycia pamięci przez In-Memory Column Store
    cursor.execute("SELECT * FROM V$INMEMORY_AREA")
    in_memory_results = cursor.fetchall()
    in_memory_columns = [desc[0] for desc in cursor.description]
    in_memory_df = pd.DataFrame(in_memory_results, columns=in_memory_columns)
    in_memory_df.to_csv(os.path.join(test_results_dir, "in_memory_area_usage.csv"), index=False)
    
    # Sprawdzenie dynamicznych komponentów pamięci
    cursor.execute("SELECT * FROM V$MEMORY_DYNAMIC_COMPONENTS")
    memory_dynamic_results = cursor.fetchall()
    memory_dynamic_columns = [desc[0] for desc in cursor.description]
    memory_dynamic_df = pd.DataFrame(memory_dynamic_results, columns=memory_dynamic_columns)
    memory_dynamic_df.to_csv(os.path.join(test_results_dir, "memory_dynamic_components.csv"), index=False)
    
    # Sprawdzenie statystyk na poziomie sesji dla In-Memory
    session_stats = [
        "IM scan rows optimized",
        "IM scan rows projected",
        "IM scan rows",
        "IM scan rows valid",
        "IM scan CUs no memcompress",
        "IM scan CUs memcompress for *",
        "IM scan CUs columns accessed",
        "IM scan CUs invalid or missing revert to on disk extent",
        "IM scan CUs pruned",
        "IM scan segments minmax eligible",
        "IM scan segments disk",
        "IM scan CUs predicates applied",
        "IM scan CUs predicates optimized",
        "IM scan CUs predicates received",
        "IM scan EU rows",
        "IM scan EUs no memcompress",
        "IM scan EUs memcompress for *",
        "IM scan EUs columns accessed",
        "IM scan EUs columns decompressed",
        "IM scan EU bytes in-memory",
        "IM scan EU bytes uncompressed",
        "IM scan EUs columns theoretical max",
        "IM scan EUs split pieces",
        "IM populate segments requested",
        "table scan disk IMC fallback",
        "table scan disk non-IMC rows gotten",
        "table scans (IM)",
        "session logical reads - IM"
    ]
    
    # Tworzenie zapytania do pobrania statystyk sesji
    stats_placeholders = "', '".join(session_stats)
    session_stats_query = f"""
        SELECT n.name, SUM(s.value) as total_value
        FROM v$sesstat s
        JOIN v$statname n ON s.statistic# = n.statistic#
        WHERE n.name IN ('{stats_placeholders}')
        GROUP BY n.name
    """
    
    cursor.execute(session_stats_query)
    session_results = cursor.fetchall()
    session_columns = [desc[0] for desc in cursor.description]
    session_df = pd.DataFrame(session_results, columns=session_columns)
    session_df.to_csv(os.path.join(test_results_dir, "session_level_statistics.csv"), index=False)
    print(f"Session level statistics saved to '{os.path.join(test_results_dir, 'session_level_statistics.csv')}'.")
    
    cursor.close()

def restart_database():
    container_name = "oracle19"  # Nazwa kontenera Oracle

    try:
        print("Restarting the database container...")
        # Zatrzymanie kontenera
        subprocess.run(["docker", "stop", container_name], check=True)
        
        # Sprawdzenie, czy kontener został zatrzymany
        while True:
            result = subprocess.run(["docker", "ps", "-f", f"name={container_name}", "--format", "{{.Status}}"], capture_output=True, text=True)
            if "Exited" in result.stdout:
                print("Container is stopped.")
                break
            else:
                print("Waiting for the container to stop...")
                time.sleep(5)  # Czekaj 5 sekund przed ponownym sprawdzeniem

        # Uruchomienie kontenera
        subprocess.run(["docker", "start", container_name], check=True)
        print("Database container started successfully.")
        
        # Pętla sprawdzająca, czy baza danych jest uruchomiona
        while True:
            try:
                connection.ping()
                print("Database is up and running.")
                break
            except oracledb.DatabaseError as e:
                print("Waiting for the database to start...")
                time.sleep(5)  # Czekaj 5 sekund przed ponownym sprawdzeniem
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while restarting the database container: {e}")
    except Exception as e:
        print(f"An error occurred while restarting the database: {e}")

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
        # "select1_deoptimized": {
        #     "script": load_sql_script("./transactions/select1_deoptimized.sql"),
        #     "params": {
        #         "min_amount": 0,
        #         "registration_number_pattern": "%",
        #         "parking_id": 1,
        #         "min_date": "2020-12-12 12:12:12"
        #     }
        # },
        "select2": {
            "script": load_sql_script("./transactions/select2_bez_timestamp.sql"),
            "params": {
                "START_DATE": datetime(2020, 5, 1, 12, 12, 12),
                "END_DATE": datetime(2020, 5, 12, 12, 12, 12)
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
        # "insert_alone": {
        #     "script": load_sql_script("./transactions/insert_alone.sql"),
        #     "params": {
        #         "PARKING_ID": 10,
        #         "USER_ID": 10,
        #         "new_end_date": "2022-12-12 18:12:12",
        #         "new_start_date": "2022-12-12 06:12:12",
        #         "reference_date": "2020-11-27"
        #     }
        # },
        "delete": {
            "script": load_sql_script("./transactions/delete.sql"),
            "params": {
                "discard_date_min": "2021-12-1 12:12:12",
                "discard_date_max": "2021-12-5 12:12:12"
            }
        },
        # "delete_deoptimized": {
        #     "script": load_sql_script("./transactions/delete_deoptimized.sql"),
        #     "params": {
        #         "discard_date_min": "2021-12-1 12:12:12",
        #         "discard_date_max": "2021-12-5 12:12:12"
        #     }
        # },
        # "update": {
        #     "script": load_sql_script("./transactions/update.sql"),
        #     "params": {
        #         "p_min_age": 18,
        #         "p_color_toyota": "Red",
        #         "p_color_bmw": "Black",
        #         "p_color_honda": "Green",
        #         "p_days_since_reservation": 30,
        #         "p_color_admin": "Gold",
        #         "p_color_default": "White"
        #     }
        # }
    }
    try:
        remove_indexes()
    except Exception as e:
        print(f"Indexes removal failed, probably they don't exist: {e}")
        pass
    
    #! Indexes
    remove_inmemory_compression("Reservation")
    remove_inmemory_compression("ParkingUser")
    remove_inmemory_compression("ParkingSpot")
    run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="NORMAL")
    
    
    set_inmemory_compression("ParkingUser", "")
    set_inmemory_compression("ParkingSpot", "")
    set_inmemory_compression("Reservation", "")
    run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="INMEMORY")
    
    

    # Test 1: Brak kompresji
    # remove_inmemory_compression("Reservation")
    # remove_inmemory_compression("ParkingUser")
    # remove_inmemory_compression("ParkingSpot")
    # run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="NO_compression_with_indexes")
    # query_memory_usage("NO_compression_with_indexes")

    # # Test 2: Kompresja danych High Capacity
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR CAPACITY HIGH")
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR CAPACITY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="MEMCOMPRESS_CAPACITY_HIGH_with_indexes")
    # query_memory_usage("MEMCOMPRESS_CAPACITY_HIGH_with_indexes")
    
    # # Test : Kompresja danych Low Capacity
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR CAPACITY LOW")
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR CAPACITY LOW")
    # run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="MEMCOMPRESS_CAPACITY_LOW_with_indexes")
    # query_memory_usage("MEMCOMPRESS_CAPACITY_LOW_with_indexes")
    
    # remove_inmemory_compression("Reservation")
    # remove_inmemory_compression("ParkingUser")
    # remove_inmemory_compression("ParkingSpot")

    # # Test 3: QUERY PRIORITY Query High
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY HIGH")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="MEMCOMPRESS_HIGH_with_indexes")
    # query_memory_usage("MEMCOMPRESS_HIGH_with_indexes")
    
    # reset_database()
    
    # # Test 4: QUERY PRIORITY Query Low
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY LOW")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY LOW")
    # run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="MEMCOMPRESS_LOW_with_indexes")
    # query_memory_usage("MEMCOMPRESS_LOW_with_indexes")
    
    # reset_database()
    
    # # Test 5: QUERY PRIORITY Query High + PRIORITY HIGH
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY HIGH")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY HIGH")
    # set_inmemory_compression("Reservation", "PRIORITY HIGH")
    # set_inmemory_compression("ParkingUser", "PRIORITY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="MEMCOMPRESS_HIGH_PRIORITY_HIGH_with_indexes")
    # query_memory_usage("MEMCOMPRESS_HIGH_PRIORITY_HIGH_with_indexes")
    
    # reset_database()
    
    # # Test 6: QUERY PRIORITY Query LOW + PRIORITY HIGH
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY LOW")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY LOW")
    # set_inmemory_compression("Reservation", "PRIORITY HIGH")
    # set_inmemory_compression("ParkingUser", "PRIORITY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=True, filename_prefix="MEMCOMPRESS_LOW_PRIORITY_HIGH_with_indexes")
    # query_memory_usage("MEMCOMPRESS_LOW_PRIORITY_HIGH_with_indexes")
    
    # reset_database()
    
    # remove_inmemory_compression("Reservation")
    # remove_inmemory_compression("ParkingUser")
    # remove_inmemory_compression("ParkingSpot")
    
    # #! No Indexes
    # #Test 1: Brak kompresji
    # run_load_test(test_queries, iterations=5, indexes=False, filename_prefix="NO_compression_NO_indexes")
    # query_memory_usage("NO_compression_NO_indexes")
    
    # reset_database()
    
    # #Test 2: Kompresja danych High Capacity
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR CAPACITY HIGH")
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR CAPACITY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=False, filename_prefix="MEMCOMPRESS_CAPACITY_HIGH_no_indexes")
    # query_memory_usage("MEMCOMPRESS_CAPACITY_HIGH_no_indexes")
    
    # reset_database()

    # # Test 3: Kompresja danych Low Capacity
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR CAPACITY LOW")
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR CAPACITY LOW")
    # run_load_test(test_queries, iterations=5, indexes=False, filename_prefix="MEMCOMPRESS_CAPACITY_LOW_no_indexes")
    # query_memory_usage("MEMCOMPRESS_CAPACITY_LOW_no_indexes")
    
    # reset_database()

    # remove_inmemory_compression("Reservation")
    # remove_inmemory_compression("ParkingUser")
    # remove_inmemory_compression("ParkingSpot")
    
    # reset_database()

    # # Test 4: QUERY PRIORITY Query High
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY HIGH")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=False, filename_prefix="MEMCOMPRESS_HIGH_no_indexes")
    # query_memory_usage("MEMCOMPRESS_HIGH_no_indexes")
    
    # reset_database()

    # # Test 5: QUERY PRIORITY Query Low
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY LOW")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY LOW")
    # run_load_test(test_queries, iterations=5, indexes=False, filename_prefix="MEMCOMPRESS_LOW_no_indexes")
    # query_memory_usage("MEMCOMPRESS_LOW_no_indexes")

    # Test 6: QUERY PRIORITY Query High + PRIORITY HIGH
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY HIGH")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY HIGH")
    # set_inmemory_compression("Reservation", "PRIORITY HIGH")
    # set_inmemory_compression("ParkingUser", "PRIORITY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=False, filename_prefix="MEMCOMPRESS_HIGH_PRIORITY_HIGH_no_indexes")
    # query_memory_usage("MEMCOMPRESS_HIGH_PRIORITY_HIGH_no_indexes")
    
    # reset_database()

    # # Test 7: QUERY PRIORITY Query LOW + PRIORITY HIGH
    # set_inmemory_compression("Reservation", "MEMCOMPRESS FOR QUERY LOW")
    # set_inmemory_compression("ParkingUser", "MEMCOMPRESS FOR QUERY LOW")
    # set_inmemory_compression("Reservation", "PRIORITY HIGH")
    # set_inmemory_compression("ParkingUser", "PRIORITY HIGH")
    # run_load_test(test_queries, iterations=5, indexes=False, filename_prefix="MEMCOMPRESS_LOW_PRIORITY_HIGH_no_indexes")
    # query_memory_usage("MEMCOMPRESS_LOW_PRIORITY_HIGH_no_indexes")
    
    # reset_database()

    # remove_inmemory_compression("Reservation")
    # remove_inmemory_compression("ParkingUser")
    # remove_inmemory_compression("ParkingSpot")

    connection.close()