import os
import pandas as pd
import re
from dotenv import load_dotenv
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from .db_operation import ambil_data_kotor, ambil_kamus_slangword, masukan_data_hasil_preprocessed
from .multiprocessing_manager import PoolManager
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import datetime
from functools import lru_cache
import multiprocessing
import logging
from tqdm import tqdm
from flask_socketio import emit
from app import socketio
import time
import traceback


load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


url_pattern = re.compile(r'https?://\S+|www\.\S+')
mention_pattern = re.compile(r'@\w+')
hashtag_pattern = re.compile(r'#\w+')
non_alphabet_pattern = re.compile(r'[^a-zA-Z\s]')

factory = StemmerFactory()
stemmer = factory.create_stemmer()


@lru_cache(maxsize=10000) 
def cached_stem(word):
    return stemmer.stem(word)


def adjust_timestamp(time_input):
    """
    Mengubah format waktu dari string ke string format lain.

    Args:
        time_str (str): String waktu yang akan diubah formatnya.

    Returns:
        str: Waktu dengan format baru sebagai string.
    """
    if isinstance(time_input, datetime.datetime):
        dt = time_input
    else:
        original_format = '%Y-%m-%d %H:%M:%S%z'
        try:
            dt = datetime.datetime.strptime(time_input, original_format)
        except ValueError as e:
            logging.error(f"Error parsing datetime from string: {e}")
            raise

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
    slang_dict = {slang: baku for _, baku, slang in slangwords}

    words = tweet.split()

    words = [slang_dict.get(word, word) for word in words]

    return ' '.join(words)


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
    words = tweet.split()
    cleaned_words = [stopword_remover.remove(word) for word in words]
    tweet_clean = ' '.join(cleaned_words)
    return tweet_clean


def remove_urls(tweet):
    """
    Menghapus URL dari teks tweet.

    Args:
        tweet (str): Teks tweet yang akan dihapus URL-nya.

    Returns:
        str: Teks tweet tanpa URL.
    """

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

    # Mengganti karakter selain a-z dengan string kosong
    tweet_clean = re.sub(non_alphabet_pattern, '', tweet)

    return tweet_clean


def stem_text(text):

    words = text.split()
    stemmed_words = [cached_stem(word) for word in words]
    return ' '.join(stemmed_words)


def worker(data_chunk, slangwords, progress_queue, start_time, total_data):
    processed_chunk = []
    additional_data_chunk = []

    for data in tqdm(data_chunk, desc="Processing", position=0):
        try:
            if '@' in data[3]:
                jumlah_mention = data[3].count('@')
                id_user_mentioned = re.findall(r'(@\w+)', data[3])
                time_change = adjust_timestamp(data[1])
                text = data[3].lower()
                text = remove_urls(text)
                text = remove_mentions(text)
                text = remove_hashtags(text)
                text = remove_non_alphabet(text)
                text = remove_extra_spaces(text)
                text = replace_slangwords(text, slangwords)
                text = remove_stopwords(text)
                text = stem_text(text)
                additional_data_chunk.append(
                    (data[0], time_change, data[2], jumlah_mention, ','.join(id_user_mentioned)))
                processed_chunk.append(
                    (data[0], time_change, data[2], text, jumlah_mention, ','.join(id_user_mentioned)))
        except Exception as e:
            logging.error(f"Error processing data with ID {data[0]}: {e}")
            logging.error(traceback.format_exc())
        finally:
            progress_queue.put(1)

    return processed_chunk, additional_data_chunk


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
    num_workers = multiprocessing.cpu_count()
    pool = PoolManager.create_pool()
    chunk_size = len(datas) // num_workers + 1
    data_chunks = [datas[i:i + chunk_size]
                   for i in range(0, len(datas), chunk_size)]

    manager = multiprocessing.Manager()
    progress_queue = manager.Queue()

    logging.info(f'Total chunks: {len(data_chunks)}, Chunk size: {chunk_size}')

    results = []
    start_time = time.time()
    for chunk in data_chunks:
        result = pool.apply_async(worker, args=(
            chunk, slangword, progress_queue, start_time, len(datas)))
        results.append(result)

    pool.close()

    total_progress = 0
    total_data = len(datas)

    with tqdm(total=total_data, desc="Overall Progress") as pbar:
        while total_progress < total_data:
            progress_queue.get()
            total_progress += 1
            pbar.update(1)

            # Calculate ETA
            elapsed_time = time.time() - start_time
            eta_seconds = elapsed_time / total_progress * \
                (total_data - total_progress) if total_progress > 0 else 0
            eta = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))

            # Emit progress to the client
            socketio.emit('progress_cleansing_stemming', {
                'current': total_progress,
                'total': total_data,
                'eta': eta
            })

    pool.join()

    processed_data = []
    additional_data = []
    for result in results:
        chunk_processed_data, chunk_additional_data = result.get()
        processed_data.extend(chunk_processed_data)
        additional_data.extend(chunk_additional_data)
    PoolManager.terminate_pool()
    return processed_data


def main():
    data = ambil_data_kotor()
    preprocessing = preprocess(data)
    masukan_data_hasil_preprocessed(preprocessing)


if __name__ == "__main__":
    main()


def main():
    directory = 'tweets-data/'
    # preprocess_csv(directory)
    data = ambil_data_kotor()
    preprocessing = preprocess(data)

    masukan_data_hasil_preprocessed(preprocessing)


if __name__ == "__main__":
    main()
