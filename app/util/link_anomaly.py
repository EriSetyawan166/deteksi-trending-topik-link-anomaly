import math
import locale
from db_operation import ambil_data_bersih
import numpy as np

def hitung_total_mention(data):
    """
    Menghitung total jumlah mention dari dataset.

    Parameters:
        data (list of tuples/lists): Dataset yang berisi data,
            dimana salah satu kolomnya adalah jumlah_mention.

    Returns:
        int: Total jumlah mention dari semua row.
    """
    total_mention = 0
    for baris in data:
        jumlah_mention = baris[4]
        total_mention += jumlah_mention

    return total_mention


def hitung_frekuensi_mention(data, nilai_v_list):
    """
    Menghitung frekuensi mention setiap user

    Parameters:
        data (list of tuples/lists): Dataset yang berisi data,
            dimana salah satu kolomnya adalah jumlah_mention.
        nilai_v_list (tuple) : kumpulan user

    Returns:
        int: Total frekuensi mention setiap user
    """
    jumlah_mention = {mention: 0 for mention in nilai_v_list}

    for baris in data:
        mentions = baris[5].split(',')
        for mention in mentions:
            if mention in jumlah_mention:
                jumlah_mention[mention] += 1

    return jumlah_mention


def hitung_probabilitas_mention(n, m, k, alpha=0.5, beta=0.5):
    """
    Fungsi untuk menghitung probabilitas suatu mention berdasarkan rentang waktu.

    Parameters:
        n (int): Jumlah tweet pada rentang waktu.
        m (int): Jumlah mention pada rentang waktu.
        k (int): Jumlah mention pada tweet.
        alpha (float): Parameter alpha untuk perhitungan probabilitas.
        beta (float): Parameter beta untuk perhitungan probabilitas.
        j (int): Indeks ke- dari suatu mention.

    Returns:
        float: Probabilitas suatu mention.
    """
    hasil = 1

    for j in range(n):
        hasil *= ((m + beta + j) / (n + m + alpha + beta + j))

    hasil *= ((n + alpha) / (m + k + beta))
    return hasil


def hitung_probabilitas_mention_user(mu, m, gamma=0.5):
    """
    Fungsi untuk menghitung probabilitas mention yang mengarah ke user

    Parameters:
        mu (int): Jumlah  mention ke user.
        m (int): Jumlah keseluruhan mention pada satu training
        gamma (float): Parameter gamma untuk perhitungan probabilitas.

    Returns:
        float: Probabilitas suatu mention ke user.
    """
    hasil = ((mu) / (m + gamma))

    return hasil


def hitung_skor_link_anomaly(hasil_probabilitas_mention, hasil_probabilitas_mention_user):
    """
    Fungsi untuk menghitung skor link anomaly
    Parameters:
        hasil_probabilitas_mention (float): Jumlah probabilitas mention
        hasil_probabilitas_mention_user (float): Jumlah probabilitas mention user

    Returns:
        float: skor link anomaly tweet.
    """
    hasil = -math.log(hasil_probabilitas_mention, 10) - \
        math.log(hasil_probabilitas_mention_user, 10)

    return hasil


def hitung_selisih_waktu(waktu1, waktu2):
    """
    Menghitung selisih waktu antara dua waktu.
    Parameters: 
        waktu1 (datetime.time) : waktu pertama
        waktu2 (datetime.time) : waktu kedua

    Returns: 
        int: hasil selisih kedua waktu dalam detik
    """
    selisih = abs(waktu2 - waktu1)
    return int(selisih.total_seconds())


def hitung_agregasi_skor_link_anomaly(skor_link_anomaly, tau):
    """
    Fungsi untuk menghitung agregasi skor link anomaly
    Parameters:
        skor_link_anomaly (float): jumlah skor link anomaly
        tau (int): Ukuran window time

    Returns:
        float: agregasi skor link anomaly
    """
    hasil = 0
    for skor in skor_link_anomaly:
        hasil += skor

    hasil *= (1 / tau)
    return hasil, tau


def periksa_agregasi_diskrit(agregasi_skor_link_anomaly, threshold_burst=0.9995):
    """
    Memeriksa apakah ada nilai dalam urutan yang melebihi Threshold burst yang ditentukan.
    Mengembalikan True jika lebih dari satu nilai melebihi Threshold burst,
    jika tidak mengembalikan False.

    Parameters:
        agregasi_skor_link_anomaly (list of float): Daftar skor anomali.
        threshold_burst (float, opsional): Threshold burst untuk menentukan burst. Default adalah 0.9995.

    Returns:
        list: list data yang sudah dibersihkan
    """
    data_bersih = []
    for index, skor_list in agregasi_skor_link_anomaly:
        filtered_data = [(skor, waktu)
                         for skor, waktu in skor_list if skor > threshold_burst]
        if filtered_data:
            data_bersih.append((index, filtered_data))
        else:
            data_bersih.append((index, None))

    return data_bersih


def hitung_cost_function(cleaned_agregasi_skor_link_anomaly, p=0.3, alpha_burst=0.01):
    """
    Fungsi untuk menghitung nilai cost function
    Parameters:
        cleaned_agregasi_skor_link_anomaly (list of float): agregasi skor link anomaly yang sudah dibersihkan
        selang_waktu (int) = selang waktu kemunculan antar skor agregasi pada sequence
        p (float, opsional) = probabilitas kemunculan. default 0.3
        alpha burst (float, optional) = alpha burst. default 0.01 

    Returns:
        float: hasil cost function
    """
    list_hasil = []
    for index, score_time_list in cleaned_agregasi_skor_link_anomaly[0]:
        if score_time_list is None:
            list_hasil.append((index, None))
            continue

        transisi_state = len(score_time_list) - 1
        hasil = transisi_state * math.log((1 - p) / p)

        for score, selang_waktu in score_time_list:
            hasil += -math.log(alpha_burst *
                                math.exp(-alpha_burst * selang_waktu))

        list_hasil.append((index, hasil))

    return list_hasil


def cari_cost_function_minimum(cost_function):
    """
    Fungsi untuk mengambil nilai cost function minimum
    Parameters:
        cost_function (list of float): hasil cost function semua sequence

    Returns:
        float: cost function minimum
    """
    data_bersih = [(index, value)
                     for index, value in cost_function if value is not None]

    if data_bersih:
        min_value = min(data_bersih, key=lambda x: x[1])
        return min_value
    else:
        return None


def ambil_teks_dari_sequence(sequences, sequence_index):
    """
    Mengambil teks dari sequence yang spesifik berdasarkan indeks.

    Parameters:
        sequences (list of list): List yang berisi data per sequence.
        sequence_index (int): Indeks dari sequence yang cost function-nya paling rendah.

    Returns:
        list: List yang berisi teks dari sequence terpilih.
    """
    sequence_terpilih = sequences[sequence_index - 1]

    teks_dari_sequence = [data[3] for data in sequence_terpilih]
    return teks_dari_sequence


def link_anomaly(data, sequence=2):
    """
    Fungsi utama dari link anomaly
    parameters:
        data (path): data yang sudah dipreprocessing
    """
    data = np.array(data, dtype=object)
    sequences = []
    agregasi_skor_anomaly_per_sequence = []
    cleaned_agregasi_skor_anomaly_per_sequence = []
    total_data = len(data)

    #memecahkan data menjadi per sequence
    items_per_sequence = math.ceil(total_data / sequence)

    for i in range(0, total_data, items_per_sequence):
        index_terakhir = min(i + items_per_sequence, total_data)
        sequence_data = data[i:index_terakhir]
        sequences.append(sequence_data)

    #perulangan per sequence
    for index, sequence in enumerate(sequences):
        probabilitas_mention_user = 0
        hasil_skor_link_anomaly_bersih = []
        waktu_sebelum = sequence[0][1]
        hasil_skor_link_anomaly = []
        agregasi_skor_anomaly_per_diskrit = []
        total_data_per_sequence = len(sequence)
        total_mention = hitung_total_mention(sequence)

        #perulangan data 
        for i, data in enumerate(sequence):
            waktu_sekarang = data[1]

            #menghitung probabilitas mention
            probabilitas_mention = hitung_probabilitas_mention(
                total_data_per_sequence, total_mention, data[4])
            nilai_v = data[5]
            nilai_v_list = nilai_v.split(',')

            #menghitung probabilitas frekuensi mention
            total_mention_user = hitung_frekuensi_mention(
                sequence, nilai_v_list)

            #menghitung probabilitas mention user
            for mention in total_mention_user:
                probabilitas_mention_user += hitung_probabilitas_mention_user(
                    total_mention_user[mention], total_mention)

            #menghitung skor link anomaly
            skor_link_anomaly = hitung_skor_link_anomaly(
                probabilitas_mention, probabilitas_mention_user)
            probabilitas_mention_user = 0

            hasil_skor_link_anomaly.append(skor_link_anomaly)

            if i % 2 != 0:
                selisih = hitung_selisih_waktu(waktu_sebelum, waktu_sekarang)
                hasil_skor_link_anomaly_bersih.append(
                    [hasil_skor_link_anomaly[-2], hasil_skor_link_anomaly[-1], selisih])
                waktu_sebelum = waktu_sekarang

        #menghitung agregasi skor link anomaly
        if len(hasil_skor_link_anomaly) % 2 != 0:
            if len(hasil_skor_link_anomaly_bersih) > 0:
                element_terakhir = hasil_skor_link_anomaly[-1]
                waktu_pertama_dari_grup_terakhir = sequence[-(len(hasil_skor_link_anomaly_bersih[-1])//2 + 1)][1] if len(
                    sequence) > 1 else sequence[-1][1]
                waktu_sebelum = sequence[-1][1]
                selisih = hitung_selisih_waktu(
                    waktu_pertama_dari_grup_terakhir, waktu_sebelum)
                hasil_skor_link_anomaly_bersih[-1] = hasil_skor_link_anomaly_bersih[-1][:-1]
                hasil_skor_link_anomaly_bersih[-1].extend([element_terakhir, selisih])
            else:
                hasil_skor_link_anomaly_bersih.append([hasil_skor_link_anomaly[-1]])

        #merapihan hasil agregasi skor link anomaly
        for diskrit in hasil_skor_link_anomaly_bersih:
            ambil_skor_link_anomaly = diskrit[:-1]
            tau = diskrit[-1]
            agregasi_skor_anomaly_per_diskrit.append(
                hitung_agregasi_skor_link_anomaly(ambil_skor_link_anomaly, tau))

        #membuat agregasi skor anomaly per-sequence
        agregasi_skor_anomaly_per_sequence.append(
            (index+1, agregasi_skor_anomaly_per_diskrit))

    #membersihkan agregasi skor anomaly
    cleaned_agregasi_skor_anomaly_per_sequence.append(
        periksa_agregasi_diskrit(agregasi_skor_anomaly_per_sequence))
    
    #menghitung cost function
    result_cost_function = hitung_cost_function(
        cleaned_agregasi_skor_anomaly_per_sequence)

    #mengambil cost function minimum
    result_cost_function_minimum = cari_cost_function_minimum(
        result_cost_function)

    #mengambil teks dari sequence terpilih
    teks_dari_sequence_terpilih = ambil_teks_dari_sequence(
        sequences, result_cost_function_minimum[0])

    return result_cost_function_minimum, teks_dari_sequence_terpilih


def main():
    locale.setlocale(locale.LC_TIME, 'id_ID')

    data = ambil_data_bersih()

    hasil = link_anomaly(data, 10)
    print(hasil)


if __name__ == "__main__":
    main()
