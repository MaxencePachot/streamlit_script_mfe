import mysql.connector

# mariadb Docker account details
host = "secret"
user = "secret"
password = "secret"
database = "E_COMMERCE"
port = 3306

# Create mariadb connection
def get_mariadb_connection():
    try:
        print("Connection in progress")
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        print("------------------------------------------")  
        print("Successfully connected to mariadb!")
        for i in range (2) : 
            print("------------------------------------------")
        return conn
    except Exception as e:
        print("------------------------------------------")  
        print("Error connecting to mariadb: ", e)
        return None