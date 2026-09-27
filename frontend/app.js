const API_URL = "http://127.0.0.1:8000";

async function loadStats() {

    const response = await fetch(
        `${API_URL}/stats`
    );

    const stats = await response.json();

    document.getElementById(
        "totalTrades"
    ).textContent = stats.total_trades;

    document.getElementById(
        "winRate"
    ).textContent =
        `${stats.win_rate.toFixed(1)}%`;

    document.getElementById(
        "totalR"
    ).textContent =
        `${stats.total_r.toFixed(2)}R`;

    document.getElementById(
        "expectancy"
    ).textContent =
        `${stats.expectancy.toFixed(2)}R`;

    document.getElementById(
        "profitFactor"
    ).textContent =
        stats.profit_factor.toFixed(2);
}


async function loadTrades() {

    const response = await fetch(
        `${API_URL}/trades`
    );

    const trades = await response.json();

    const tradeList =
        document.getElementById("tradeList");

    if (trades.length === 0) {

        tradeList.innerHTML =
            "<p>No trades recorded yet.</p>";

        return;
    }

    tradeList.innerHTML = "";

    trades
        .slice(-5)
        .reverse()
        .forEach(trade => {

            const tradeElement =
                document.createElement("div");

            tradeElement.innerHTML = `
                <strong>
                    ${trade.pair}
                </strong>

                <span>
                    ${trade.direction}
                </span>

                <span>
                    ${trade.result_r}R
                </span>
            `;

            tradeElement.style.display = "flex";
            tradeElement.style.gap = "20px";
            tradeElement.style.padding = "12px 0";

            tradeList.appendChild(
                tradeElement
            );
        });
}


async function loadDashboard() {

    await loadStats();
    await loadTrades();

}


loadDashboard();