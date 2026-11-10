from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
    return "<h1>External Cybersecurity Analyzer</h1>"
