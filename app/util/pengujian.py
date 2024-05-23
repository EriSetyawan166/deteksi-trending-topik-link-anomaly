def pengujian(data_ground_truth, topic_word_list):
    # Ekstrak daftar kata topik
    detected_words = topic_word_list['topic_word_list']['Topik 1']

    # Inisialisasi metrik
    TP = 0
    FP = 0
    FN = 0

    # Set untuk memudahkan pencarian kata
    detected_set = set(detected_words)

    # Menghitung TP dan FN
    for _, _, ground_truth_keywords in data_ground_truth:
        ground_truth_set = set(ground_truth_keywords.split())

        # True Positives: Kata terdeteksi yang juga ada di ground truth
        TP += len(detected_set.intersection(ground_truth_set))

        # False Negatives: Kata di ground truth yang tidak terdeteksi
        FN += len(ground_truth_set - detected_set)
        print(ground_truth_set)
        print(detected_set)
        print(ground_truth_set - detected_set)
        print()

    # print(TP, FN)

    # False Positives: Kata terdeteksi yang tidak ada di ground truth
    all_ground_truth_keywords = set()
    for _, _, ground_truth_keywords in data_ground_truth:
        all_ground_truth_keywords.update(ground_truth_keywords.split())

    FP = len(detected_set - all_ground_truth_keywords)

    # Tampilkan hasil
    print("Confusion Matrix Results:")
    print(f"True Positives (TP): {TP}")
    print(f"False Positives (FP): {FP}")
    print(f"False Negatives (FN): {FN}")
    accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")


def main():
    data_ground_truth = [(10, 'Gerilya Mencegah Hak Angket Kecurangan Pemilu 2024 Melaju di DPR', 'cegah hak angket curang pemilu dpr'), (11, 'KPU Tak Hadir, Komisi II DPR Tunda Rapat Evaluasi Pemilu Sampai Mei 2024', 'kpu dpr tunda rapat evaluasi pemilu'), (12, 'Empat Menteri Dipanggil ke Sidang MK, Ngabalin: Masa Sengketa Pemilu Bahas Bansos', 'menteri panggil sidang mk sengketa pemilu bansos'), (13, 'Peluang dan Tantangan Diskualifikasi Prabowo-Gibran di MK', 'diskualifikasi prabowo gibran mk'), (14,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         'Uskup Agung: Jika Tidak Setuju dengan Hasil Pemilu, Jangan Buat Rusuh', 'hasil pemilu rusuh'), (15, 'Panas MK Sidang pemilu Lagi, Banyak Nama Menteri Disebut-sebut', 'mk sidang pemilu menteri'), (16, 'Soroti Pemilu 2024, Romli Atmasasmita: Prihatin, Hukum Seolah Jadi Mainan Politik', 'pemilu prihatin hukum politik'), (17, 'Kubu Prabowo-Gibran Yakin Permohonan Sengketa Pemilu 2024 Tak Dikabulkan', 'prabowo gibran sengketa pemilu'), (18, '[HOAKS] MK Telah Putuskan pemilu 2024 Diulang', 'hoaks mk putus pemilu diulang')]
    topic_word_list = {
        "topic_word_list": {
            "Topik 1": [
                "pemilu",
                "curang",
                "ulang",
                "menang",
                "mk",
                "damai",
                "hasil",
                "rakyat",
                "kalah",
                "gugat",
                "pilih",
                "suara",
                "adil",
                "orang",
                "kpu"
            ]
        }
    }
    pengujian(data_ground_truth, topic_word_list)


if __name__ == '__main__':
    main()
