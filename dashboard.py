from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)


CSV_PATH =  "/opt/render/project/src/merged_auctions.csv"
# Column renaming dictionary
COLUMN_RENAMES = {
    "lote": "Lote",
    "name": "Name",
    "padrillo": "Sire",
    "M": "Dam",
    "birth_eday": "Birth Date",
    "haras": "Haras",
    "link": "Auction Reference",
}

# Load data at startup if the CSV exists
df = None
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    print(df)
    df.rename(columns=COLUMN_RENAMES, inplace=True)

@app.route('/', methods=['GET'])
def index():
    if os.path.exists(CSV_PATH):
        # Load the merged CSV
        df = pd.read_csv(CSV_PATH)

        # Rename columns
        df.rename(columns=COLUMN_RENAMES, inplace=True)

        # Convert 'Yegua' column to boolean (if exists)
        if 'Yegua' in df.columns:
            df['Yegua'] = df['Yegua'].astype(bool)

        # Format percentage columns if they exist
        percentage_cols = ["PR", "PS", "PRS"]
        for col in percentage_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

        # Filter data for tabs
        df_yegua = df[df['Yegua']] if 'Yegua' in df.columns else pd.DataFrame()
        df_caballos = df[~df['Yegua']] if 'Yegua' in df.columns else df

        return render_template('index.html', 
                               columns=df.columns, 
                               data_yegua=df_yegua.to_dict(orient='records'), 
                               data_caballos=df_caballos.to_dict(orient='records'))
    
    return render_template('index.html', columns=[], data_yegua=[], data_caballos=[], message="No data found in merged_auctions.csv")


@app.route('/filter', methods=['POST'])
def filter_data():
    if not os.path.exists(CSV_PATH):
        return jsonify({'error': 'No data available.'})

    df = pd.read_csv(CSV_PATH)
    df.rename(columns=COLUMN_RENAMES, inplace=True)

    filters = request.json
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if column in filtered_df.columns and value:
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
    
    return jsonify(filtered_df.to_dict(orient='records'))


@app.route('/data', methods=['GET'])
def load_static_data():
    """Returns all dataset entries at once."""
    if not os.path.exists(CSV_PATH):
        return jsonify({'error': 'No data available.'})

    df = pd.read_csv(CSV_PATH)
    df.rename(columns=COLUMN_RENAMES, inplace=True)

    # Format percentage columns if they exist
    percentage_cols = ["PR (%)", "PS (%)", "PRS (%)"]
    for col in percentage_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

    return jsonify({'data': df.to_dict(orient="records")})


if __name__ == '__main__':
    app.run(debug=True)
