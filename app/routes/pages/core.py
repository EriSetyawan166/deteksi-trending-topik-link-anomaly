# Flask modules
from flask import Blueprint, render_template, current_app, Response, request
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


@core_bp.route("/scraping")
def scraping_route():
    # Render the scraping template
    return render_template("pages/scraping.html")

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
    cursor.execute("SELECT * FROM dataset_preprocessed")
    data = cursor.fetchall()

    sequence = int(request.args.get('sequence', '2'))
    
    hasil = link_anomaly(data, sequence)

    # Assuming hasil is a tuple as you described:
    sequence_number, sequence_value = hasil[0]
    # Taking the first element from the list if it's always one element
    sequence_text = hasil[1]

    response_data = {
        "sequence_number": sequence_number,
        "sequence_value": sequence_value,
        "sequence_text": sequence_text
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
