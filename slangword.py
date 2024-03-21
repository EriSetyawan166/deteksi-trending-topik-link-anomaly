import mysql.connector

def insert_slangwords(connection, file_path):
    try:
        cursor = connection.cursor()

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip().split('\t')
                if len(line) >= 2:
                    kata_tidak_baku, kata_baku = line[0], line[1]
                    query = "INSERT INTO slangword (kata_tidak_baku, kata_baku) VALUES (%s, %s)"
                    values = (kata_tidak_baku, kata_baku)
                    cursor.execute(query, values)
                else:
                    print(f"Ignoring invalid line: {line}")

        connection.commit()
        print("Data slangword inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()

def close_connection(connection):
    connection.close()
    print("Koneksi ditutup.")

# Connect to the database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="deteksi_trending_topik"
)

# File path to the slangword.txt file
file_path = "kamus/slangword.txt"

# Call the function to insert slangwords
insert_slangwords(connection, file_path)

# Close the database connection
close_connection(connection)
