import mysql.connector


def insert_slangwords(connection, file_path):
    """
    Fungsi untuk memasukkan kata slang ke dalam basis data dari file teks.

    Parameter:
    - connection (Connection): Objek koneksi ke database.
    - file_path (str): Jalur ke file teks yang berisi pasangan kata tidak baku dan kata baku.

    Tidak ada nilai yang dikembalikan, tetapi akan mencetak status atau kesalahan ke konsol.
    """
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
    """
    Fungsi untuk menutup koneksi ke basis data.

    Parameter:
    - connection (Connection): Objek koneksi ke database yang akan ditutup.

    Tidak ada nilai yang dikembalikan, tetapi akan mencetak status ke konsol.
    """
    connection.close()
    print("Koneksi ditutup.")


connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="deteksi_trending_topik"
)

file_path = "../../kamus/slangword.txt"

insert_slangwords(connection, file_path)

close_connection(connection)
