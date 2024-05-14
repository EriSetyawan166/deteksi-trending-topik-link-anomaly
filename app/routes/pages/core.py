# Flask modules
from flask import Blueprint, render_template, current_app, Response, request
import csv
from ...util import link_anomaly
# from models import DatasetPreprocessed
import mysql.connector
import locale
from flask import jsonify

core_bp = Blueprint("core", __name__, url_prefix="/")


def create_db_connection():
    # Your database configuration
    db_config = {
        'host': current_app.config['MYSQL_HOST'],
        'user': current_app.config['MYSQL_USER'],
        'password': current_app.config['MYSQL_PASSWORD'],
        'database': current_app.config['MYSQL_DATABASE']
    }

    # Create database connection
    return mysql.connector.connect(**db_config)


@core_bp.route("/")
def home_route():
    return render_template("pages/index.html")


@core_bp.route("/import")
def scraping_route():
    # Render the import template
    return render_template("pages/import.html")


@core_bp.route("/api/data")
def api_data():
    response_data = []
    db = create_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "SELECT username, created_at, full_text FROM dataset_twitter")
    data = cursor.fetchall()

    for row in data:
        # Each row is a tuple, so unpack the values
        username, created_at, full_text = row
        # Create a dictionary for the current row and append it to the response data list
        row_data = {
            "username": username,
            "created_at": created_at,
            "full_text": full_text,
        }
        response_data.append(row_data)

    # Wrap the list of data in a dictionary under the key 'data'
    return jsonify({"data": response_data})


@core_bp.route("api/delete_all_data", methods=['DELETE'])
def api_delete_all_data():
    db = create_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM dataset_twitter")
    db.commit()
    return jsonify({"message": "All data deleted successfully"})


@core_bp.route("api/upload_csv_file", methods=['POST'])
def api_upload_csv_file():
    db = create_db_connection()
    cursor = db.cursor()
    if 'fileInput' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['fileInput']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        try:
            # Simpan file CSV ke direktori server (misalnya 'uploads/')
            file.save('tweets-data/' + file.filename)

            # Proses file CSV
            with open('tweets-data/' + file.filename, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)
                for row in csvreader:
                    # Lakukan sesuatu dengan setiap baris (contoh: simpan ke database)
                    conversation_id_str = row['conversation_id_str']
                    created_at = row['created_at']
                    favorite_count = row['favorite_count']
                    full_text = row['full_text']
                    id_str = row['id_str']
                    image_url = row['image_url']
                    in_reply_to_screen_name = row['in_reply_to_screen_name']
                    lang = row['lang']
                    location = row['location']
                    quote_count = row['quote_count']
                    reply_count = row['reply_count']
                    retweet_count = row['retweet_count']
                    tweet_url = row['tweet_url']
                    user_id_str = row['user_id_str']
                    username = row['username']

                    # Query SQL untuk memasukkan data ke tabel
                    sql = """INSERT INTO dataset_twitter (conversation_id_str, created_at, favorite_count, full_text, id_str, 
                            image_url, in_reply_to_screen_name, lang, location, quote_count, reply_count, retweet_count, 
                            tweet_url, user_id_str, username) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    values = (conversation_id_str, created_at, favorite_count, full_text, id_str, image_url, 
                            in_reply_to_screen_name, lang, location, quote_count, reply_count, retweet_count, 
                            tweet_url, user_id_str, username)
                    
                    # Eksekusi query SQL
                    cursor.execute(sql, values)
                    db.commit()

            return jsonify({"message": "CSV file uploaded and processed successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Failed to process CSV file: " + str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format, please upload a CSV file"}), 400


# Route for preprocessing page


@core_bp.route("/preprocessing")
def preprocessing_route():
    # Render the preprocessing template
    return render_template("pages/preprocessing.html")

# Route for link anomaly page


@core_bp.route("/link_anomaly")
def link_anomaly_route():
    # Render the template
    return render_template("pages/link_anomaly.html")


@core_bp.route("/run_link_anomaly")
def run_link_anomaly():
    locale.setlocale(locale.LC_TIME, 'id_ID')
    db = create_db_connection()

    cursor = db.cursor()
    cursor.execute("SELECT * FROM dataset_preprocessed ORDER BY time ASC")
    data = cursor.fetchall()

    sequence = int(request.args.get('sequence', '2'))

    hasil = link_anomaly(data, sequence)

    # Assuming hasil is a tuple as you described:
    sequence_number, sequence_value = hasil[0]
    # Taking the first element from the list if it's always one element
    sequence_text = hasil[1]
    probabilitas_mention_keseluruhan = hasil[3]
    probabilitas_user_keseluruhan = hasil[4]
    skor_link_anomaly_keseluruhan = hasil[5]
    agregasi_skor_link_anomaly_keseluruhan = hasil[6]
    seleksi_agregasi_skor_link_anomaly_keseluruhan = hasil[7]
    cost_function = hasil[8]
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
        "waktu_sequence_terpilih": waktu_sequence_terpilih
    }

    return jsonify(response_data)

# Route for modelling page


@core_bp.route("/modelling")
def modelling_route():
    # Render the modelling template
    return render_template("pages/modelling.html")

# Route for pengujian page


@core_bp.route("/pengujian")
def pengujian_route():
    # Render the pengujian template
    return render_template("pages/pengujian.html")
