from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Define the persistent storage path
PERSISTENT_FOLDER = "/opt/render/project/src/uploads"
CSV_PATH = os.path.join(PERSISTENT_FOLDER, "dashboard_data.csv")

# Ensure directory exists
os.makedirs(PERSISTENT_FOLDER, exist_ok=True)

# Column renaming dictionary
COLUMN_RENAMES = {
    "lote": "Lote",
    "name": "Name",
    "padrillo": "Sire",
    "M": "Dam",
    "birth_eday": "Birth Date",
    "haras": "Hara",
    "link": "Auction Reference",
}

# Load data at startup if the CSV exists
df = None
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    df.rename(columns=COLUMN_RENAMES, inplace=True)

@app.route('/')
def index():
    """Render homepage with data if available."""
    if df is not None:
        return render_template('index.html', columns=df.columns, data=df.to_dict(orient='records'))
    return render_template('index.html', columns=[], data=[])

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file upload and saves it to the persistent disk."""
    global df
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        file.save(CSV_PATH)  # Save to persistent storage
        df = pd.read_csv(CSV_PATH)
        df.rename(columns=COLUMN_RENAMES, inplace=True)
        return jsonify({'message': 'File uploaded and data loaded successfully'}), 200

    return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

@app.route('/data', methods=['GET'])
def load_static_data():
    """Returns the full dataset in JSON format."""
    if df is None:
        return jsonify({'error': 'No data available.'})

    return jsonify(df.to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True)
