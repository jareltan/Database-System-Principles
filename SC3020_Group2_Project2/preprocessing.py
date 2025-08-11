import psycopg2

def db_connect_and_obtain_qep(db_connection_configurations):
    
    # Establish connection with PostgreSQL server with login credentials keyed in by user on GUI
    connection = psycopg2.connect(
        host = db_connection_configurations["host"],
        port = db_connection_configurations["port"],
        database = db_connection_configurations["database"],
        user = db_connection_configurations["user"],
        password = db_connection_configurations["password"]
    )
    
    input_sql_query = db_connection_configurations['query']
    
    # Create cursor object to facilitate execution of SQL queries via connection
    cursor = connection.cursor()
    
    # Execute EXPLAIN ANALYSE on SQL query to get JSON output showing QEP and other statistics 
    cursor.execute(f"EXPLAIN (FORMAT JSON, ANALYZE) {input_sql_query}")
    result = cursor.fetchone()[0] 
    # print(result)
    
    cursor.close()
    connection.close()
    
    # Return QEP 
    return result[0]['Plan']



