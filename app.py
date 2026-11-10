from flask import Flask, render_template, request

app = Flask(__name__, template_folder=".")


@app.route("/", methods=["GET", "POST"])
def home():
    website = request.form.get("website", "").strip()
    return render_template("index.html", website=website)
