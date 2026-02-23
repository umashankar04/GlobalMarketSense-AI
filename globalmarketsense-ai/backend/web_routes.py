from fastapi import APIRouter
from fastapi.responses import HTMLResponse


web_router = APIRouter(tags=["web"])


@web_router.get("/", response_class=HTMLResponse)
def localhost_dashboard() -> str:
    return """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>GlobalMarketSense AI</title>
  <script src=\"https://cdn.plot.ly/plotly-2.35.2.min.js\"></script>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0a0f19;
      --panel: #111827;
      --panel-2: #0f172a;
      --line: #263446;
      --text: #e6edf5;
      --muted: #91a4bc;
      --green: #22c55e;
      --red: #ef4444;
      --amber: #f59e0b;
      --cyan: #22d3ee;
      --violet: #a78bfa;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: radial-gradient(circle at 20% 0%, #14223a 0%, var(--bg) 40%);
      color: var(--text);
    }
    .container { max-width: 1520px; margin: 0 auto; padding: 14px; }
    .topbar {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
      margin-bottom: 12px;
    }
    .brand { display: flex; gap: 10px; align-items: center; }
    .logo {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(145deg, #4f46e5, #06b6d4);
      box-shadow: 0 0 24px rgba(79, 70, 229, 0.38);
    }
    .title { font-size: 26px; font-weight: 800; letter-spacing: 0.2px; }
    .subtitle { font-size: 12px; color: var(--muted); margin-top: 2px; }
    .tools { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
    .pill {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 12px;
      color: #b8c8db;
      background: rgba(17, 24, 39, 0.62);
    }
    .ctl {
      border: 1px solid var(--line);
      border-radius: 9px;
      background: var(--panel);
      color: var(--text);
      padding: 7px 10px;
      min-width: 88px;
    }
    button.ctl { cursor: pointer; }
    .status { font-weight: 700; }
    .status.ok { color: var(--green); }
    .status.bad { color: var(--red); }

    .kpis {
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }
    .card {
      background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }
    .card-soft {
      background: linear-gradient(180deg, rgba(20, 31, 48, 0.9) 0%, rgba(14, 22, 35, 0.92) 100%);
    }
    .kpi-title { color: var(--muted); font-size: 12px; }
    .kpi-value { margin-top: 8px; font-size: 22px; font-weight: 800; }
    .kpi-delta { margin-top: 6px; font-size: 12px; }
    .up { color: var(--green); }
    .down { color: var(--red); }
    .flat { color: var(--amber); }

    .grid-main {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }
    .grid-secondary {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }
    .chart { width: 100%; height: 340px; }
    .chart-sm { width: 100%; height: 300px; }
    .card h3 {
      margin: 0 0 10px 0;
      font-size: 14px;
      letter-spacing: 0.2px;
      color: #c2d0e0;
    }
    .meta {
      display: grid;
      gap: 8px;
      margin-bottom: 12px;
    }
    .meta-row { display: flex; justify-content: space-between; color: #b5c4d6; font-size: 13px; }
    .risk-pill {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      font-weight: 700;
      font-size: 11px;
    }
    .risk-low { color: var(--green); }
    .risk-mid { color: var(--amber); }
    .risk-high { color: var(--red); }
    .watchlist { display: grid; gap: 8px; }
    .watch-item {
      display: flex;
      justify-content: space-between;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 8px 10px;
      background: rgba(12, 18, 30, 0.82);
    }

    table { width: 100%; border-collapse: collapse; }
    thead th {
      text-align: left;
      color: #9eb0c7;
      font-size: 12px;
      border-bottom: 1px solid var(--line);
      padding: 8px 6px;
      font-weight: 600;
    }
    tbody td {
      border-bottom: 1px solid #1f2a3a;
      padding: 8px 6px;
      font-size: 13px;
    }
    tbody tr:nth-child(odd) { background: rgba(16, 25, 39, 0.36); }
    tbody tr:hover { background: rgba(33, 52, 74, 0.35); }
    .signal-buy { color: var(--green); font-weight: 700; }
    .signal-hold { color: var(--amber); font-weight: 700; }
    .signal-sell { color: var(--red); font-weight: 700; }
    .footer { margin-top: 8px; text-align: right; font-size: 12px; color: var(--muted); }

    @media (max-width: 1200px) {
      .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .grid-main { grid-template-columns: 1fr; }
      .grid-secondary { grid-template-columns: 1fr; }
    }
    @media (max-width: 760px) {
      .topbar { grid-template-columns: 1fr; }
      .tools { justify-content: flex-start; }
      .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <div class=\"container\">
          <div class="subtitle">Institutional-grade sentiment and risk intelligence across US, India, and crypto markets</div>
      <div class="brand">
        <div class="logo"></div>
        <div>
          <div class="title">GlobalMarketSense AI Terminal</div>
        <span class="pill">localhost trading mode</span>
        <span id="apiStatus" class="pill">API: Checking...</span>
        <span id="updatedPill" class="pill">Updated: --</span>
      </div>
      <div class="tools">
        <span id=\"clockPill\" class=\"pill\">--:--:--</span>
        <span class="pill">localhost trading mode</span>
        <span id="apiStatus" class="pill">API: --</span>
        <select id=\"marketSelect\" class=\"ctl\">
          <option>SP500</option>
          <option>NIFTY50</option>
          <option>SENSEX</option>
          <option>BTC</option>
          <option>NASDAQ</option>
        </select>
        <select id="windowSelect" class="ctl">
          <option value="60">1M</option>
          <option value="120">2M</option>
          <option value="220" selected>3M+</option>
        </select>
        <select id=\"refreshSelect\" class=\"ctl\">
          <option value=\"3000\">3s</option>
          <option value=\"6000\" selected>6s</option>
          <option value=\"10000\">10s</option>
          <option value=\"15000\">15s</option>
        </select>
        <button id=\"toggleBtn\" class=\"ctl btn\">Pause</button>
      </div>
    </div>

    <div id="kpiGrid" class="kpis"></div>

    <div class="grid-main">
      <div class="card card-soft">
        <h3>Price Sentiment Trend</h3>
        <div id="trendChart" class="chart"></div>
      </div>
      <div class="card card-soft">
        <h3>Risk Meter</h3>
        <div id="gaugeChart" class="chart-sm"></div>
        <div class="meta">
          <div class="meta-row"><span>Selected Market</span><strong id="selectedMarket">SP500</strong></div>
          <div class="meta-row"><span>Risk Probability</span><strong id="riskProb">-</strong></div>
          <div class="meta-row"><span>Volatility Proxy</span><strong id="volProxy">-</strong></div>
          <div class="meta-row"><span>Signal</span><span id="riskSignal" class="risk-pill">-</span></div>
        </div>
        <h3 style="margin-top:14px">Watchlist Snapshot</h3>
        <div id="watchlist" class="watchlist"></div>
      </div>
    </div>

    <div class="grid-secondary">
      <div class="card card-soft">
        <h3>Sentiment Heatmap</h3>
        <div id="heatChart" class="chart-sm"></div>
      </div>
      <div class="card card-soft">
        <h3>Market Correlation Matrix</h3>
        <div id="corrChart" class="chart-sm"></div>
      </div>
    </div>

    <div class="card card-soft">
      <h3>Realtime Sentiment Feed</h3>
        <table>
          <thead><tr><th>Market</th><th>Date</th><th>Sentiment</th><th>Signal</th><th>Updated</th></tr></thead>
          <tbody id=\"feedBody\"></tbody>
        </table>
    </div>
    <div class="footer">GlobalMarketSense AI · Advanced Local Trading Dashboard</div>
  </div>

  <script>
    const markets = ["SP500", "NIFTY50", "SENSEX", "BTC", "NASDAQ"];
    const palette = ["#22d3ee", "#a78bfa", "#22c55e", "#f59e0b", "#f43f5e"];
    let refreshMs = 6000;
    let windowLimit = 220;
    let timer = null;
    let running = true;

    function getSignalClass(signal) {
      if (!signal) return 'signal-hold';
      const value = String(signal).toLowerCase();
      if (value.includes('buy') || value.includes('bull')) return 'signal-buy';
      if (value.includes('sell') || value.includes('bear')) return 'signal-sell';
      return 'signal-hold';
    }

    async function fetchJson(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error('Request failed: ' + url);
      return res.json();
    }

    function groupLatest(rows) {
      const latest = new Map();
      const previous = new Map();
      rows.forEach((row) => {
        const m = row.market;
        if (!latest.has(m)) latest.set(m, row);
        else if (!previous.has(m)) previous.set(m, row);
      });
      return { latest, previous };
    }

    function toNumber(value) {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : 0;
    }

    function renderKpis(rows, selectedMarket, risk) {
      const { latest, previous } = groupLatest(rows);
      const selectedNow = latest.get(selectedMarket) ? toNumber(latest.get(selectedMarket).sentiment_index) : 0;
      const selectedPrev = previous.get(selectedMarket) ? toNumber(previous.get(selectedMarket).sentiment_index) : selectedNow;
      const netDirection = selectedNow - selectedPrev;

      const marketAverage = markets.reduce((acc, market) => {
        return acc + (latest.get(market) ? toNumber(latest.get(market).sentiment_index) : 0);
      }, 0) / markets.length;

      const strongest = markets.reduce((best, m) => {
        const value = latest.get(m) ? toNumber(latest.get(m).sentiment_index) : -999;
        return value > best.value ? { market: m, value } : best;
      }, { market: '-', value: -999 });

      const weakest = markets.reduce((best, m) => {
        const value = latest.get(m) ? toNumber(latest.get(m).sentiment_index) : 999;
        return value < best.value ? { market: m, value } : best;
      }, { market: '-', value: 999 });

      const riskPct = toNumber(risk.risk_probability) * 100;
      const kpiData = [
        { title: selectedMarket + ' Sentiment', value: selectedNow.toFixed(3), delta: netDirection },
        { title: 'Market Breadth', value: marketAverage.toFixed(3), delta: marketAverage - selectedNow },
        { title: 'Risk Probability', value: riskPct.toFixed(2) + '%', delta: toNumber(risk.volatility_proxy) },
        { title: 'Volatility Proxy', value: toNumber(risk.volatility_proxy).toFixed(4), delta: toNumber(risk.volatility_proxy) - 0.15 },
        { title: 'Sentiment Leader', value: strongest.market + ' ' + strongest.value.toFixed(3), delta: strongest.value },
        { title: 'Sentiment Laggard', value: weakest.market + ' ' + weakest.value.toFixed(3), delta: weakest.value }
      ];

      const grid = document.getElementById('kpiGrid');
      grid.innerHTML = kpiData.map((item) => {
        const delta = toNumber(item.delta);
        const deltaSign = delta > 0 ? '+' : '';
        const tone = delta > 0.00001 ? 'up' : (delta < -0.00001 ? 'down' : 'flat');
        const deltaText = tone === 'flat' ? 'No major shift' : (deltaSign + delta.toFixed(4) + ' momentum');
        return '<div class="card">'
          + '<div class="kpi-title">' + item.title + '</div>'
          + '<div class="kpi-value">' + item.value + '</div>'
          + '<div class="kpi-delta ' + tone + '">' + deltaText + '</div>'
          + '</div>';
      }).join('');
    }

    function renderWatchlist(rows) {
      const { latest } = groupLatest(rows);
      const html = markets.map((market) => {
        const value = latest.get(market) ? toNumber(latest.get(market).sentiment_index) : 0;
        const tone = value > 0 ? 'up' : (value < 0 ? 'down' : 'flat');
        const prefix = value > 0 ? '+' : '';
        return '<div class="watch-item">'
          + '<span>' + market + '</span>'
          + '<strong class="' + tone + '">' + prefix + value.toFixed(3) + '</strong>'
          + '</div>';
      }).join('');
      document.getElementById('watchlist').innerHTML = html;
    }

    function renderFeed(rows) {
      const body = document.getElementById('feedBody');
      const tableRows = rows.slice(0, 50).map((row) => {
        const sentiment = toNumber(row.sentiment_index);
        const signal = sentiment > 0.12 ? 'BUY' : (sentiment < -0.12 ? 'SELL' : 'HOLD');
        const cls = getSignalClass(signal);
        return '<tr>'
          + '<td>' + (row.market || '-') + '</td>'
          + '<td>' + (row.sentiment_date || '-') + '</td>'
          + '<td>' + sentiment.toFixed(4) + '</td>'
          + '<td class="' + cls + '">' + signal + '</td>'
          + '<td>' + (row.updated_at || '-') + '</td>'
          + '</tr>';
      }).join('');
      body.innerHTML = tableRows || '<tr><td colspan="5">No feed data available.</td></tr>';
    }

    function prepPivot(rows) {
      const byDate = {};
      rows.forEach((row) => {
        const date = row.sentiment_date;
        if (!date) return;
        if (!byDate[date]) byDate[date] = { sentiment_date: date };
        byDate[date][row.market] = toNumber(row.sentiment_index);
      });
      return Object.values(byDate).sort((a, b) => a.sentiment_date.localeCompare(b.sentiment_date));
    }

    function drawTrend(rows, selectedMarket) {
      const pivot = prepPivot(rows);
      const x = pivot.map((row) => row.sentiment_date);
      const traces = markets.map((market, idx) => {
        const isSelected = market === selectedMarket;
        return {
          x,
          y: pivot.map((row) => row[market] ?? null),
          mode: 'lines',
          name: market,
          line: {
            width: isSelected ? 3.2 : 1.6,
            color: palette[idx],
            dash: isSelected ? 'solid' : 'dot'
          },
          opacity: isSelected ? 1 : 0.7
        };
      });

      Plotly.react('trendChart', traces, {
        margin: { l: 40, r: 20, t: 20, b: 35 },
        paper_bgcolor: '#0f172a',
        plot_bgcolor: '#0f172a',
        font: { color: '#c8d7ea' },
        yaxis: { gridcolor: '#1f2a3a', zerolinecolor: '#304156' },
        xaxis: { gridcolor: '#1f2a3a' },
        legend: { orientation: 'h', y: 1.16, x: 0 }
      }, { displayModeBar: false, responsive: true });
    }

    function drawHeatAndCorrelation(rows) {
      const pivot = prepPivot(rows);
      const x = pivot.map((row) => row.sentiment_date);
      const z = markets.map((market) => x.map((_, i) => {
        const row = pivot[i] || {};
        return row[market] ?? 0;
      }));

      Plotly.react('heatChart', [{
        type: 'heatmap',
        z,
        x,
        y: markets,
        colorscale: [
          [0.0, '#7f1d1d'],
          [0.5, '#1e293b'],
          [1.0, '#14532d']
        ]
      }], {
        margin: { l: 52, r: 16, t: 20, b: 30 },
        paper_bgcolor: '#0f172a',
        plot_bgcolor: '#0f172a',
        font: { color: '#c8d7ea' }
      }, { displayModeBar: false, responsive: true });

      const corr = markets.map((a) => markets.map((b) => {
        const pair = pivot
          .map((row) => [row[a], row[b]])
          .filter((values) => Number.isFinite(values[0]) && Number.isFinite(values[1]));
        if (pair.length < 2) return 0;

        const n = pair.length;
        const ax = pair.reduce((acc, values) => acc + values[0], 0) / n;
        const by = pair.reduce((acc, values) => acc + values[1], 0) / n;
        const num = pair.reduce((acc, values) => acc + (values[0] - ax) * (values[1] - by), 0);
        const denA = Math.sqrt(pair.reduce((acc, values) => acc + (values[0] - ax) ** 2, 0));
        const denB = Math.sqrt(pair.reduce((acc, values) => acc + (values[1] - by) ** 2, 0));
        if (!denA || !denB) return 0;
        return num / (denA * denB);
      }));

      Plotly.react('corrChart', [{
        type: 'heatmap',
        z: corr,
        x: markets,
        y: markets,
        zmin: -1,
        zmax: 1,
        colorscale: [
          [0.0, '#7f1d1d'],
          [0.5, '#1e293b'],
          [1.0, '#14532d']
        ]
      }], {
        margin: { l: 52, r: 16, t: 20, b: 40 },
        paper_bgcolor: '#0f172a',
        plot_bgcolor: '#0f172a',
        font: { color: '#c8d7ea' }
      }, { displayModeBar: false, responsive: true });
    }

    function drawGauge(probability) {
      const value = Math.max(0, Math.min(100, toNumber(probability) * 100));
      Plotly.react('gaugeChart', [{
        type: 'indicator',
        mode: 'gauge+number',
        value,
        number: { suffix: '%' },
        gauge: {
          axis: { range: [0, 100] },
          bar: { color: '#22d3ee' },
          steps: [
            { range: [0, 35], color: '#14532d' },
            { range: [35, 70], color: '#78350f' },
            { range: [70, 100], color: '#7f1d1d' }
          ]
        }
      }], {
        margin: { l: 10, r: 10, t: 10, b: 10 },
        paper_bgcolor: '#0f172a',
        font: { color: '#c8d7ea' }
      }, { displayModeBar: false, responsive: true });
    }

    function applyRiskSignal(signal) {
      const node = document.getElementById('riskSignal');
      node.className = 'risk-pill';
      const value = String(signal || 'HOLD').toUpperCase();
      node.textContent = value;
      if (value.includes('BUY') || value.includes('LOW')) node.classList.add('risk-low');
      else if (value.includes('SELL') || value.includes('HIGH')) node.classList.add('risk-high');
      else node.classList.add('risk-mid');
    }

    function updateStatus(healthStatus) {
      const ok = healthStatus === 'ok';
      const apiStatus = document.getElementById('apiStatus');
      apiStatus.textContent = ok ? 'API: Online' : 'API: Offline';
      apiStatus.className = ok ? 'pill status ok' : 'pill status bad';
    }

    function stampUpdatedNow() {
      document.getElementById('updatedPill').textContent = 'Updated: ' + new Date().toLocaleTimeString();
    }

    async function refresh() {
      const selectedMarket = document.getElementById('marketSelect').value;
      document.getElementById('selectedMarket').textContent = selectedMarket;

      try {
        const [health, daily, risk] = await Promise.all([
          fetchJson('/api/health'),
          fetchJson('/api/sentiment/daily?limit=' + windowLimit),
          fetchJson('/api/risk/index/' + selectedMarket)
        ]);

        updateStatus(health.status);

        const rows = (daily.rows || []).slice().sort((a, b) => {
          const da = String(a.sentiment_date || '');
          const db = String(b.sentiment_date || '');
          if (da === db) return 0;
          return da > db ? -1 : 1;
        });

        document.getElementById('riskProb').textContent = (toNumber(risk.risk_probability) * 100).toFixed(2) + '%';
        document.getElementById('volProxy').textContent = toNumber(risk.volatility_proxy).toFixed(4);
        applyRiskSignal(risk.signal || 'HOLD');

        renderKpis(rows, selectedMarket, risk);
        renderWatchlist(rows);
        renderFeed(rows);
        drawTrend(rows, selectedMarket);
        drawHeatAndCorrelation(rows);
        drawGauge(risk.risk_probability);
        stampUpdatedNow();
      } catch (error) {
        updateStatus('offline');
      }
    }

    function applyRefreshRate() {
      refreshMs = Number(document.getElementById('refreshSelect').value);
      if (timer) clearInterval(timer);
      if (running) timer = setInterval(refresh, refreshMs);
    }

    function setupControls() {
      document.getElementById('refreshSelect').addEventListener('change', applyRefreshRate);
      document.getElementById('windowSelect').addEventListener('change', () => {
        windowLimit = Number(document.getElementById('windowSelect').value);
        refresh();
      });
      document.getElementById('marketSelect').addEventListener('change', refresh);
      document.getElementById('toggleBtn').addEventListener('click', () => {
        running = !running;
        document.getElementById('toggleBtn').textContent = running ? 'Pause' : 'Resume';
        if (running) {
          refresh();
          applyRefreshRate();
        } else if (timer) {
          clearInterval(timer);
        }
      });
    }

    function startClock() {
      const updateClock = () => {
        document.getElementById('clockPill').textContent = new Date().toLocaleTimeString();
      };
      updateClock();
      setInterval(updateClock, 1000);
    }

    setupControls();
    startClock();
    refresh();
    timer = setInterval(refresh, refreshMs);
  </script>
</body>
</html>
    """

@web_router.get("/markets", response_class=HTMLResponse)
def global_markets_dashboard() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MoneyControl Pro - Complete Market Intelligence</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #0a0e1a;
      --panel: #111827;
      --line: #2d3a4e;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --green: #10b981;
      --red: #ef4444;
      --amber: #f59e0b;
      --blue: #3b82f6;
      --cyan: #06b6d4;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(to bottom, #0a0e1a, #0d1117);
      color: var(--text);
    }
    .wrapper { min-height: 100vh; }
    .container { max-width: 1920px; margin: 0 auto; padding: 20px; }
    .top-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(17, 24, 39, 0.6);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--line);
      padding: 16px 20px;
      margin: -20px -20px 20px -20px;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .logo-section h1 {
      font-size: 24px;
      font-weight: 900;
      background: linear-gradient(to right, var(--cyan), var(--blue));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .logo-section p { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
    .header-stats { display: flex; gap: 20px; }
    .stat-box { display: flex; flex-direction: column; align-items: flex-end; }
    .stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; }
    .stat-value { font-size: 18px; font-weight: 700; margin-top: 4px; }
    .stat-up { color: var(--green); }
    .stat-down { color: var(--red); }
    .nav-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--line);
      overflow-x: auto;
      padding-bottom: 12px;
    }
    .nav-tab {
      padding: 10px 16px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      white-space: nowrap;
    }
    .nav-tab.active {
      color: var(--cyan);
      border-bottom-color: var(--cyan);
    }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }
    .summary-card {
      background: rgba(17, 24, 39, 0.8);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      transition: all 0.2s;
    }
    .summary-card:hover { border-color: var(--cyan); }
    .card-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
    .card-value { font-size: 22px; font-weight: 800; margin-top: 6px; }
    .card-change { font-size: 12px; margin-top: 6px; }
    .card-change.up { color: var(--green); }
    .card-change.down { color: var(--red); }
    .section-card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 16px;
    }
    .section-header {
      padding: 16px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .section-title { font-size: 16px; font-weight: 700; }
    .section-body { padding: 16px; }
    .stock-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 12px;
    }
    .stock-card {
      background: rgba(30, 41, 59, 0.5);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      transition: all 0.2s;
      cursor: pointer;
    }
    .stock-card:hover {
      border-color: var(--cyan);
      background: rgba(17, 24, 39, 0.8);
      transform: translateY(-2px);
    }
    .stock-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px; }
    .stock-symbol { font-weight: 700; font-size: 13px; }
    .stock-name { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
    .stock-price { font-size: 18px; font-weight: 800; margin: 8px 0; }
    .stock-metrics {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      font-size: 11px;
      margin-bottom: 8px;
    }
    .metric { background: rgba(255, 255, 255, 0.05); padding: 6px; border-radius: 4px; text-align: center; }
    .metric-label { color: var(--text-muted); font-size: 10px; }
    .metric-value { font-weight: 600; margin-top: 2px; }
    .badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 600;
    }
    .badge-green { background: rgba(16, 185, 129, 0.2); color: var(--green); }
    .badge-red { background: rgba(239, 83, 80, 0.2); color: var(--red); }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .data-table th {
      text-align: left;
      padding: 12px;
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-muted);
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      border-bottom: 1px solid var(--line);
    }
    .data-table td {
      padding: 12px;
      border-bottom: 1px solid var(--line);
    }
    .data-table tbody tr:hover { background: rgba(255, 255, 255, 0.03); }
    .footer { font-size: 12px; color: var(--text-muted); text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--line); }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="top-header">
      <div class="logo-section">
        <h1>💰 MoneyControl Pro</h1>
        <p>Complete Financial Market Intelligence & Analytics</p>
      </div>
      <div class="header-stats">
        <div class="stat-box">
          <span class="stat-label">Global Change</span>
          <span class="stat-value" id="globalChange">+0.32%</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Active Markets</span>
          <span class="stat-value" id="activeMarkets">18</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Updated</span>
          <span class="stat-value" id="lastUpdate" style="font-size: 14px;">Just now</span>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="nav-tabs">
        <button class="nav-tab active" data-tab="dashboard">📊 Dashboard</button>
        <button class="nav-tab" data-tab="gainers">📈 Top Gainers</button>
        <button class="nav-tab" data-tab="losers">📉 Top Losers</button>
        <button class="nav-tab" data-tab="sectors">🏢 By Sector</button>
      </div>

      <!-- DASHBOARD TAB -->
      <div id="dashboard" class="tab-content active">
        <div class="summary-grid">
          <div class="summary-card">
            <div class="card-label">🏆 Market Leader</div>
            <div class="card-value" id="topGainer">-</div>
            <div class="card-change up" id="topGainerChange">-</div>
          </div>
          <div class="summary-card">
            <div class="card-label">📉 Market Laggard</div>
            <div class="card-value" id="topLoser">-</div>
            <div class="card-change down" id="topLoserChange">-</div>
          </div>
          <div class="summary-card">
            <div class="card-label">😊 Best Sentiment</div>
            <div class="card-value" id="bestSent">-</div>
            <div class="card-change up" id="bestSentChange">-</div>
          </div>
          <div class="summary-card">
            <div class="card-label">⚡ Avg Change</div>
            <div class="card-value" id="avgChange">-</div>
            <div class="card-change">Daily volatility</div>
          </div>
          <div class="summary-card">
            <div class="card-label">📊 Gainers</div>
            <div class="card-value card-change up" id="gainersCount">0</div>
            <div class="card-change">Out of 18 markets</div>
          </div>
        </div>

        <div class="section-card">
          <div class="section-header">
            <span class="section-title">⭐ ALL MARKETS (18)</span>
          </div>
          <div class="section-body">
            <div class="stock-grid" id="allMarketsGrid"></div>
          </div>
        </div>

        <div class="section-card">
          <div class="section-header">
            <span class="section-title">🏆 Performance Rankings</span>
          </div>
          <div class="section-body">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 40px;">#</th>
                  <th>Market</th>
                  <th>Price</th>
                  <th>Change %</th>
                  <th>Volume (M)</th>
                  <th>Sentiment</th>
                </tr>
              </thead>
              <tbody id="performanceTable"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- GAINERS TAB -->
      <div id="gainers" class="tab-content">
        <div class="section-card">
          <div class="section-header">
            <span class="section-title">📈 Top Gainers</span>
          </div>
          <div class="section-body">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Market</th>
                  <th>Price</th>
                  <th>Change %</th>
                  <th>Sentiment</th>
                </tr>
              </thead>
              <tbody id="gainersTable"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- LOSERS TAB -->
      <div id="losers" class="tab-content">
        <div class="section-card">
          <div class="section-header">
            <span class="section-title">📉 Top Losers</span>
          </div>
          <div class="section-body">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Market</th>
                  <th>Price</th>
                  <th>Change %</th>
                  <th>Sentiment</th>
                </tr>
              </thead>
              <tbody id="losersTable"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- SECTORS TAB -->
      <div id="sectors" class="tab-content">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div class="section-card">
            <div class="section-header">
              <span class="section-title">🌎 Americas</span>
            </div>
            <div class="section-body">
              <div class="stock-grid" id="americasGrid"></div>
            </div>
          </div>
          <div class="section-card">
            <div class="section-header">
              <span class="section-title">🇪🇺 Europe</span>
            </div>
            <div class="section-body">
              <div class="stock-grid" id="europeGrid"></div>
            </div>
          </div>
          <div class="section-card">
            <div class="section-header">
              <span class="section-title">🌏 Asia-Pacific</span>
            </div>
            <div class="section-body">
              <div class="stock-grid" id="asiaGrid"></div>
            </div>
          </div>
          <div class="section-card">
            <div class="section-header">
              <span class="section-title">💎 Crypto</span>
            </div>
            <div class="section-body">
              <div class="stock-grid" id="cryptoGrid"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="footer">
        <p>💼 MoneyControl Pro - Professional Market Intelligence • Real-time • Multi-market • 24/7</p>
      </div>
    </div>
  </div>

  <script>
    const REGIONS = {
      'US': ['SP500', 'NASDAQ', 'DJI'],
      'EU': ['DAX', 'CAC40', 'FTSE100'],
      'IN': ['NIFTY50', 'SENSEX'],
      'HK': ['HSI'],
      'JP': ['N225'],
      'KR': ['KOSPI'],
      'AU': ['ASX200'],
      'SG': ['STI'],
      'SA': ['TADAWUL'],
      'Crypto': ['BTC', 'ETH']
    };

    let allMarkets = [];

    function buildStockCard(market) {
      const changeClass = market.change_percent >= 0 ? 'up' : 'down';
      const sentimentScore = market.sentiment?.net || 0;
      const sentimentColor = sentimentScore > 0.1 ? 'positive' : sentimentScore < -0.1 ? 'negative' : 'neutral';
      
      return `
        <div class="stock-card">
          <div class="stock-header">
            <div>
              <div class="stock-symbol">${market.market}</div>
              <div class="stock-name">${market.exchange_info?.name || 'Market'}</div>
            </div>
            <div class="badge badge-${changeClass === 'up' ? 'green' : 'red'}">${market.change_percent?.toFixed(2) || 0}%</div>
          </div>
          <div class="stock-price" style="color: ${changeClass === 'up' ? 'var(--green)' : 'var(--red)'};">₹${(market.price || 0).toLocaleString('en-IN', {maximumFractionDigits: 2})}</div>
          <div class="stock-metrics">
            <div class="metric">
              <div class="metric-label">High</div>
              <div class="metric-value">${(market.high || 0).toFixed(0)}</div>
            </div>
            <div class="metric">
              <div class="metric-label">Low</div>
              <div class="metric-value">${(market.low || 0).toFixed(0)}</div>
            </div>
            <div class="metric">
              <div class="metric-label">Vol</div>
              <div class="metric-value">${(market.volume || 0 / 1000000).toFixed(1)}M</div>
            </div>
            <div class="metric">
              <div class="metric-label">Sent</div>
              <div class="metric-value" style="color: ${sentimentScore > 0 ? 'var(--green)' : 'var(--red)'};">${sentimentScore.toFixed(2)}</div>
            </div>
          </div>
        </div>
      `;
    }

    async function fetchAndRender() {
      try {
        const res = await fetch('/api/markets/all');
        const data = await res.json();
        allMarkets = data.markets || [];

        // Render all markets cards
        const grid = document.getElementById('allMarketsGrid');
        grid.innerHTML = allMarkets.map(m => buildStockCard(m)).join('');

        // Performance table
        const sorted = [...allMarkets].sort((a, b) => (b.change_percent || 0) - (a.change_percent || 0));
        const tbody = document.getElementById('performanceTable');
        tbody.innerHTML = sorted.map((m, i) => `
          <tr>
            <td><strong>${i + 1}</strong></td>
            <td><strong>${m.market}</strong></td>
            <td>₹${(m.price || 0).toLocaleString('en-IN', {maximumFractionDigits: 2})}</td>
            <td style="color: ${m.change_percent >= 0 ? 'var(--green)' : 'var(--red)'}; font-weight: 600;">${m.change_percent >= 0 ? '+' : ''}${m.change_percent?.toFixed(2)}%</td>
            <td>${(m.volume / 1000000 || 0).toFixed(1)}</td>
            <td><div class="badge badge-blue">${(m.sentiment?.net || 0).toFixed(2)}</div></td>
          </tr>
        `).join('');

        // Gainers
        const gainersBody = document.getElementById('gainersTable');
        gainersBody.innerHTML = sorted.slice(0, 10).map((m, i) => `
          <tr>
            <td>${i + 1}</td>
            <td><strong>${m.market}</strong></td>
            <td>₹${(m.price || 0).toLocaleString('en-IN', {maximumFractionDigits: 2})}</td>
            <td style="color: var(--green); font-weight: 600;">+${m.change_percent?.toFixed(2)}%</td>
            <td>${(m.sentiment?.net || 0).toFixed(2)}</td>
          </tr>
        `).join('');

        // Losers
        const losersBody = document.getElementById('losersTable');
        const losersData = [...allMarkets].sort((a, b) => (a.change_percent || 0) - (b.change_percent || 0));
        losersBody.innerHTML = losersData.slice(0, 10).map((m, i) => `
          <tr>
            <td>${i + 1}</td>
            <td><strong>${m.market}</strong></td>
            <td>₹${(m.price || 0).toLocaleString('en-IN', {maximumFractionDigits: 2})}</td>
            <td style="color: var(--red); font-weight: 600;">${m.change_percent?.toFixed(2)}%</td>
            <td>${(m.sentiment?.net || 0).toFixed(2)}</td>
          </tr>
        `).join('');

        // Regional grids
        Object.entries(REGIONS).forEach(([region, symbols]) => {
          const markets = allMarkets.filter(m => symbols.includes(m.market));
          const gridId = region === 'US' ? 'americasGrid' : 
                         region === 'EU' ? 'europeGrid' : 
                         region === 'Crypto' ? 'cryptoGrid' : 'asiaGrid';
          const grid = document.getElementById(gridId);
          if (grid) grid.innerHTML = markets.map(m => buildStockCard(m)).join('');
        });

        // Summary cards
        const gainers = allMarkets.filter(m => m.change_percent >= 0).length;
        const avgChg = (allMarkets.reduce((s, m) => s + (m.change_percent || 0), 0) / allMarkets.length).toFixed(2);
        const topG = sorted[0];
        const topL = sorted[allMarkets.length - 1];
        const bestSent = [...allMarkets].sort((a, b) => (b.sentiment?.net || 0) - (a.sentiment?.net || 0))[0];

        document.getElementById('topGainer').textContent = topG?.market || '-';
        document.getElementById('topGainerChange').textContent = `+${topG?.change_percent?.toFixed(2)}% | ${topG?.exchange_info?.name}`;
        document.getElementById('topLoser').textContent = topL?.market || '-';
        document.getElementById('topLoserChange').textContent = `${topL?.change_percent?.toFixed(2)}% | ${topL?.exchange_info?.name}`;
        document.getElementById('bestSent').textContent = bestSent?.market || '-';
        document.getElementById('bestSentChange').textContent = `+${(bestSent?.sentiment?.net || 0).toFixed(2)} | Very Positive`;
        document.getElementById('avgChange').textContent = (avgChg >= 0 ? '+' : '') + avgChg + '%';
        document.getElementById('gainersCount').textContent = gainers;
        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
      } catch (e) {
        console.error('Error:', e);
      }
    }

    function setupTabs() {
      document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
          document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
          document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
          tab.classList.add('active');
          document.getElementById(tab.dataset.tab).classList.add('active');
        });
      });
    }

    setupTabs();
    fetchAndRender();
    setInterval(fetchAndRender, 3000);
  </script>
</body>
</html>
    """