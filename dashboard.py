from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

df = None  # Global variable to store data

COLUMN_RENAMES = {
    "lote": "Lote",
    "name": "Name",
    "padrillo": "Sire",
    "M": "Dam",
    "birth_eday": "Birth Date",
    "haras": "Hara",
    "link": "Auction Reference",
}

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            df = pd.read_csv(file_path)

            # Rename columns
            df.rename(columns=COLUMN_RENAMES, inplace=True)

            return render_template('index.html', columns=df.columns, data=df.to_dict(orient='records'))
    
    return render_template('index.html', columns=[], data=[])

@app.route('/filter', methods=['POST'])
def filter_data():
    global df
    if df is None:
        return jsonify({'error': 'No data uploaded yet.'})
    
    filters = request.json
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if value:
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
    
    return jsonify(filtered_df.to_dict(orient='records'))

    return jsonify(filtered_df.to_dict(orient='records'))

# Uncomment the section below if you want a static CSV file instead of uploads

    @app.route('/data', methods=['GET'])
    def load_static_data():
        global df
        static_file = "dashboard_data.csv"  # Path to static CSV file
        df = pd.read_csv(static_file)

        # Rename columns
        df.rename(columns=COLUMN_RENAMES, inplace=True)

        # Format percentage columns
        percentage_cols = ["PR (%)", "PS (%)", "PRS (%)"]
        for col in percentage_cols:
            if col in df.columns:
                df[col] = df[col].astype(float).map(lambda x: f"{x:.2f}%")

        return jsonify(df.to_dict(orient="records"))


if __name__ == '__main__':
    app.run(debug=True)