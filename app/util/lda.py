import random
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string


def tokenize_data(data):
    """
    Tokenisasi data teks menjadi token alfanumerik dalam huruf kecil.

    Parameter:
    - data (list of str): List yang berisi string teks untuk di-tokenisasi.

    Return:
    - list of list of str: List dari list token untuk setiap string input.
    """
    tokens_list = []

    for text in data:
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalnum()]
        tokens_list.append(tokens)

    return tokens_list


def sample_from_weights(weights):
    """
    Memilih indeks berdasarkan distribusi bobot yang diberikan.

    Parameter:
    - weights (list of float): List bobot untuk sampling.

    Return:
    - int: Indeks yang dipilih berdasarkan bobot.
    """
    total = sum(weights)
    rnd = total * random.random()
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0:
            return i


def p_topic_given_document(topic, d, document_topic_counts, document_lengths, K, alpha=0.1):
    """
    Menghitung probabilitas topik tertentu diberikan sebuah dokumen.

    Parameter:
    - topic (int): Indeks topik.
    - d (int): Indeks dokumen.
    - document_topic_counts (list of Counter): Counter jumlah topik per dokumen.
    - document_lengths (list of int): List panjang setiap dokumen.
    - K (int): Jumlah topik total.
    - alpha (float, optional): Parameter alpha untuk smoothing, default 0.1.

    Return:
    - float: Probabilitas topik diberikan dokumen.
    """
    return ((document_topic_counts[d][topic] + alpha) /
            (document_lengths[d] + K * alpha))


def p_word_given_topic(word, topic, topic_word_counts, topic_counts, W, beta=0.1):
    """
    Menghitung probabilitas kata diberikan topik.

    Parameter:
    - word (str): Kata.
    - topic (int): Indeks topik.
    - topic_word_counts (list of Counter): Counter jumlah kata per topik.
    - topic_counts (list of int): Jumlah kata per topik.
    - W (int): Jumlah kata unik di semua dokumen.
    - beta (float, optional): Parameter beta untuk smoothing, default 0.1.

    Return:
    - float: Probabilitas kata diberikan topik.
    """
    return ((topic_word_counts[topic][word] + beta) /
            (topic_counts[topic] + W * beta))


def topic_weight(d, word, topic, document_topic_counts, document_lengths, topic_word_counts, topic_counts, K, W, alpha=0.1, beta=0.1):
    """
    Menghitung bobot topik untuk kata dalam dokumen.

    Parameter:
    - d (int): Indeks dokumen.
    - word (str): Kata yang sedang dipertimbangkan.
    - topic (int): Indeks topik yang sedang dipertimbangkan.
    - document_topic_counts (list of Counter): Counter jumlah topik per dokumen.
    - document_lengths (list of int): List panjang setiap dokumen.
    - topic_word_counts (list of Counter): Counter jumlah kata per topik.
    - topic_counts (list of int): Jumlah kata per topik.
    - K (int): Jumlah topik total.
    - W (int): Jumlah kata unik di semua dokumen.
    - alpha (float, optional): Parameter alpha untuk smoothing, default 0.1.
    - beta (float, optional): Parameter beta untuk smoothing, default 0.1.

    Return:
    - float: Bobot topik untuk kata dalam dokumen.
    """
    return p_word_given_topic(word, topic, topic_word_counts, topic_counts, W, beta) * p_topic_given_document(topic, d, document_topic_counts, document_lengths, K, alpha)


def choose_new_topic(d, word, K, document_topic_counts, document_lengths, topic_word_counts, topic_counts, W):
    """
    Memilih topik baru untuk kata dalam dokumen menggunakan distribusi probabilitas.

    Parameter:
    - d (int): Indeks dokumen.
    - word (str): Kata yang sedang dipertimbangkan.
    - K (int): Jumlah total topik.
    - document_topic_counts (list of Counter): Counter jumlah topik per dokumen.
    - document_lengths (list of int): Panjang setiap dokumen.
    - topic_word_counts (list of Counter): Counter jumlah kata per topik.
    - topic_counts (list of int): Jumlah kata per topik.
    - W (int): Jumlah kata unik di semua dokumen.

    Return:
    - int: Indeks topik baru yang dipilih.
    """
    weights = []
    for k in range(K):
        weight = topic_weight(d, word, k, document_topic_counts,
                              document_lengths, topic_word_counts, topic_counts, K, W)
        weights.append(weight)
    return sample_from_weights(weights)


def gibbs_sample(documents, K, max_iteration, document_topic_counts, topic_word_counts, topic_counts, document_lengths, document_topics, W):
    """
    Melakukan sampling Gibbs untuk inferensi LDA.

    Parameter:
    - documents (list of list of str): Dokumen-dokumen yang berisi kata-kata.
    - K (int): Jumlah total topik.
    - max_iteration (int): Jumlah iterasi maksimum untuk sampling Gibbs.
    - document_topic_counts (list of Counter): Counter jumlah topik per dokumen.
    - topic_word_counts (list of Counter): Counter jumlah kata per topik.
    - topic_counts (list of int): Jumlah kata per topik.
    - document_lengths (list of int): Panjang setiap dokumen.
    - document_topics (list of list of int): Topik saat ini untuk setiap kata di setiap dokumen.
    - W (int): Jumlah kata unik di semua dokumen.

    Tidak ada nilai yang dikembalikan.
    """
    D = len(documents)
    for _ in range(max_iteration):
        for d in range(D):
            for i, (word, topic) in enumerate(zip(documents[d], document_topics[d])):
                document_topic_counts[d][topic] -= 1
                topic_word_counts[topic][word] -= 1
                topic_counts[topic] -= 1
                document_lengths[d] -= 1
                new_topic = choose_new_topic(
                    d, word, K, document_topic_counts, document_lengths, topic_word_counts, topic_counts, W)
                document_topics[d][i] = new_topic
                document_topic_counts[d][new_topic] += 1
                topic_word_counts[new_topic][word] += 1
                topic_counts[new_topic] += 1
                document_lengths[d] += 1


def run_lda(documents, K, max_iteration):
    """
    Menjalankan algoritma Latent Dirichlet Allocation (LDA).

    Parameter:
    - documents (list of list of str): Dokumen-dokumen yang akan diproses.
    - K (int): Jumlah topik yang akan dihasilkan.
    - max_iteration (int): Jumlah iterasi maksimum yang akan dilakukan.

    Return:
    - tuple: Mengembalikan tuple yang berisi counter kata per topik, counter topik per dokumen, panjang dokumen, jumlah kata per topik, dan jumlah kata unik.
    """
    random.seed(28347429)
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

    gibbs_sample(documents, K, max_iteration, document_topic_counts,
                 topic_word_counts, topic_counts, document_lengths, document_topics, W)

    return topic_word_counts, document_topic_counts, document_lengths, topic_counts, W


def get_topic_word_list(topic_word_counts, document_topic_counts, document_lengths, topic_counts, K, W, alpha=0.1, beta=0.1):
    """
    Mendapatkan list kata per topik dengan bobotnya.

    Parameter:
    - topic_word_counts (list of Counter): Counter jumlah kata per topik.
    - document_topic_counts (list of Counter): Counter jumlah topik per dokumen.
    - document_lengths (list of int): Panjang setiap dokumen.
    - topic_counts (list of int): Jumlah kata per topik.
    - K (int): Jumlah topik total.
    - W (int): Jumlah kata unik di semua dokumen.
    - alpha (float, optional): Parameter alpha untuk smoothing, default 0.1.
    - beta (float, optional): Parameter beta untuk smoothing, default 0.1.

    Return:
    - dict: Dictionary dengan topik sebagai kunci dan list kata dengan bobot sebagai nilai.
    """
    topic_word_list = {}
    for topic in range(K):
        data = []
        for word, count in topic_word_counts[topic].most_common():
            if count > 1:
                weight = p_word_given_topic(word, topic, topic_word_counts, topic_counts, W, beta) * \
                    (topic_word_counts[topic][word] / topic_counts[topic])
                if weight > 0.0002:
                    data.append((word, weight))
        topic_word_list[f"Topik {topic+1}"] = data
    return topic_word_list


def main():
    pass


if __name__ == '__main__':
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

    tokenized_data = tokenize_data(data)

    K = 2
    max_iteration = 1000
    topic_word_counts, document_topic_counts, document_lengths, topic_counts, W = run_lda(
        tokenized_data, K, max_iteration)

    topic_word_list = get_topic_word_list(topic_word_counts, document_topic_counts,
                                          document_lengths, topic_counts, K, W)

    for topic, words in topic_word_list.items():
        formatted_words = [f"{word}: {weight:.4f}" for word, weight in words]
        print(f"{topic}: {', '.join(formatted_words)}")
