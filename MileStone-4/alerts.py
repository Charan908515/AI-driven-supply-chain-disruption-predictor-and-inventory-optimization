import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
import pandas as pd
from electric_batteries import compute_risk_score, main as fetch_risk_data  # MileStone-2 code
from database import Database, Adjusted_database  # MileStone-3 code


os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
# Database instances
db = Database("products.db")
adjusted_db = Adjusted_database("adjusted_data.db")

def send_email(alert, product_info):
    sender_email = "ncharankumareddy@gmail.com"
    sender_password ="ualc ovau fbrz stkd"
    recipient_email = "freefire908515@gmail.com"

    subject = f"Alert: {alert.upper()} Action Required for {product_info['company']}"
    body = f"""
    Alert: {alert.upper()}
    Product ID: {product_info['product_id']}
    Company: {product_info['company']}
    Country: {product_info['country']}
    Stock Level: {product_info['stock_level']}
    Stock Adjusted: {product_info['stock_adjusted']}
    Risk Score: {product_info['risk_score']}
    Reason: {product_info['reason']}
    """

    # Compose email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail server and send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_slack_notification(alert, product_info):
    webhook_url = "https://hooks.slack.com/services/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"

    message = {
        "text": f"""
        Alert: {alert.upper()}
        Product ID: {product_info['product_id']}
        Company: {product_info['company']}
        Country: {product_info['country']}
        Stock Level: {product_info['stock_level']}
        Stock Adjusted: {product_info['stock_adjusted']}
        Risk Score: {product_info['risk_score']}
        Reason: {product_info['reason']}
        """
    }

    try:
        response = requests.post(webhook_url, json=message)
        if response.status_code == 200:
            print("Slack notification sent successfully.")
        else:
            print(f"Failed to send Slack notification: {response.text}")
    except Exception as e:
        print(f"Error sending Slack notification: {e}")

def generate_alerts():
    try:
        # Fetch risk data using electric_batteries module
        risk_data_path = fetch_risk_data()
        risk_data = pd.read_csv(risk_data_path)
        risk_data["Published At"] = pd.to_datetime(risk_data["Published At"]).dt.date
        risk_data["Month"] = pd.to_datetime(risk_data["Published At"]).dt.month_name().str.lower()

        
       

        # Fetch products from database
        products = db.fetch_all_rows()
        minimum_stock=500
        for product in products:
            product_id, company, month, cost_price, selling_price, country, stock_level = product


            # Match product with risk data
            matching_risks = risk_data[(risk_data['Title'].str.contains(company, case=False)) & (risk_data['Month'].str.contains(month, case=False))]
                              

            if not matching_risks.empty:
                # Compute risk score
                risk_score = compute_risk_score(matching_risks.iloc[0]['Risk Analysis'])
            else:
                risk_score = 0.0  # Default to no risk if no matching risks

            # Determine alert based on risk score and stock level
            if risk_score <= -0.5 and stock_level > minimum_stock:
                alert = "sell"
                reason = "High risk detected and stock level above optimal range."
            elif risk_score <= -0.5 and stock_level <= minimum_stock:
                alert = "monitor"
                reason = "High risk detected, but stock level is manageable."
            elif -0.5 < risk_score < 0.5 and stock_level < minimum_stock:
                alert = "buy"
                reason = "Moderate risk detected and stock level below threshold."
            elif risk_score >= 0.5 and stock_level < minimum_stock:
                alert = "buy"
                reason = "Low risk detected and stock level below threshold."
            else:
                alert = "monitor"
                reason = "Conditions are stable."

            stock_adjusted = stock_level  # Adjust as needed

            # Prepare product information for alerts
            product_info = {
                "product_id": product_id,
                "company": company,
                "country": country,
                "stock_level": stock_level,
                "stock_adjusted": stock_adjusted,
                "risk_score": risk_score,
                "reason": reason
            }

            # Send email and Slack notifications
            send_email(alert, product_info)
            send_slack_notification(alert, product_info)

    except Exception as e:
        print(f"Error generating alerts: {e}")

if __name__ == "__main__":
    while True: # generate the alerts for every 2 days
        generate_alerts()
        seconds=2*24*60*60 
        time.sleep(seconds)
