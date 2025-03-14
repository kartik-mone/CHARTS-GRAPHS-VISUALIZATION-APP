from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import matplotlib.pyplot as plt
import os
from io import BytesIO
import base64

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
CHART_FOLDER = "charts"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CHART_FOLDER"] = CHART_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)

uploaded_file = None  # To store uploaded file's name globally
current_chart = None  # To store the current chart's path

@app.route("/", methods=["GET", "POST"])
def index():
    global uploaded_file
    if request.method == "POST":
        file = request.files["dataset"]
        if file:
            uploaded_file = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(uploaded_file)
            df = load_data(uploaded_file)
            columns = df.columns.tolist()
            return render_template("index.html", columns=columns, chart_img=None)
    return render_template("index.html", columns=None, chart_img=None)

@app.route("/generate-chart", methods=["POST"])
def generate_chart():
    global uploaded_file, current_chart
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    chart_type = request.json.get("chart_type")
    file_format = request.json.get("file_format", "png")
    df = load_data(uploaded_file)

    # Save chart to file
    current_chart = save_chart(df, chart_type, file_format)
    chart_img = convert_chart_to_base64(current_chart)
    return jsonify({"chart_img": chart_img})

@app.route("/download-chart/<format>")
def download_chart(format):
    global current_chart
    if not current_chart or not os.path.exists(current_chart):
        return jsonify({"error": "No chart to download"}), 400

    # Convert to requested format if necessary
    if format not in ["png", "jpg", "pdf"]:
        return jsonify({"error": "Invalid format"}), 400

    if current_chart.endswith(f".{format}"):
        return send_file(current_chart, as_attachment=True)

    # Convert chart to requested format
    chart_base, _ = os.path.splitext(current_chart)
    converted_chart = f"{chart_base}.{format}"
    df = pd.read_csv(uploaded_file) if uploaded_file.endswith(".csv") else pd.read_excel(uploaded_file)
    save_chart(df, None, format, save_path=converted_chart)
    return send_file(converted_chart, as_attachment=True)

def load_data(filepath):
    return pd.read_csv(filepath) if filepath.endswith(".csv") else pd.read_excel(filepath)

def save_chart(df, chart_type, file_format, save_path=None):
    plt.figure(figsize=(8, 6))
    if chart_type == "bar":
        df.iloc[:, 1].value_counts().plot(kind="bar")
    elif chart_type == "pie":
        df.iloc[:, 1].value_counts().plot(kind="pie", autopct='%1.1f%%')
    elif chart_type == "hist":
        df.iloc[:, 1].plot(kind="hist")
    elif chart_type == "dot":
        plt.plot(df.iloc[:, 0], df.iloc[:, 1], "o")
    elif chart_type == "line":
        df.plot(kind="line")
    else:
        plt.text(0.5, 0.5, "Unsupported Chart Type", horizontalalignment="center", verticalalignment="center")
    
    plt.title("Chart Visualization")
    plt.tight_layout()

    if not save_path:
        save_path = os.path.join(app.config["CHART_FOLDER"], f"chart.{file_format}")
    plt.savefig(save_path, format=file_format)
    plt.close()
    return save_path

def convert_chart_to_base64(chart_path):
    with open(chart_path, "rb") as img_file:
        base64_img = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/{os.path.splitext(chart_path)[-1][1:]};base64,{base64_img}"

if __name__ == "__main__":
    app.run(debug=True)
