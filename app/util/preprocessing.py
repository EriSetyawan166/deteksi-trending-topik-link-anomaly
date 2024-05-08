import os
import pandas as pd
import re
from dotenv import load_dotenv
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from db_operation import ambil_data_kotor, ambil_kamus_slangword, masukan_data_hasil_preprocessed
import datetime

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

def adjust_timestamp(time_str):
    """
    Mengubah format waktu dari string ke string format lain.

    Args:
        time_str (str): String waktu yang akan diubah formatnya.

    Returns:
        str: Waktu dengan format baru sebagai string.
    """
    # Parse the string to datetime object
    original_format = '%a %b %d %H:%M:%S %z %Y'
    dt = datetime.datetime.strptime(time_str, original_format)

    # Tambahkan 7 jam
    adjusted_dt = dt + datetime.timedelta(hours=7)

    # Format datetime sebagai string
    new_format = '%Y-%m-%d %H:%M:%S'
    return adjusted_dt.strftime(new_format)

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

def replace_slangwords(tweet, slangwords):
    """
    Mengubah kata tidak baku menjadi kata baku dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan diubah katanya dari tidak baku menjadi baku.

    Returns:
        str: Teks tweet tanpa URL.
    """
    words = tweet.split()
    for i in range(len(words)): 
        for slangword in slangwords:
            if slangword[2] == words[i]:
                words[i] = slangword[1]

    result = ' '.join(words)
    return result

def remove_stopwords(tweet):
    """
    Menghapus stopword dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan dihapus stopwordnya.

    Returns:
        str: Teks tweet tanpa stopwords.
    """
    factory = StopWordRemoverFactory()
    stopword_remover = factory.create_stop_word_remover()
    tweet_clean = stopword_remover.remove(tweet)
    return tweet_clean

def remove_urls(tweet):
    """
    Menghapus URL dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan dihapus URL-nya.

    Returns:
        str: Teks tweet tanpa URL.
    """
    # Pola regex untuk mendeteksi URL
    url_pattern = r'https?://\S+|www\.\S+'

    # Mengganti URL dengan string kosong
    tweet_clean = re.sub(url_pattern, '', tweet)

    return tweet_clean

def remove_mentions(tweet):
    """
    Menghilangkan mention dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan dihilangkan mention-nya.

    Returns:
        str: Teks tweet tanpa mention.
    """
    # Pola regex untuk mendeteksi mention
    mention_pattern = r'@\w+'

    # Mengganti mention dengan string kosong
    tweet_clean = re.sub(mention_pattern, '', tweet)

    return tweet_clean

def remove_hashtags(tweet):
    """
    Menghilangkan hashtag dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan dihilangkan hashtag-nya.

    Returns:
        str: Teks tweet tanpa hashtag.
    """
    # Pola regex untuk mendeteksi hashtag
    hashtag_pattern = r'#\w+'

    # Mengganti hashtag dengan string kosong
    tweet_clean = re.sub(hashtag_pattern, '', tweet)

    return tweet_clean

def remove_non_alphabet(tweet):
    """
    Menghilangkan karakter selain a-z dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan dihilangkan karakter selain a-z.

    Returns:
        str: Teks tweet hanya mengandung karakter a-z.
    """
    # Pola regex untuk mendeteksi karakter selain a-z
    non_alphabet_pattern = r'[^a-zA-Z\s]'

    # Mengganti karakter selain a-z dengan string kosong
    tweet_clean = re.sub(non_alphabet_pattern, '', tweet)

    return tweet_clean

def remove_extra_spaces(tweet):
    """
    Menghilangkan spasi yang berjarak lebih dari satu spasi dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan dihilangkan spasi berjarak.

    Returns:
        str: Teks tweet tanpa spasi yang berjarak lebih dari satu spasi.
    """
    # Mengganti spasi yang berjarak lebih dari satu spasi menjadi satu spasi
    tweet_clean = ' '.join(tweet.split())

    return tweet_clean

def preprocess(datas):
    slangword = ambil_kamus_slangword()
    # print(slangword)

    processed_data = []
    for data in datas:
        # Filter baris berdasarkan kolom 'full_text' yang mengandung karakter "@"
        if '@' in data[3]:
            # Menghitung jumlah "@"
            jumlah_mention = data[3].count('@')

            # Ekstrak semua user yang disebutkan
            id_user_mentioned = re.findall(r'(@\w+)', data[3])

            time = adjust_timestamp(data[1])
            
            # Mengubah teks menjadi lowercase
            text = data[3].lower()

            # mengubah slangword
            text = replace_slangwords(text, slangword)

            #Menghapus stopword
            text = remove_stopwords(text)

            # Menghapus url
            text = remove_urls(text)

            # Menghapus mention
            text = remove_mentions(text)

            # Menghapus hastags
            text = remove_hashtags(text)

            # Menghapus huruf selain a-z
            text = remove_non_alphabet(text)
            
            # Menghapus spasi berjarak
            text = remove_extra_spaces(text)

            processed_data.append((data[0], time, data[2], text, jumlah_mention, ','.join(id_user_mentioned)))
        else:
            continue
    return processed_data
    

def main():
    # directory = 'tweets-data/'
    # preprocess_csv(directory)
    data = ambil_data_kotor()
    
    # print(data)
    preprocessing = preprocess(data)
    
    masukan_data_hasil_preprocessed(preprocessing)
    


if __name__ == "__main__":
    main()
