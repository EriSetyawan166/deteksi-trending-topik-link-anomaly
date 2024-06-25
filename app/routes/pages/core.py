# Flask modules
from flask import Blueprint, render_template, current_app, Response, request
import csv
import json
from ...util import link_anomaly
from ...util import preprocessing
from ...util import lda
from ...util import PoolManager
import os
import mysql.connector
import locale
from flask import jsonify, send_from_directory
import cProfile
import pstats

core_bp = Blueprint("core", __name__, url_prefix="/")
processing_pool = None


def save_to_json(data, filename):
    """
    Menyimpan data ke dalam file JSON.

    Parameter:
    - data (dict/list): Data yang akan disimpan.
    - filename (str): Nama file yang akan dibuat untuk menyimpan data.

    Tidak ada nilai yang dikembalikan.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=str)


def create_db_connection():
    """
    Membuat koneksi ke database menggunakan konfigurasi dari aplikasi Flask.

    Return:
    - Connection: Objek koneksi ke database.
    """
    db_config = {
        'host': current_app.config['MYSQL_HOST'],
        'user': current_app.config['MYSQL_USER'],
        'password': current_app.config['MYSQL_PASSWORD'],
        'database': current_app.config['MYSQL_DATABASE']
    }

    return mysql.connector.connect(**db_config)


@core_bp.route("/")
def home_route():
    """
    Route untuk halaman utama aplikasi.

    Return:
    - Rendered template: Mengembalikan template halaman utama.
    """
    return render_template("pages/index.html")


@core_bp.route("/import")
def scraping_route():
    """
    Route untuk halaman import data.

    Return:
    - Rendered template: Mengembalikan template halaman import data.
    """
    return render_template("pages/import.html")


@core_bp.route("/api/data")
def api_data():
    """
    API route yang menyediakan data dari dataset Twitter.

    Return:
    - JSON: Mengembalikan data dalam format JSON.
    """
    response_data = []
    db = create_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM dataset_twitter")
    data = cursor.fetchall()
    for row in data:
        row_data = {
            "id": row[0],
            "url": row[1],
            "date": row[2],
            "username": row[3],
            "displayname": row[4],
            "description": row[5],
            "followersCount": row[6],
            "friendsCount": row[7],
            "statusesCount": row[8],
            "location": row[9],
            "rawContent": row[10]
        }
        response_data.append(row_data)
    return jsonify({"data": response_data})


@core_bp.route("api/delete_all_data", methods=['DELETE'])
def api_delete_all_data():
    """
    API route untuk menghapus semua data dari dataset Twitter.

    Return:
    - JSON: Pesan konfirmasi penghapusan data.
    """
    db = create_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM dataset_twitter")
    db.commit()
    return jsonify({"message": "All data deleted successfully"})


@core_bp.route("api/upload_csv_file", methods=['POST'])
def api_upload_csv_file():
    """
    API route untuk mengunggah dan memproses file CSV ke dalam database.

    Return:
    - JSON: Mengembalikan pesan keberhasilan atau pesan kesalahan.
    """
    db = create_db_connection()
    cursor = db.cursor()
    if 'fileInput' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['fileInput']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        try:
            file.save('tweets-data/' + file.filename)

            with open('tweets-data/' + file.filename, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)
                for row in csvreader:
                    url = row['url']
                    date = row['date']
                    username = row['username']
                    displayname = row['displayname']
                    description = row['description']
                    followersCount = int(row['followersCount'])
                    friendsCount = int(row['friendsCount'])
                    statusesCount = int(row['statusesCount'])
                    location = row['location']
                    rawContent = row['rawContent']

                    sql = """INSERT INTO dataset_twitter (url, date, username, displayname, description, followersCount,
                                         friendsCount, statusesCount, location, rawContent)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    values = (url, date, username, displayname, description, followersCount,
                              friendsCount, statusesCount, location, rawContent)

                    cursor.execute(sql, values)
                    db.commit()

            return jsonify({"message": "CSV file uploaded and processed successfully"}), 200
        except Exception as e:
            print("error Failed to process CSV file: " + str(e))
            return jsonify({"error": "Failed to process CSV file: " + str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format, please upload a CSV file"}), 400


@core_bp.route("/preprocessing")
def preprocessing_route():
    """
    Route untuk halaman pra-pemrosesan data.

    Return:
    - Rendered template: Mengembalikan template halaman pra-pemrosesan.
    """
    return render_template("pages/preprocessing.html")


@core_bp.route("/api/data/preprocessing")
def api_data_preprocessing():
    """
    API route yang menyediakan data yang telah dipra-proses.

    Return:
    - JSON: Mengembalikan data dalam format JSON, termasuk jumlah total data.
    """
    db = create_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM dataset_preprocessed")
    data = cursor.fetchall()

    response_data = []
    for row in data:
        row_data = {
            "id": row[0],
            "time": row[1],
            "user_twitter": row[2],
            "tweet": row[3],
            "jumlah_mention": row[4],
            "id_user_mentioned": row[5],
        }
        response_data.append(row_data)

    total_count = len(response_data)

    return jsonify({"data": response_data, "total_count": total_count})


@core_bp.route("/api/data/stats")
def api_data_stats():
    """
    API route untuk mendapatkan statistik data dalam database.

    Return:
    - JSON: Mengembalikan jumlah total data dan jumlah data yang telah diproses.
    """
    db = create_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM dataset_twitter")
    total_data = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM dataset_preprocessed WHERE tweet != 'n/a'")
    processed_data = cursor.fetchone()[0]

    return jsonify({"total_data": total_data, "processed_data": processed_data})


@core_bp.route("/delete_preprocessing_data", methods=['POST'])
def delete_preprocessing_data():
    """
    Menghapus semua data yang telah dipra-proses dari database.

    Return:
    - JSON: Respon berisi pesan keberhasilan atau kesalahan.
    """
    db = create_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM dataset_preprocessed")
        db.commit()
        return jsonify({"success": "Data berhasil dihapus"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Gagal menghapus data: {}".format(str(e))}), 500
    finally:
        cursor.close()
        db.close()


@core_bp.route("/check_preprocessing_data", methods=['GET'])
def check_preprocessing_data():
    """
    Mengecek apakah terdapat data yang telah dipra-proses di database.

    Return:
    - JSON: Respon berisi status keberadaan data pra-proses.
    """
    db = create_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM dataset_preprocessed LIMIT 1)")
        exists = cursor.fetchone()[0]
        return jsonify({"exists": bool(exists)})
    finally:
        cursor.close()
        db.close()


@core_bp.route("/run_preprocessing", methods=['POST'])
def run_preprocessing():
    """
    Melakukan pra-pemrosesan data dan menyimpan hasilnya ke database.

    Return:
    - JSON: Respon berisi pesan keberhasilan atau kesalahan, dan data yang diproses.
    """
    db = create_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id, date, username, rawContent FROM dataset_twitter")
        data = cursor.fetchall()

        processed_data = preprocessing.preprocess(data)

        insert_sql = """
            INSERT INTO dataset_preprocessed (id, time, user_twitter, tweet, jumlah_mention, id_user_mentioned)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, processed_data)  # Batch insert
        db.commit()
        return jsonify({"success": "Data processed and stored successfully", "data": processed_data})

    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": "Failed to process data: {}".format(str(err))}), 500

    finally:
        cursor.close()
        db.close()


@core_bp.route("/cancel_preprocessing", methods=["POST"])
def cancel_preprocessing():
    """
    Membatalkan operasi pra-pemrosesan yang sedang berlangsung.

    Return:
    - JSON: Respon berisi pesan keberhasilan pembatalan atau kesalahan.
    """
    if PoolManager.get_pool() is not None:
        PoolManager.terminate_pool()
        return jsonify({"message": "Preprocessing cancelled successfully"}), 200
    else:
        return jsonify({"error": "No active preprocessing"}), 400


@core_bp.route("/link_anomaly")
def link_anomaly_route():
    """
    Menampilkan halaman untuk analisis anomali link.

    Return:
    - Rendered template: Mengembalikan template halaman analisis anomali link.
    """
    return render_template("pages/link_anomaly.html")


@core_bp.route('/link_anomaly_result_detail.json')
def serve_json_link_anomaly_result_detail():
    """
    Menyajikan file JSON yang berisi detail hasil analisis anomali link.

    Return:
    - JSON file: Kirim file JSON yang berisi hasil detail dari analisis anomali link.
    """
    directory = os.getcwd()
    return send_from_directory(directory, 'link_anomaly_result_detail.json')


@core_bp.route("/run_link_anomaly")
def run_link_anomaly():
    """
    Melakukan analisis anomaly pada data link berdasarkan urutan waktu tertentu.

    Parameter:
    - sequence (int): Jumlah urutan data yang akan dianalisis.

    Return:
    - JSON: Respon berisi hasil analisis dengan detail seperti skor anomaly, probabilitas, dan lain-lain.
    """
    locale.setlocale(locale.LC_TIME, 'id_ID')
    db = create_db_connection()

    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM dataset_preprocessed ORDER BY time ASC")
    data = cursor.fetchall()

    sequence = int(request.args.get('sequence', '2'))

    default_response = {
        "sequence_number": None,
        "sequence_value": None,
        "sequence_text": [],
        "probabilitas_mention_keseluruhan": {},
        "probabilitas_user_keseluruhan": {},
        "skor_link_anomaly_keseluruhan": {},
        "agregasi_skor_link_anomaly_keseluruhan": {},
        "seleksi_agregasi_skor_link_anomaly_keseluruhan": {},
        "cost_function": [],
        "waktu_sequence_terpilih": [],
        "info_message": "Jumlah sequence melebihi jumlah data yang tersedia."
    }

    if sequence >= len(data):
        return jsonify(default_response)

    hasil = link_anomaly(data, sequence)

    sequence_number, sequence_value = hasil[0]
    sequence_text = hasil[1]
    probabilitas_mention_keseluruhan = hasil[3]
    probabilitas_user_keseluruhan = hasil[4]
    skor_link_anomaly_keseluruhan = hasil[5]
    agregasi_skor_link_anomaly_keseluruhan = hasil[6]
    seleksi_agregasi_skor_link_anomaly_keseluruhan = hasil[7]
    cost_function = hasil[8]
    info_message = ""

    if not cost_function:
        info_message = "Agregasi skor link anomaly tidak cukup"

    waktu_sequence_terpilih = hasil[9]
    response_data = {
        "sequence_number": sequence_number,
        "sequence_value": sequence_value,
        "sequence_text": sequence_text,
        "probabilitas_mention_keseluruhan": probabilitas_mention_keseluruhan,
        "probabilitas_user_keseluruhan": probabilitas_user_keseluruhan,
        "skor_link_anomaly_keseluruhan": skor_link_anomaly_keseluruhan,
        "agregasi_skor_link_anomaly_keseluruhan": agregasi_skor_link_anomaly_keseluruhan,
        "seleksi_agregasi_skor_link_anomaly_keseluruhan": seleksi_agregasi_skor_link_anomaly_keseluruhan,
        "cost_function": cost_function,
        "waktu_sequence_terpilih": waktu_sequence_terpilih,
        "info_message": info_message
    }

    save_to_json({
        "sequence_number": sequence_number,
        "sequence_value": sequence_value,
        "sequence_text": sequence_text,
        "probabilitas_mention_keseluruhan": probabilitas_mention_keseluruhan,
        "probabilitas_user_keseluruhan": probabilitas_user_keseluruhan,
        "skor_link_anomaly_keseluruhan": skor_link_anomaly_keseluruhan,
        "agregasi_skor_link_anomaly_keseluruhan": agregasi_skor_link_anomaly_keseluruhan,
        "seleksi_agregasi_skor_link_anomaly_keseluruhan": seleksi_agregasi_skor_link_anomaly_keseluruhan,
        "cost_function": cost_function,
        "waktu_sequence_terpilih": waktu_sequence_terpilih
    }, 'link_anomaly_result_detail.json')

    save_to_json({
        "waktu_sequence_terpilih": waktu_sequence_terpilih,
        "sequence_text": sequence_text
    }, 'link_anomaly_result.json')

    return jsonify(response_data)


@core_bp.route("/modelling")
def modelling_route():
    """
    Menampilkan halaman untuk pemodelan.

    Return:
    - Rendered template: Mengembalikan template halaman pemodelan.
    """
    return render_template("pages/modelling.html")


@core_bp.route("/api/data/hasil_link_anomaly")
def hasil_link_anomaly():
    """
    Mengembalikan hasil analisis link anomaly yang tersimpan dalam format JSON.

    Return:
    - JSON: Respon berisi data hasil analisis atau pesan kesalahan.
    """
    try:
        with open('link_anomaly_result.json', 'r') as file:
            data = json.load(file)

        return jsonify(data)

    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500


@core_bp.route('/run_lda', methods=['GET'])
def run_lda():
    """
    Melakukan pemodelan Latent Dirichlet Allocation (LDA) berdasarkan teks yang dianalisis sebelumnya.

    Return:
    - JSON: Respon berisi daftar topik yang dihasilkan atau pesan kesalahan.
    """
    try:
        with open('link_anomaly_result.json', 'r') as file:
            data = json.load(file)
            sequence_texts = data.get('sequence_text', [])

        if not sequence_texts:
            return jsonify({"error": "LDA gagal dilakukan karena belum ada hasil link anomaly"}), 400
        tokenized_data = lda.tokenize_data(sequence_texts)

        K = 10
        max_iteration = 2000
        topic_word_counts, document_topic_counts, document_lengths, topic_counts, W = lda.run_lda(
            tokenized_data, K, max_iteration)
        topic_word_list = lda.get_topic_word_list(topic_word_counts, document_topic_counts,
                                                  document_lengths, topic_counts, K, W)
        save_to_json({
            "topic_word_list": topic_word_list,
        }, 'topic_word_list.json')

        return jsonify({"topic_word_list": topic_word_list})

    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@core_bp.route("/api/data/hasil_lda")
def hasil_lda():
    """
    Menyajikan hasil pemodelan LDA yang telah disimpan dalam format JSON.

    Return:
    - JSON: Mengembalikan data hasil LDA atau pesan kesalahan jika file tidak ditemukan atau terjadi kesalahan decoding.
    """
    try:
        with open('topic_word_list.json', 'r') as file:
            data = json.load(file)

        return jsonify(data)

    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500


@core_bp.route('/topic_word_list.json')
def serve_json():
    """
    Menyediakan akses langsung ke file JSON yang berisi daftar kata per topik hasil pemodelan LDA.

    Return:
    - File: Mengirim file JSON 'topic_word_list.json' dari direktori kerja saat ini.
    """
    directory = os.getcwd()
    return send_from_directory(directory, 'topic_word_list.json')
