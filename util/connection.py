import mysql.connector

def connect_to_database(host, user, password, database):
    try:
        # Membuat koneksi ke database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Koneksi ke database berhasil!")
        return connection
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

def close_connection(connection):
    try:
        # Menutup koneksi ke database
        if connection.is_connected():
            connection.close()
            print("Koneksi ditutup.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")

def main():
    connection = connect_to_database("localhost", "root", "", "deteksi_trending_topik")
    close_connection(connection)

if __name__ == "__main__":
    main()