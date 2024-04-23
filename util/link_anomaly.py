import pandas as pd
from io import StringIO
import math
import locale


def hitung_probabilitas_mention(n, m, k, alpha, beta):
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
    result = 1
    
    for j in range(n):
        # print(j)
        result *= round(((m + beta + j) / (n + m + alpha + beta + j)), 2)
        # print(result)

    result *= round(((n + alpha) / (m + k + beta)), 2)
    result = round(result,2)
    return result


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
    result = round(((mu) / (m + gamma)), 2)
    
   

    return result

def hitung_skor_link_anomaly(hasil_probabilitas_mention, hasil_probabilitas_mention_user):
    """
    Fungsi untuk menghitung skor link anomaly
    Parameters:
        hasil_probabilitas_mention (float): Jumlah probabilitas mention
        hasil_probabilitas_mention_user (float): Jumlah probabilitas mention user

    Returns:
        float: skor link anomaly tweet.
    """
    result = round(-math.log(hasil_probabilitas_mention, 10) - math.log(hasil_probabilitas_mention_user, 10), 2)
    
    return result

def hitung_agregasi_skor_link_anomaly(skor_link_anomaly, tau):
    """
    Fungsi untuk menghitung agregasi skor link anomaly
    Parameters:
        skor_link_anomaly (float): jumlah skor link anomaly
        tau (int): Ukuran window time

    Returns:
        float: agregasi skor link anomaly
    """
    result = 0
    for skor in skor_link_anomaly:
        result += round(skor,2)
    
    result *= round((1 / tau),2)
    # print(result)
    return result


def main():
    locale.setlocale(locale.LC_TIME, 'id_ID')
    tau = 4
    agregasi_skor_anomaly_per_diskrit = []
    temp_skor_anomaly = []

    data = """
        Id Tweet,Time,User Twitter,Tweet,k (jumlah mention),V (sekumpulan id user yang di mention)
        1,23 Juni 2016 10:26:08 AM,NHasan03,Ahok modus manipulasi kp @Fdayun @Faktababelcom,2,"{@Fdayun, @Faktababelcom}"
        2,23 Juni 2016 10:26:12 AM,Fdayun,Ahok modus pembuatan sertifikat @Faktababelcom,1,"{@Faktababelcom}"
        3,23 Juni 2016 10:26:13 AM,Faktababelcom,Jokowi natuna ratas imam bonjol @FaktaSumbarcom,1,"{@FaktaSumbarcom}"
        4,23 Juni 2016 10:26:14 AM,FaktaSumbarcom,Jokowi rapat natuna @Faktababelcom @NHasan03,2,"{@Faktababelcom, @NHasan03}"
        5,23 Juni 2016 10:26:16 AM,NHasan03,TNI jamin keamanan jokowi natuna @FaktaSumbarcom,1,"{@FaktaSumbarcom}"
        """
    # 6,23 Juni 2016 10:26:24 AM,Nurul,Ahok modus manipulasi kp @Anisahka007,1,"{@Anisahka007}"

    data_io = StringIO(data)
    df = pd.read_csv(data_io)
    df['Time'] = pd.to_datetime(df['Time'], format='%d %B %Y %I:%M:%S %p', errors='coerce')
    df = df.sort_values('Time')
    start_time = df['Time'].iloc[0]
    

    total_data = df.shape[0]

    total_mention = df['k (jumlah mention)'].sum()

    probabilitas_mention_user = 0
    
    hasil_skor_link_anomaly = []

    for index, row in df.iterrows():
        current_time = row['Time']
        probabilitas_mention = hitung_probabilitas_mention(
            total_data, total_mention, row['k (jumlah mention)'], 0.5, 0.5)
        # print(probabilitas_mention)
        # print(total_data, total_mention, row['k (jumlah mention)'])
        # print()

        nilai_v = row['V (sekumpulan id user yang di mention)']
        nilai_v_list = nilai_v.strip('{}').split(', ')

        for i in range(row['k (jumlah mention)']):
            total_mention_user = df['V (sekumpulan id user yang di mention)'].str.contains(
                nilai_v_list[i]).sum()
            # print(total_mention_user, total_mention)
            
            probabilitas_mention_user += hitung_probabilitas_mention_user(
                total_mention_user, total_mention)
            # print(probabilitas_mention_user)
            
        

        skor_link_anomaly = hitung_skor_link_anomaly(probabilitas_mention, probabilitas_mention_user)
        # print(probabilitas_mention, probabilitas_mention_user)
        # print(skor_link_anomaly)
        # print()
        
        hasil_skor_link_anomaly.append(skor_link_anomaly)

        # print(probabilitas_mention_user)
        # print()
        probabilitas_mention_user = 0

        if (current_time - start_time).total_seconds() <= tau:
            temp_skor_anomaly.append(skor_link_anomaly) 
        else:
            # print(temp_skor_anomaly)
            agregasi_skor_anomaly_per_diskrit.append(hitung_agregasi_skor_link_anomaly(temp_skor_anomaly, tau))
            temp_skor_anomaly = [skor_link_anomaly]
            start_time = current_time  
       
    if temp_skor_anomaly:
        # print(temp_skor_anomaly)
        agregasi_skor_anomaly_per_diskrit.append(hitung_agregasi_skor_link_anomaly(temp_skor_anomaly, tau))

    print(agregasi_skor_anomaly_per_diskrit)
    print()


    
    
    
    
    
    

    

if __name__ == "__main__":
    main()
