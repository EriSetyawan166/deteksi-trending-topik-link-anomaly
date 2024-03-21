import os
import pandas as pd
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

def adjust_timestamp(df):
    """
    Mengubah format waktu pada dataframe.

    Args:
        df (pandas.DataFrame): Dataframe yang akan diubah format waktunya.

    Returns:
        pandas.DataFrame: Dataframe dengan format waktu yang sudah diubah.
    """

    df['created_at'] = pd.to_datetime(
        df['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    df['created_at'] = df['created_at'] + pd.DateOffset(hours=7)

    return df


def selection_attribute(df):
    """
    Seleksi atribut pada dataframe.

    Args:
        df (pandas.DataFrame): Dataframe yang akan dipilih atributnya.

    Returns:
        pandas.DataFrame: Dataframe dengan atribut yang sudah dipilih.
    """

    df_selected = df[['created_at', 'username', 'full_text']]

    df_selected = df_selected.rename(columns={
        'created_at': 'time',
        'username': 'user_tweet',
        'full_text': 'tweet'
    })

    df_selected['jumlah_mention'] = df_selected['tweet'].str.count('@')

    df_selected['id_user_mentioned'] = df_selected['tweet'].str.findall(
        '@(\w+)').apply(lambda x: ', '.join(x))

    return df_selected

def replace_slangwords(tweet, cursor):
    cursor.execute("SELECT kata_tidak_baku, kata_baku FROM slangword")
    slangwords = cursor.fetchall()

    # Pisahkan tweet menjadi kata-kata
    words = tweet.split()

    # Iterasi setiap kata
    for i in range(len(words)):
        for slangword in slangwords:
            if slangword[0] == words[i]:
                words[i] = slangword[1]

    # Gabungkan kata-kata menjadi tweet baru
    new_tweet = ' '.join(words)
    return new_tweet


def preprocess_csv(directory):
    """
    Melakukan preprocessing pada file CSV dalam suatu direktori.

    Args:
        directory (str): Direktori tempat file CSV disimpan.

    Returns:
        bool: True jika preprocessing berhasil dilakukan dan file baru disimpan, False jika file sudah dipreprocessed sebelumnya.
    """
    
    connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
    file_list = os.listdir(directory)

    latest_file = max(file_list)
    # print(latest_file)

    preprocessed_file_name = latest_file.replace('.csv', '-preprocessed.csv')

    if not os.path.exists(os.path.join('tweets-data-preprocessed', preprocessed_file_name)):

        df_original = pd.read_csv(os.path.join(directory, latest_file))

        df_adjusted = adjust_timestamp(df_original)

        # Filter baris berdasarkan kolom 'full_text' yang mengandung karakter "@"
        df_filtered = df_adjusted[df_adjusted['full_text'].str.contains('@')]

        # Seleksi atribut
        df_selected = selection_attribute(df_filtered)

        # Mengubah teks di dalam kolom 'tweet' menjadi lowercase
        df_selected['tweet'] = df_selected['tweet'].str.lower()

        cursor = connection.cursor()
        df_selected['tweet'] = df_selected['tweet'].apply(lambda x: replace_slangwords(x, cursor))
        # Urutkan berdasarkan kolom 'created_at' dari waktu terlama ke terbaru
        df_sorted = df_selected.sort_values(by='time', ascending=True)
        df_sorted.to_csv(os.path.join(
            'tweets-data-preprocessed', preprocessed_file_name), index=False)
        cursor.close()
        connection.close()

        return True
    else:
        return False


def main():
    directory = 'tweets-data/'
    preprocess_csv(directory)


if __name__ == "__main__":
    main()
