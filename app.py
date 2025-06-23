


from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
print(API_KEY)
print(ALPHA_VANTAGE_API_KEY)
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")

        if not user_message:
            return jsonify({"reply": "No message received."}), 400

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                f"You are a financial AI assistant. Format your response in Markdown. More on stocks and investments can be found at https://www.moneycontrol.com/india/stockpricequote/"
                                f"User query: {user_message}"
                            )
                        }
                    ]
                }
            ]
        }

        response = requests.post(GEMINI_URL, json=payload, timeout=10)

        response.raise_for_status()
        data = response.json()
        ai_message = data["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"reply": ai_message})

    except requests.exceptions.RequestException as req_err:
        print("Request error:", req_err)
        return jsonify({"reply": "Failed to contact Gemini API."}), 502

    except Exception as e:
        print("Server error:", e)
        return jsonify({"reply": "Something went wrong on the server."}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if not API_KEY:
            return jsonify({
                "success": False,
                "message": "Gemini API key not configured"
            }), 500

        print(f"[{datetime.now()}] Received analyze request from Express server")

        # Get portfolio data
        portfolio_data = request.json
        if not portfolio_data:
            return jsonify({
                "success": False,
                "message": "No portfolio data provided"
            }), 400

        portfolio_items = portfolio_data.get("portfolioItems", [])
        if not portfolio_items:
            return jsonify({
                "success": False,
                "message": "No portfolio items found to analyze"
            }), 400

        print(f"Processing {len(portfolio_items)} portfolio items...")

        # Basic metric calculation
        total_value = 0
        total_investment = 0
        for item in portfolio_items:
            quantity = float(item.get("quantity", 0))
            current_price = float(item.get("currentPrice", 0))
            avg_buy_price = float(item.get("avgBuyPrice", 0))
            total_value += quantity * current_price
            total_investment += quantity * avg_buy_price

        total_profit_loss = total_value - total_investment
        profit_loss_percentage = (total_profit_loss / total_investment * 100) if total_investment else 0

        holdings_text = "\n".join([
            f"{item.get('symbol', 'Unknown')}: {item.get('quantity', 0)} shares @ ₹{item.get('avgBuyPrice', 0):.2f} (Current: ₹{item.get('currentPrice', 0):.2f})"
            for item in portfolio_items
        ])

        # Prompt to Gemini
        prompt = f"""Analyze this investment portfolio and provide insights:

Portfolio Summary:
- Total Portfolio Value: ₹{total_value:.2f}
- Total Investment: ₹{total_investment:.2f}
- Total P/L: ₹{total_profit_loss:.2f} ({profit_loss_percentage:.2f}%)

Holdings:
{holdings_text}

Please provide a comprehensive analysis including:
1. Overall portfolio health assessment
2. Key risks and opportunities
3. Diversification analysis
4. Specific recommendations for improvement
5. Performance evaluation

Keep the analysis concise, actionable, and format your response in Markdown."""

        print("Calling Gemini AI...")

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ]
        }

        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": f"Bearer {API_KEY}"
        # }

        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        print("Gemini response received")

        # Parse AI response
        analysis = "Unable to generate analysis - unexpected API response"
        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                analysis = parts[0]["text"]
            else:
                print("Warning: Unexpected Gemini response format")
        else:
            print("Warning: No candidates returned by Gemini API")

        print("Returning AI analysis to client")
        return jsonify({
            "success": True,
            "metrics": {
                "totalValue": round(total_value, 2),
                "totalInvestment": round(total_investment, 2),
                "totalProfitLoss": round(total_profit_loss, 2),
                "profitLossPercentage": round(profit_loss_percentage, 2)
            },
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "itemsAnalyzed": len(portfolio_items)
        }), 200

    except requests.exceptions.Timeout:
        print("Gemini API request timed out")
        return jsonify({
            "success": False,
            "message": "Gemini API timed out. Try again."
        }), 504

    except requests.exceptions.RequestException as req_err:
        print(f"Gemini API request error: {req_err}")
        return jsonify({
            "success": False,
            "message": "Failed to contact Gemini API"
        }), 502

    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        return jsonify({
            "success": False,
            "message": "Unexpected server error"
        }), 500





# Your Alpha Vantage API key (use env variable or hardcode for testing)


# API Key
ALPHA_VANTAGE_API_KEY = os.getenv("AlphaVantage_API_KEY", "29X9YHVU0IAY0KCT")

# MongoDB setup
client = MongoClient("mongodb+srv://mahidharkarakala2405:a87UuNPxYkNwhiQN@cluster0.ghpwnzy.mongodb.net/")
db = client['test']
collection = db['daily_prices']

# Stock symbols with custom IDs
symbols = {
    "HDFC Bank": {"symbol": "HDFCBANK.BSE", "id": 4},
    "ICICI Bank": {"symbol": "ICICIBANK.BSE", "id": 6},
    "TCS": {"symbol": "TCS.BSE", "id": 2},
    "Reliance": {"symbol": "RELIANCE.BSE", "id": 1},
    "Wipro": {"symbol": "WIPRO.BSE", "id": 8},
    "Sun Pharma": {"symbol": "SUNPHARMA.BSE", "id": 9},
    "Kotak Bank": {"symbol": "KOTAKBANK.BSE", "id": 10},
    "Infosys": {"symbol": "INFY.BSE", "id": 3},
    "Bharti Airtel": {"symbol": "BHARTIARTL.BSE", "id": 5},
    "Tata Motors": {"symbol": "TATAMOTORS.BSE", "id": 7}
}

def fetch_stock_data(symbol_code):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol_code}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    quote = data.get("Global Quote", {})

    if not quote:
        return None

    try:
        return {
            "symbol": symbol_code,
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "changePercent": float(quote.get("10. change percent", "0%").strip('%')),
            "volume": float(quote.get("06. volume", 0)) / 1e6,  # Convert to millions
            "marketCap": None,
            "fetched_at": datetime.utcnow()
        }
    except (ValueError, TypeError):
        return None

@app.route('/fetch-daily-stock-data', methods=['GET'])
def fetch_and_store():
    today = datetime.utcnow().date()
    existing = collection.find_one({"fetched_at_date": str(today)})
    if existing:
        return jsonify({"status": "already_fetched", "message": "Data already fetched for today."})

    results = []
    for name, meta in symbols.items():
        symbol_code = meta["symbol"]
        stock_id = str(meta["id"])

        stock_data = fetch_stock_data(symbol_code)
        if stock_data:
            stock_data["name"] = name
            stock_data["id"] = str(stock_id)
            stock_data["fetched_at_date"] = str(today)
            inserted = collection.insert_one(stock_data)
            stock_data["_id"] = str(inserted.inserted_id)
            results.append(stock_data)

    return jsonify({
        "status": "success",
        "fetched_count": len(results),
        "data": results
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
