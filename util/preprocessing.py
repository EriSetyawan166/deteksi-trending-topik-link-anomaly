import os
import pandas as pd

def preprocess_csv(directory):
    # Mendapatkan daftar file CSV dalam direktori
    file_list = os.listdir(directory)

    # Tentukan file terbaru berdasarkan nama file
    latest_file = max(file_list)

    # Nama file hasil preprocessed
    preprocessed_file_name = latest_file.replace('.csv', '-preprocessed.csv')

    if not os.path.exists(os.path.join('tweets-data-preprocessed', preprocessed_file_name)):
        # Baca file CSV terbaru
        df_original = pd.read_csv(os.path.join(directory, latest_file))

        # Parsing waktu dari format string
        df_original['created_at'] = pd.to_datetime(df_original['created_at'], format='%a %b %d %H:%M:%S %z %Y')

        # Tambahkan 7 jam ke waktu
        df_original['created_at'] = df_original['created_at'] + pd.DateOffset(hours=7)

        # Filter baris berdasarkan kolom 'full_text' yang mengandung karakter "@"
        df_filtered = df_original[df_original['full_text'].str.contains('@')]

        # Simpan hasil filter ke dalam file CSV baru dengan nama yang jelas
        df_filtered.to_csv(os.path.join('tweets-data-preprocessed', preprocessed_file_name), index=False)

        return True
    else:
        return False

def main():
    directory = 'tweets-data/'
    preprocess_csv(directory)

if __name__ == "__main__":
    main()
