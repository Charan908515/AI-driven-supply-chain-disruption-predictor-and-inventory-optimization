from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import Database,Adjusted_database,DamagedLogDatabase
import csv
from electric_batteries import main  # MileStone-2 code
import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)

db = Database("products.db")
adjusted_db=Adjusted_database("adjusted_data.db")

@app.route('/')
def index():
    products = db.fetch_all_rows()
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add_product():
    try:
        product_id = request.form['product_id']
        company=request.form["company"]
        month = request.form['month']
        cost_price = int(request.form['cost_price'])
        selling_price = int(request.form['selling_price'])
        country = request.form['country']
        stock_level = int(request.form['stock_level'])
        
        db.insert(product_id,company, month, cost_price, selling_price, country, stock_level)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error: {e}", 400


@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        db.remove(product_id)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error: {e}", 400

@app.route('/api/products', methods=['GET'])
def api_products():
    try:
        products = db.fetch_all_rows()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/export', methods=['POST'])
def export_to_excel():
    try:
        import pandas as pd

        # Fetch all products from the database
        products = db.fetch_all_rows()

        # Convert data to a DataFrame
        columns = ["Product ID","company", "Month", "cost_price", "selling_price", "Country", "Stock Level"]
        df = pd.DataFrame(products, columns=columns)

        # Save DataFrame to an Excel file
        excel_file = "products.xlsx"
        df.to_excel(excel_file, index=False)

        # Return success message
        return f"Data exported successfully to {excel_file}"
    except Exception as e:
        return f"Error exporting data: {e}", 500

@app.route('/import', methods=['POST'])
def import_file():
    try:
        # Check if a file is uploaded
        if 'file' not in request.files:
            return "No file part", 400
        
        file = request.files['file']

        # Ensure the file has a valid name
        if file.filename == '':
            return "No selected file", 400

        # Check file extension
        file_extension = file.filename.rsplit('.', 1)[-1].lower()

        if file_extension == 'csv':
            # Process CSV file
            csv_data = csv.reader(file.stream, delimiter=',')
            header = next(csv_data)  # Skip the header row

            for row in csv_data:
                if len(row) == 6:  # Ensure the row has all required fields
                    product_id, month, cost_price, selling_price, country, stock_level = row
                    db.insert(product_id, month, int(cost_price), int(selling_price), country, int(stock_level))
        
        elif file_extension in ['xls', 'xlsx']:
            # Process Excel file
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                db.insert(
                    row['Product ID'],row["company"], row['Month'], int(row['cost_price']), 
                    int(row['selling_price']), row['Country'], int(row['Stock Level'])
                )
        else:
            return "Unsupported file format. Please upload a .csv or .xlsx file.", 400
        
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error importing file: {e}", 500



    
@app.route("/run_prediction", methods=["GET"])
def adjust_inventory_and_predict_risk():
    try:
        # Fetch risk data from the milestone-2 module
        risk_data_path = main()  # Returns the path to the CSV containing risk analysis
        risk_data = pd.read_csv(risk_data_path)

        # Preprocess risk data
        risk_data["Published At"] = pd.to_datetime(risk_data["Published At"]).dt.date
        risk_data["Month"] = pd.to_datetime(risk_data["Published At"]).dt.month_name().str.lower()

        # Initialize summarizer once (efficient)
        summarizer = pipeline("summarization")

        # Fetch products from the database
        products_database = db.fetch_all_rows()
        products = pd.DataFrame(
            products_database,
            columns=["id", "company", "month", "cost_price", "selling_price", "country", "stock_level"]
        )

        # Iterate through risks and adjust inventory
        for _, risk_row in risk_data.iterrows():
            for _, product_row in products.iterrows():
                # Match product with the risk based on company and month
                if product_row["company"].lower() in risk_row["Title"].lower() and \
                        product_row["month"].lower() == risk_row["Month"]:
                    
                    stock_level = product_row["stock_level"]
                    risk_score = risk_row["risk_score"]

                    # Risk thresholds for adjustment and alert logic
                    if risk_score <= -0.5:  # High Risk
                        stock_adjustment = stock_level * -0.30  # Decrease by 30%
                        alert = "sell"
                    elif -0.5 < risk_score < 0.5:  # Moderate Risk
                        stock_adjustment = stock_level * 0.00  # No adjustment
                        alert = "monitor"
                    elif risk_score >= 0.5:  # Low Risk
                        stock_adjustment = stock_level * 0.10  # Increase by 10%
                        alert = "buy"
                    else:
                        stock_adjustment = 0
                        alert = "monitor"

                    # Generate a summary of the risk analysis
                    summary = summarizer(risk_row["Risk Analysis"], max_length=50, min_length=10, do_sample=False)
                    reason = summary[0]['summary_text']

                    # Calculate new stock levels
                    new_stock = int(stock_level + stock_adjustment)

                    # Insert adjusted inventory data into the adjusted database
                    adjusted_db.insert(
                        product_row["id"],
                        product_row["company"],
                        product_row["country"],
                        product_row["stock_level"],
                        new_stock,
                        stock_adjustment,
                        product_row["month"],
                        reason,
                        alert
                    )

        # Fetch and display all adjusted data
        adjusted_data = adjusted_db.fetch_all_rows()
        return render_template('adjusted_inventory.html', adjusted_data=adjusted_data)

    except Exception as e:
        return f"Error: {e}", 500



@app.route('/visualize/inventory', methods=['GET'])
def visualize_inventory():
    try:
        # Fetch inventory data
        inventory_data = db.fetch_all_rows()

        # Check if the data is empty
        if not inventory_data:
            return "<h3>No data available in the inventory table to visualize.</h3>"

        # Convert data to a DataFrame
        df = pd.DataFrame(inventory_data, columns=[
            "Product ID", "Company", "Month", "Cost Price", "Selling Price", "Country", "Stock Level"
        ])

        # Group by company and sum stock levels
        stock_by_company = df.groupby('Company')['Stock Level'].sum().sort_values()

        # Plot the data
        fig, ax = plt.subplots(figsize=(10, 6))
        stock_by_company.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
        ax.set_title('Stock Levels by Company', fontsize=16)
        ax.set_ylabel('Total Stock Level', fontsize=12)
        ax.set_xlabel('Company', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        return f'<img src="data:image/png;base64,{plot_url}" alt="Inventory Visualization">'

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/visualize/adjusted_inventory', methods=['GET'])
def visualize_adjusted_inventory():
    try:
        # Fetch adjusted inventory data
        adjusted_data = adjusted_db.fetch_all_rows()

        # Check if the data is empty
        if not adjusted_data:
            return "<h3>No data available in the adjusted inventory table to visualize.</h3>"

        # Convert data to a DataFrame
        df = pd.DataFrame(adjusted_data, columns=[
            "Product ID", "Company", "Country", "Stock Level", "Adjusted Stock", 
            "Adjustment", "Month", "Reason", "Alert"
        ])

        # Calculate stock adjustment per company
        stock_adjustment_by_company = df.groupby('Company')['Adjustment'].sum().sort_values()

        # Plot the data
        fig, ax = plt.subplots(figsize=(10, 6))
        stock_adjustment_by_company.plot(kind='bar', ax=ax, color='lightcoral', edgecolor='black')
        ax.set_title('Total Stock Adjustments by Company', fontsize=16)
        ax.set_ylabel('Total Adjustment', fontsize=12)
        ax.set_xlabel('Company', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        return f'<img src="data:image/png;base64,{plot_url}" alt="Adjusted Inventory Visualization">'

    except Exception as e:
        return jsonify({"error": str(e)}), 500


damaged_db = DamagedLogDatabase("damaged_logs.db")

@app.route('/log_damage', methods=['POST'])
def log_damage():
    try:
        data = request.get_json()
        product_id = data['product_id']
        company = data['company']
        country = data['country']
        damage_reason = data['damage_reason']
        quantity = data['quantity']
        reported_date = data['reported_date']

        damaged_db.insert(product_id, company, country, damage_reason, quantity, reported_date)
        return jsonify({"message": "Damage log added successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_damaged_logs', methods=['GET'])
def get_damaged_logs():
    try:
        adjusted_data=damaged_db.fetch_all_rows()
        return render_template('damaged_logs_table.html', damaged_log_data=adjusted_data)

    except Exception as e:
        return f"Error: {e}", 500



if __name__ == '__main__':
    app.run(debug=True)





