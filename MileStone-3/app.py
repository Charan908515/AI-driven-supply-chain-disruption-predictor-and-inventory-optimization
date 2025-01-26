from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import Database,Adjusted_database
import csv
from electric_batteries import main
import pandas as pd
from transformers import pipeline



app = Flask(__name__)

db = Database("products.db")
adjusted_db=Database("adjusted_data.db")

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
            if ["raw materials","climate change","lithium","cobalt","nickel"] in risk_row["Title"] and risk_row["risk_score"]<=0.5:
                for _, product_row in products.iterrows():
                    stock_level = product_row["stock_level"]
                    risk_score = risk_row["risk_score"]
                    stock_adjustment = stock_level * -0.30  # Decrease by 30%
                    alert = "sell"
                    summary = summarizer(risk_row["Risk Analysis"], max_length=50, min_length=10, do_sample=False)
                    reason = summary[0]['summary_text']
                    new_stock = int(stock_level + stock_adjustment)
                    adjusted_db.insert(
                        product_row["id"],
                        product_row["company"],
                        product_row["country"],
                        product_row["stock_level"],
                        new_stock,
                        stock_adjustment,
                        product_row["month"],
                        reason,
                        alert)      
                    
            break    
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



    



if __name__ == '__main__':
    app.run(debug=True)





