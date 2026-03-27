from flask import Flask, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>加密货币监控</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0e1a; color: #fff; font-family: 'Arial', sans-serif; min-height: 100vh; }
        .header { text-align: center; padding: 40px 20px 20px; }
        .header h1 { font-size: 28px; color: #f0b90b; letter-spacing: 2px; }
        .header p { color: #8b949e; margin-top: 8px; font-size: 14px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; padding: 20px 40px; max-width: 1200px; margin: 0 auto; }
        .card { background: linear-gradient(135deg, #161b22, #1f2937); border-radius: 16px; padding: 24px; border: 1px solid #30363d; transition: transform 0.2s; }
        .card:hover { transform: translateY(-4px); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .coin-name { font-size: 18px; font-weight: bold; color: #e6edf3; }
        .coin-symbol { font-size: 12px; color: #8b949e; background: #21262d; padding: 4px 10px; border-radius: 20px; }
        .price { font-size: 36px; font-weight: bold; color: #f0b90b; margin-bottom: 12px; }
        .change { font-size: 16px; font-weight: bold; padding: 6px 12px; border-radius: 8px; display: inline-block; }
        .up { color: #3fb950; background: rgba(63,185,80,0.1); }
        .down { color: #f85149; background: rgba(248,81,73,0.1); }
        .footer { text-align: center; padding: 30px; color: #8b949e; font-size: 13px; }
        .dot { display: inline-block; width: 8px; height: 8px; background: #3fb950; border-radius: 50%; margin-right: 6px; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    </style>
    <script>setTimeout(() => location.reload(), 30000);</script>
</head>
<body>
    <div class="header">
        <h1>💰 加密货币实时监控</h1>
        <p><span class="dot"></span>数据实时更新 · 每30秒自动刷新</p >
    </div>
    <div class="grid">
        {% for coin in coins %}
        <div class="card">
            <div class="card-header">
                <span class="coin-name">{{ coin.name }}</span>
                <span class="coin-symbol">{{ coin.symbol }}</span>
            </div>
            <div class="price">${{ coin.price }}</div>
            <span class="change {{ coin.change_class }}">
                {{ coin.change_icon }} {{ coin.change }}% (24h)
            </span>
        </div>
        {% endfor %}
    </div>
    <div class="footer">数据来源：CoinGecko · Jessica's Crypto Dashboard</div>
</body>
</html>
"""

@app.route("/")
def index():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana,binancecoin,dogecoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        data = requests.get(url, params=params, timeout=10).json()

        coin_map = [
            ("bitcoin", "Bitcoin", "BTC"),
            ("ethereum", "Ethereum", "ETH"),
            ("solana", "Solana", "SOL"),
            ("binancecoin", "BNB", "BNB"),
            ("dogecoin", "Dogecoin", "DOGE"),
        ]

        coins = []
        for cid, name, symbol in coin_map:
            price = data[cid]["usd"]
            change = round(data[cid]["usd_24h_change"], 2)
            coins.append({
                "name": name,
                "symbol": symbol,
                "price": f"{price:,.2f}",
                "change": change,
                "change_class": "up" if change >= 0 else "down",
                "change_icon": "▲" if change >= 0 else "▼"
            })
    except Exception as e:
        coins = []

    return render_template_string(HTML, coins=coins)

if __name__ == "__main__":
    app.run(debug=True)
