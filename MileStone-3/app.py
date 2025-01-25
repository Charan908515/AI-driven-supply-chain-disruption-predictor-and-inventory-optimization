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



    
@app.route("/run_prediction",methods=["GET"])
def adjust_inventory_and_predict_risk():
    risk_data_path=main() # call the main function from the milestone-2 module that returns the csv file path containing the data of the articles and the risk
    risk_data=pd.read_csv(risk_data_path) # csv file:risk_and_sentiment_results
    risk_data["Published At"]=pd.to_datetime(risk_data['Published At']).dt.date
    risk_data["Month"] = pd.to_datetime(risk_data["Published At"]).dt.month_name()
    summarizer = pipeline("summarization")
    products_database=db.fetch_all_rows()
    products=pd.DataFrame(products_database,columns=["id","company","month","cost_price","selling_price","country","stock_level"])
    for risk_id,risks in risk_data.iterrows():
        for product_id,data in products.iterrows():
            if data["company"] in risks["Title"].lower() and data["month"].lower()==risks["Month"]:
                stock_level=data["stock_level"]
                if risks["risk_score"]<0:  # risk score is between -1 to 1, -1 is for high risk and 1 for low risk
                    stock_adjustment = stock_level * -0.20  # Decrease by 20%
                    summary=summarizer(risks["Risk Analysis"], max_length=50, min_length=10, do_sample=False)
                    reason=summary[0]['summary_text']

                elif risks["risk_score"]>0:
                    stock_adjustment = stock_level * 0.05
                    summary=summarizer(risks["Risk Analysis"], max_length=50, min_length=10, do_sample=False)
                    reason=summary[0]['summary_text']   # increase by 5%
                else:
                    stock_adjustment = stock_level * 0.00
                    reason="there is no risk"
    
            
                new_stock = int(stock_level + stock_adjustment) 
                adjusted_db.insert(data["product_id"],data["company"],data["country"],data["stock_level"],new_stock,stock_adjustment,data["month"],reason)
    try:
        # Fetch all rows from the adjusted database
        adjusted_data = adjusted_db.fetch_all_rows()
        return render_template('adjusted_inventory.html', adjusted_data=adjusted_data)
    except Exception as e:
        return f"Error: {e}", 500

            



   




if __name__ == '__main__':
    app.run(debug=True)
