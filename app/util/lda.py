import random
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
# Fungsi untuk mentokenisasi data dalam bahasa Indonesia


def tokenize_data(data):
    # Set stop words dalam bahasa Indonesia
    stop_words = set(stopwords.words('indonesian'))
    tokens_list = []

    for text in data:
        # Tokenisasi dan konversi ke huruf kecil
        tokens = word_tokenize(text.lower())
        # Hapus punctuation dan stop words
        tokens = [word for word in tokens if word.isalnum()
                  and word not in stop_words]
        tokens_list.append(tokens)

    return tokens_list

# Fungsi untuk memilih indeks berdasarkan bobot


def sample_from_weights(weights):
    # print('bobot', weights)
    total = sum(weights)
    rnd = total * random.random()
    # print('nilai acak', rnd)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0:
            # print('nilai terpilih', rnd, i)
            return i  # mengembalikan indeks

# Fungsi untuk menghitung probabilitas topik diberikan dokumen


def p_topic_given_document(topic, d, document_topic_counts, document_lengths, K, alpha=0.1):
    # print('jumlah topik sebuah dokumen', document_topic_counts[d][topic])
    # print('panjang dokumen', document_lengths)
    return ((document_topic_counts[d][topic] + alpha) /
            (document_lengths[d] + K * alpha))

# Fungsi untuk menghitung probabilitas kata diberikan topik


def p_word_given_topic(word, topic, topic_word_counts, topic_counts, W, beta=0.1):
    # print('jumlah topik pada sebuah kata', topic_word_counts[topic][word])
    # print('jumlah topik', topic_counts[topic])
    return ((topic_word_counts[topic][word] + beta) /
            (topic_counts[topic] + W * beta))

# Fungsi untuk menghitung bobot topik untuk kata tertentu dalam dokumen


def topic_weight(d, word, topic, document_topic_counts, document_lengths, topic_word_counts, topic_counts, K, W, alpha=0.1, beta=0.1):
    return p_word_given_topic(word, topic, topic_word_counts, topic_counts, W, beta) * p_topic_given_document(topic, d, document_topic_counts, document_lengths, K, alpha)

# Fungsi untuk memilih topik baru berdasarkan bobot


def choose_new_topic(d, word, K, document_topic_counts, document_lengths, topic_word_counts, topic_counts, W):
    weights = []
    for k in range(K):
        weight = topic_weight(d, word, k, document_topic_counts,
                              document_lengths, topic_word_counts, topic_counts, K, W)
        weights.append(weight)
    return sample_from_weights(weights)

# Fungsi untuk melakukan Gibbs sampling


def gibbs_sample(documents, K, max_iteration, document_topic_counts, topic_word_counts, topic_counts, document_lengths, document_topics, W):
    # print('topik dokumen', document_topics)
    D = len(documents)
    for _ in range(max_iteration):
        for d in range(D):
            for i, (word, topic) in enumerate(zip(documents[d], document_topics[d])):
                # print(word)
                # print("dokumen, dan topik dokumen",
                #       documents[d], document_topics[d])
                # print()
                document_topic_counts[d][topic] -= 1
                # print('dokumen topik count', document_topic_counts[d][topic])
                # print()
                # print('topik word count', topic_word_counts[topic][word])
                topic_word_counts[topic][word] -= 1
                # print('topik word count', topic_word_counts[topic][word])
                # print()
                topic_counts[topic] -= 1
                # print('topic count', topic_counts[topic])
                # print()
                document_lengths[d] -= 1
                # print('document length', document_lengths[d])
                # print()

                # Pilih topik baru berdasarkan bobot
                new_topic = choose_new_topic(
                    d, word, K, document_topic_counts, document_lengths, topic_word_counts, topic_counts, W)
                # print('topik baru', new_topic)
                # print('topik kata sebelum pembobotan', document_topics[d][i])
                document_topics[d][i] = new_topic
                # print('topik kata sesudah pembobotan', document_topics[d][i])

                # Tambahkan kembali ke jumlah
                document_topic_counts[d][new_topic] += 1
                topic_word_counts[new_topic][word] += 1
                topic_counts[new_topic] += 1
                document_lengths[d] += 1
# Fungsi utama untuk menjalankan LDA


def run_lda(documents, K, max_iteration):
    D = len(documents)
    document_topic_counts = [Counter() for _ in documents]
    topic_word_counts = [Counter() for _ in range(K)]
    topic_counts = [0 for _ in range(K)]
    document_lengths = [len(d) for d in documents]
    distinct_words = set(word for document in documents for word in document)
    W = len(distinct_words)

    document_topics = []
    for document in documents:
        topics = []
        for _ in document:
            topics.append(random.randrange(K))
        document_topics.append(topics)

    for d in range(D):
        for word, topic in zip(documents[d], document_topics[d]):
            document_topic_counts[d][topic] += 1
            topic_word_counts[topic][word] += 1
            topic_counts[topic] += 1

    # print(document_topic_counts)
    # print()
    # print(topic_word_counts)
    # print()
    # print(topic_counts)
    gibbs_sample(documents, K, max_iteration, document_topic_counts,
                 topic_word_counts, topic_counts, document_lengths, document_topics, W)

    return topic_word_counts, document_topic_counts

# Fungsi untuk mendapatkan daftar kata untuk setiap topik


def get_topic_word_list(topic_word_counts, K):
    topic_word_list = {}
    for topic in range(K):
        data = []
        for word, count in topic_word_counts[topic].most_common():
            if count > 1:
                data.append(word)
        if len(data) > 15:
            data = data[:15]
        topic_word_list[f"Topik {topic+1}"] = data
    return topic_word_list


def main():
    pass


if __name__ == '__main__':
    # Data sampel dalam bahasa Indonesia
    data = [
        "Perubahan iklim berdampak pada peningkatan suhu global dan cuaca ekstrem.",
        "Kemajuan dalam kecerdasan buatan mengubah industri dari kesehatan hingga keuangan.",
        "Pasar saham mengalami penurunan tajam bulan ini karena ketidakpastian ekonomi.",
        "Sumber energi terbarukan seperti tenaga angin dan matahari semakin efektif biaya.",
        "Pemilihan umum lokal semakin memanas saat kandidat bersiap untuk debat mendatang.",
        "Industri teknologi melihat lonjakan inovasi dengan munculnya startup baru di Silicon Valley.",
        "Kekhawatiran tentang privasi dan perlindungan data berada di garis depan regulasi baru dalam pemasaran digital.",
        "Temukan praktik terbaik untuk pertanian berkelanjutan dan produksi pangan lokal.",
        "Pembicaraan damai bersejarah dimulai antara negara-negara tetangga setelah puluhan tahun konflik.",
        "Industri film beradaptasi dengan layanan streaming, mempengaruhi bioskop tradisional.",
    ]

    # Tokenisasi data
    tokenized_data = tokenize_data(data)

    # Menjalankan LDA
    K = 1  # Jumlah topik
    max_iteration = 1000  # Iterasi maksimum
    topic_word_counts, document_topic_counts = run_lda(
        tokenized_data, K, max_iteration)

    # Mendapatkan daftar kata untuk setiap topik
    # print(topic_word_counts)
    topic_word_list = get_topic_word_list(topic_word_counts, K)

    # Menampilkan topik dan kata-kata terkait
    for topic, words in topic_word_list.items():
        print(f"{topic}: {', '.join(words)}")
