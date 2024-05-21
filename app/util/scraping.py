import pandas as pd
import subprocess
import mysql.connector
import os
import subprocess
from dotenv import load_dotenv


def scrape_tweets(start_date, end_date, search_query, tweet_limit, token, tab):
    # Command untuk menjalankan tweet-harvest
    # command = f'npx tweet-harvest@latest -f {start_date} -to {end_date} -s "{search_query}" -l {tweet_limit} -t "{token}" --tab "{tab}"'
    command = f'npx tweet-harvest@latest -f {start_date} -to {end_date} -s "{search_query}" -t "{token}" --tab "{tab}"'

    try:
        # Jalankan command dengan subprocess.Popen
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Membaca output secara real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        # Check jika ada error
        stderr = process.communicate()[1]
        if stderr:
            print(stderr)
        return
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def insert_data_to_database(database_connection):
    try:
        # Baca file CSV
        directory = 'tweets-data/'
        file_list = os.listdir(directory)
        latest_file = max(file_list)
        csv_file = os.path.join(directory, latest_file)
        df = pd.read_csv(csv_file)

        # Mengganti nilai NaN dengan nilai default
        df.fillna('', inplace=True)

        # Membuat kursor untuk koneksi database
        cursor = database_connection.cursor()

        # Iterasi setiap baris data dari dataframe CSV
        for index, row in df.iterrows():
            # Query untuk memasukkan data ke dalam tabel
            query = "INSERT INTO dataset_twitter (conversation_id_str, created_at, favorite_count, full_text, id_str, image_url, in_reply_to_screen_name, lang, location, quote_count, reply_count, retweet_count, tweet_url, user_id_str, username) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            # Menyiapkan nilai untuk dimasukkan ke dalam query
            values = (
                row['conversation_id_str'], row['created_at'], row['favorite_count'], row['full_text'], row['id_str'],
                row['image_url'], row['in_reply_to_screen_name'], row['lang'], row['location'], row['quote_count'],
                row['reply_count'], row['retweet_count'], row['tweet_url'], row['user_id_str'], row['username']
            )

            # Menjalankan query untuk memasukkan data ke dalam database
            cursor.execute(query, values)

        # Commit perubahan ke dalam database
        database_connection.commit()
        print("Data berhasil dimasukkan ke dalam database.")
    except Exception as e:
        print(f"Error: {e}")
        database_connection.rollback()


def main():
    load_dotenv()
    token = os.getenv("TOKEN")
    # scrape_tweets("25-03-2024", "31-03-2024", "pemilu", 10, token, "TOP")
    scrape_tweets("25-03-2024", "26-03-2024", "pemilu", 1000, token, "LATEST")
    # insert_data_to_database()


if __name__ == "__main__":
    main()
