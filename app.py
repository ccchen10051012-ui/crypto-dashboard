from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Jessica's Crypto Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0e1a; color: #fff; font-family: Arial, sans-serif; }
        .header { text-align: center; padding: 30px 20px 10px; }
        .header h1 { font-size: 26px; color: #f0b90b; letter-spacing: 2px; }
        .header p { color: #8b949e; margin-top: 6px; font-size: 13px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; padding: 16px 30px; max-width: 1200px; margin: 0 auto; }
        .card { background: linear-gradient(135deg, #161b22, #1f2937); border-radius: 14px; padding: 20px; border: 1px solid #30363d; }
        .card:hover { border-color: #f0b90b44; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .coin-name { font-size: 16px; font-weight: bold; }
        .coin-symbol { font-size: 11px; color: #8b949e; background: #21262d; padding: 3px 8px; border-radius: 20px; }
        .price { font-size: 30px; font-weight: bold; color: #f0b90b; margin-bottom: 8px; }
        .change { font-size: 14px; font-weight: bold; padding: 4px 10px; border-radius: 6px; display: inline-block; margin-bottom: 12px; }
        .up { color: #3fb950; background: rgba(63,185,80,0.1); }
        .down { color: #f85149; background: rgba(248,81,73,0.1); }
        .chart-container { height: 80px; }
        .footer { text-align: center; padding: 20px; color: #8b949e; font-size: 12px; }
        .dot { display: inline-block; width: 7px; height: 7px; background: #3fb950; border-radius: 50%; margin-right: 5px; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 Jessica's Crypto Dashboard</h1>
        <p><span class="dot"></span>实时数据 · 每30秒自动刷新 · 数据来源 CoinGecko</p >
    </div>
    <div class="grid" id="grid"></div>
    <div class="footer">Made by Jessica · Powered by Python Flask</div>

    <script>
        const charts = {};

        async function loadData() {
            const res = await fetch('/api/prices');
            const coins = await res.json();
            const grid = document.getElementById('grid');
            grid.innerHTML = '';

            coins.forEach(coin => {
                const div = document.createElement('div');
                div.className = 'card';
                div.innerHTML = `
                    <div class="card-header">
                        <span class="coin-name">${coin.name}</span>
                        <span class="coin-symbol">${coin.symbol}</span>
                    </div>
                    <div class="price">$${coin.price}</div>
                    <span class="change ${coin.change >= 0 ? 'up' : 'down'}">
                        ${coin.change >= 0 ? '▲' : '▼'} ${Math.abs(coin.change)}% (24h)
                    </span>
                    <div class="chart-container">
                        <canvas id="chart-${coin.id}"></canvas>
                    </div>
                `;
                grid.appendChild(div);

                const ctx = document.getElementById('chart-' + coin.id).getContext('2d');
                const color = coin.change >= 0 ? '#3fb950' : '#f85149';
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: coin.history_dates,
                        datasets: [{
                            data: coin.history_prices,
                            borderColor: color,
                            backgroundColor: color + '22',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 0,
                            borderWidth: 2
                        }]
                    },
                    options: {
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { display: false },
                            y: { display: false }
                        },
                        animation: false
                    }
                });
            });
        }

        loadData();
        setInterval(loadData, 30000);
    </script>
</body>
</html>
"""

COIN_IDS = ["bitcoin", "ethereum", "solana", "binancecoin", "dogecoin"]
COIN_NAMES = {"bitcoin": "Bitcoin", "ethereum": "Ethereum", "solana": "Solana", "binancecoin": "BNB", "dogecoin": "Dogecoin"}
COIN_SYMBOLS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "binancecoin": "BNB", "dogecoin": "DOGE"}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/prices")
def api_prices():
    try:
        # 当前价格
        price_url = "https://api.coingecko.com/api/v3/simple/price"
        price_params = {"ids": ",".join(COIN_IDS), "vs_currencies": "usd", "include_24hr_change": "true"}
        price_data = requests.get(price_url, params=price_params, timeout=10).json()

        coins = []
        for cid in COIN_IDS:
            # 7天历史
            hist_url = f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart"
            hist_params = {"vs_currency": "usd", "days": "7", "interval": "daily"}
            hist_data = requests.get(hist_url, params=hist_params, timeout=10).json()
            prices = [p[1] for p in hist_data.get("prices", [])]
            dates = [str(i) for i in range(len(prices))]

            coins.append({
                "id": cid,
                "name": COIN_NAMES[cid],
                "symbol": COIN_SYMBOLS[cid],
                "price": f"{price_data[cid]['usd']:,.2f}",
                "change": round(price_data[cid]["usd_24h_change"], 2),
                "history_prices": prices,
                "history_dates": dates
            })
        return jsonify(coins)
    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
