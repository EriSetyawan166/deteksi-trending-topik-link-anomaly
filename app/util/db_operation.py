from .db_manager import DatabaseManager
import os
import pandas as pd
import mysql

db_manager = DatabaseManager()


def masukan_data(csv_path):
    database_connection = DatabaseManager().get_connection()
    try:
        df = pd.read_csv(csv_path)
        df.fillna('', inplace=True)
        cursor = database_connection.cursor()
        for index, row in df.iterrows():

            query = "INSERT INTO dataset_twitter (conversation_id_str, created_at, favorite_count, full_text, id_str, image_url, in_reply_to_screen_name, lang, location, quote_count, reply_count, retweet_count, tweet_url, user_id_str, username) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            values = (
                row['conversation_id_str'], row['created_at'], row['favorite_count'], row['full_text'], row['id_str'],
                row['image_url'], row['in_reply_to_screen_name'], row['lang'], row['location'], row['quote_count'],
                row['reply_count'], row['retweet_count'], row['tweet_url'], row['user_id_str'], row['username']
            )

            cursor.execute(query, values)

        database_connection.commit()
        print("Data berhasil dimasukkan ke dalam database.")
    except Exception as e:
        print(f"Error: {e}")
        database_connection.rollback()
    finally:
        cursor.close()
        database_connection.close()


def ambil_data_kotor():
    connection = db_manager.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, created_at, username, full_text FROM dataset_twitter")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def ambil_kamus_slangword():
    connection = db_manager.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM slangword")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def ambil_data_bersih():
    connection = db_manager.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dataset_preprocessed ORDER BY time ASC")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def masukan_data_hasil_preprocessed(data_hasil_preprocessed):
    connection = db_manager.get_connection()
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO dataset_preprocessed (id, time, user_twitter, tweet, jumlah_mention, id_user_mentioned)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        # data_bersih adalah list tuples
        cursor.executemany(query, data_hasil_preprocessed)
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        cursor.close()


def main():
    csv_path = "tweets-data\pemilu_21-03-2024_14-02-41.csv"
    masukan_data(csv_path)


if __name__ == "__main__":
    main()
