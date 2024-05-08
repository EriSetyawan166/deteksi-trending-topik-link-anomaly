# Flask modules
from flask import Blueprint, render_template

core_bp = Blueprint("core", __name__, url_prefix="/")


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
    # Render the link anomaly template
    return render_template("pages/link_anomaly.html")

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