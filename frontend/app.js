const API_URL = "http://127.0.0.1:8000";


async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);

        if (!response.ok) {
            throw new Error("Failed to load statistics");
        }

        const stats = await response.json();

        console.log("Stats:", stats);

        document.getElementById("totalTrades").textContent =
            stats.total_trades ?? stats.trades ?? 0;

        document.getElementById("winRate").textContent =
            `${Number(stats.win_rate ?? 0).toFixed(1)}%`;

        document.getElementById("totalR").textContent =
            `${Number(stats.total_r ?? 0).toFixed(2)}R`;

        document.getElementById("expectancy").textContent =
            `${Number(stats.expectancy ?? 0).toFixed(2)}R`;

        document.getElementById("profitFactor").textContent =
            Number(stats.profit_factor ?? 0).toFixed(2);

        document.getElementById("smcCompliance").textContent =
            `${Number(
                stats.smc_compliance ??
                stats.smc_validity ??
                0
            ).toFixed(1)}%`;

    } catch (error) {
        console.error("Error loading stats:", error);
    }
}


async function loadTrades() {
    try {
        const response = await fetch(`${API_URL}/trades`);

        if (!response.ok) {
            throw new Error("Failed to load trades");
        }

        const trades = await response.json();

        console.log("Trades:", trades);

        const tradeList =
            document.getElementById("tradeList");

        if (!trades.length) {
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

                tradeElement.className = "trade-row";

                tradeElement.innerHTML = `
                    <strong>${trade.pair}</strong>
                    <span>${trade.direction}</span>
                    <span>${trade.result_r}R</span>
                `;

                tradeList.appendChild(tradeElement);
            });

    } catch (error) {
        console.error("Error loading trades:", error);
    }
}


async function loadDashboard() {
    await loadStats();
    await loadTrades();
}

const tradeForm = document.getElementById("tradeForm");

tradeForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const pair =
        document.getElementById("pair").value;

    const direction =
        document.getElementById("direction").value;

    const risk =
        Number(document.getElementById("risk").value);

    const resultR =
        Number(document.getElementById("resultR").value);

    const entryType =
        document.getElementById("entryType").value;

    const liquiditySweep =
        document.getElementById("liquiditySweep").checked;

    const bos =
        document.getElementById("bos").checked;

    const structuralLiquidity =
        document.getElementById("structuralLiquidity").checked;

    const poi =
        document.getElementById("poi").checked;

    const exitType =
        document.getElementById("exitType").value;

    const plannedTp =
        Number(document.getElementById("plannedTp").value);

    const mistake =
        document.getElementById("mistake").checked;

    const mistakeType =
        document.getElementById("mistakeType").value;


    const params = new URLSearchParams({

        pair: pair,
        direction: direction,
        risk: risk,
        result_r: resultR,
        entry_type: entryType,

        liquidity_sweep: liquiditySweep,
        bos: bos,
        structural_liquidity: structuralLiquidity,
        poi: poi,

        exit_type: exitType,
        planned_tp: plannedTp,

        mistake: mistake,
        mistake_type: mistakeType

    });


    try {

        const response = await fetch(
            `${API_URL}/trades?${params.toString()}`,
            {
                method: "POST"
            }
        );


        const data = await response.json();

        console.log("Trade response:", data);


        if (!response.ok) {

            throw new Error(
                data.detail || data.error || "Failed to save trade"
            );

        }


        document.getElementById(
            "formMessage"
        ).textContent =
            "Trade saved successfully!";


        tradeForm.reset();


        await loadStats();

        await loadTrades();


    } catch (error) {

        console.error(error);

        document.getElementById(
            "formMessage"
        ).textContent =
            `Error: ${error.message}`;

    }

});

loadDashboard();