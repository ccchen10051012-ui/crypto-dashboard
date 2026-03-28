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
    <script src="https://cdn.jsdelivr.net/npm/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0e1a; color: #fff; font-family: Arial, sans-serif; }
        .header { text-align: center; padding: 24px 20px 10px; }
        .header h1 { font-size: 24px; color: #f0b90b; letter-spacing: 2px; }
        .header p { color: #8b949e; margin-top: 6px; font-size: 13px; }
        .tabs { display: flex; justify-content: center; gap: 10px; padding: 16px; flex-wrap: wrap; }
        .tab { padding: 8px 20px; border-radius: 20px; cursor: pointer; font-size: 14px; border: 1px solid #30363d; background: #161b22; color: #8b949e; }
        .tab.active { background: #f0b90b; color: #000; font-weight: bold; border-color: #f0b90b; }
        .price-bar { display: flex; justify-content: center; gap: 30px; padding: 10px 20px; flex-wrap: wrap; }
        .price-item { text-align: center; }
        .price-item .label { font-size: 11px; color: #8b949e; }
        .price-item .value { font-size: 20px; font-weight: bold; color: #f0b90b; }
        .price-item .change { font-size: 13px; font-weight: bold; }
        .up { color: #3fb950; }
        .down { color: #f85149; }
        .chart-wrap { padding: 0 20px 10px; max-width: 1100px; margin: 0 auto; }
        #chart { width: 100%; height: 400px; border-radius: 12px; overflow: hidden; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; padding: 12px 20px; max-width: 1100px; margin: 0 auto; }
        .card { background: #161b22; border-radius: 12px; padding: 16px; border: 1px solid #30363d; cursor: pointer; }
        .card:hover, .card.active { border-color: #f0b90b; }
        .card .name { font-size: 13px; color: #8b949e; }
        .card .price { font-size: 20px; font-weight: bold; color: #f0b90b; margin: 4px 0; }
        .footer { text-align: center; padding: 16px; color: #8b949e; font-size: 12px; }
        .dot { display: inline-block; width: 7px; height: 7px; background: #3fb950; border-radius: 50%; margin-right: 5px; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 Jessica's Crypto Dashboard</h1>
        <p><span class="dot"></span>实时数据 · 每30秒自动刷新</p >
    </div>

    <div class="price-bar" id="priceBar"></div>

    <div class="chart-wrap">
        <div id="chart"></div>
    </div>

    <div class="grid" id="grid"></div>
    <div class="footer">Made by Jessica · Powered by Python Flask · Data by CoinGecko</div>

<script>
let allData = [];
let currentCoin = 'bitcoin';
let chart, candleSeries;

function initChart() {
    chart = LightweightCharts.createChart(document.getElementById('chart'), {
        width: document.getElementById('chart').clientWidth,
        height: 400,
        layout: { background: { color: '#161b22' }, textColor: '#8b949e' },
        grid: { vertLines: { color: '#21262d' }, horzLines: { color: '#21262d' } },
        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
        rightPriceScale: { borderColor: '#30363d' },
        timeScale: { borderColor: '#30363d', timeVisible: true },
    });
    candleSeries = chart.addCandlestickSeries({
        upColor: '#3fb950', downColor: '#f85149',
        borderUpColor: '#3fb950', borderDownColor: '#f85149',
        wickUpColor: '#3fb950', wickDownColor: '#f85149',
    });
}

function updateChart(coinId) {
    currentCoin = coinId;
    const coin = allData.find(c => c.id === coinId);
    if (!coin || !candleSeries) return;
    candleSeries.setData(coin.candles);
    chart.timeScale().fitContent();

    document.querySelectorAll('.card').forEach(c => {
        c.classList.toggle('active', c.dataset.id === coinId);
    });
}

async function loadData() {
    const res = await fetch('/api/prices');
    allData = await res.json();

    // Price bar
    const bar = document.getElementById('priceBar');
    bar.innerHTML = allData.map(c => `
        <div class="price-item">
            <div class="label">${c.symbol}</div>
            <div class="value">$${c.price}</div>
            <div class="change ${c.change >= 0 ? 'up' : 'down'}">${c.change >= 0 ? '▲' : '▼'} ${Math.abs(c.change)}%</div>
        </div>
    `).join('');

    // Cards
    const grid = document.getElementById('grid');
    grid.innerHTML = allData.map(c => `
        <div class="card ${c.id === currentCoin ? 'active' : ''}" data-id="${c.id}" onclick="updateChart('${c.id}')">
            <div class="name">${c.name} · ${c.symbol}</div>
            <div class="price">$${c.price}</div>
            <div class="change ${c.change >= 0 ? 'up' : 'down'}">${c.change >= 0 ? '▲' : '▼'} ${Math.abs(c.change)}% (24h)</div>
        </div>
    `).join('');

    updateChart(currentCoin);
}

initChart();
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
        price_url = "https://api.coingecko.com/api/v3/simple/price"
        price_params = {"ids": ",".join(COIN_IDS), "vs_currencies": "usd", "include_24hr_change": "true"}
        price_data = requests.get(price_url, params=price_params, timeout=10).json()

        coins = []
        for cid in COIN_IDS:
            hist_url = f"https://api.coingecko.com/api/v3/coins/{cid}/ohlc"
            hist_params = {"vs_currency": "usd", "days": "30"}
            hist_data = requests.get(hist_url, params=hist_params, timeout=10).json()

            candles = []
            for item in hist_data:
                candles.append({
                    "time": item[0] // 1000,
                    "open": item[1],
                    "high": item[2],
                    "low": item[3],
                    "close": item[4]
                })

            coins.append({
                "id": cid,
                "name": COIN_NAMES[cid],
                "symbol": COIN_SYMBOLS[cid],
                "price": f"{price_data[cid]['usd']:,.2f}",
                "change": round(price_data[cid]["usd_24h_change"], 2),
                "candles": candles
            })
        return jsonify(coins)
    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
