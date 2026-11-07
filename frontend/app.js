const API_URL = "http://127.0.0.1:8000";
let currentTrades = [];

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

        console.error(
            "Error loading stats:",
            error
        );

        document.getElementById("totalTrades").textContent =
            "Unavailable";

        document.getElementById("winRate").textContent =
            "Unavailable";

        document.getElementById("totalR").textContent =
            "Unavailable";

        document.getElementById("expectancy").textContent =
            "Unavailable";

        document.getElementById("profitFactor").textContent =
            "Unavailable";

        document.getElementById("smcCompliance").textContent =
            "Unavailable";
    }
}
async function loadDailyStats() {

    const tableBody = document.getElementById("dailyStatsBody");

    try {

        const response = await fetch(
            `${API_URL}/stats/daily`
        );

        if (!response.ok) {
            throw new Error("Failed to load daily statistics");
        }

        const dailyStats = await response.json();

        tableBody.innerHTML = "";

        const dailyEntries = Object.entries(dailyStats)
            .sort((a, b) => b[0].localeCompare(a[0]));

        if (dailyEntries.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7">No daily performance data available.</td>
                </tr>
            `;
            return;
        }

        dailyEntries.forEach(([date, stats]) => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${date}</td>
                <td>${stats.trades}</td>
                <td>${stats.wins}</td>
                <td>${stats.losses}</td>
                <td>${stats.breakevens}</td>
                <td>${Number(stats.total_r).toFixed(2)}R</td>
                <td>${Number(stats.average_r).toFixed(2)}R</td>
            `;

            tableBody.appendChild(row);

        });

    } catch (error) {

        console.error("Daily statistics error:", error);

        tableBody.innerHTML = `
            <tr>
                <td colspan="7">Unable to load daily performance.</td>
            </tr>
        `;

    }
}
function isSMCValid(trade) {

    return (
        trade.liquidity_sweep &&
        trade.bos &&
        trade.structural_liquidity &&
        trade.poi
    )
        ? "Valid"
        : "Invalid";
}

function renderRecentTrades(trades) {

    const tradeList = document.getElementById("tradeList");

    // Handle an empty trading journal
    if (trades.length === 0) {
        tradeList.textContent = "No recent trades.";
        return;
    }

    // Get the five latest trades
    const recentTrades = [...trades]
        .sort((a, b) => b.id - a.id)
        .slice(0, 5);

    tradeList.innerHTML = "";

    recentTrades.forEach(trade => {

        const tradeCard = document.createElement("div");
        tradeCard.className = "recent-trade-card";

        const tradeInfo = document.createElement("div");

        const pair = document.createElement("h3");
        pair.textContent = `${trade.pair} — ${trade.direction}`;

        const result = document.createElement("p");
        result.textContent = `Result: ${trade.result_r}R`;

        const entry = document.createElement("p");
        entry.textContent = `Entry: ${trade.entry_type}`;

        tradeInfo.append(pair, result, entry);

        const reviewButton = document.createElement("button");
        reviewButton.textContent = "Review";

        reviewButton.addEventListener("click", () => {
            reviewTrade(trade.id);
        });

        tradeCard.append(tradeInfo, reviewButton);

        tradeList.appendChild(tradeCard);

    });
}

async function loadTrades() {

    try {

        const response = await fetch(
            `${API_URL}/trades`
        );

        if (!response.ok) {
            throw new Error("Failed to load trades");
        }

        const trades = await response.json();
        currentTrades = trades;
        renderRecentTrades(trades);

        console.log("Trades received:", trades);

        const tableBody =
            document.getElementById(
                "tradeTableBody"
            );

        if (trades.length === 0) {

            tableBody.innerHTML = `
                <tr>
                    <td colspan="9">
                        No trades recorded yet.
                    </td>
                </tr>
            `;

            return;
        }

        tableBody.innerHTML = "";

        trades.forEach(trade => {

            const row =
                document.createElement("tr");

            row.innerHTML = `
                <td>${trade.id}</td>
                <td>${trade.pair}</td>
                <td>${trade.direction}</td>
                <td>${trade.entry_type}</td>
                <td>${trade.result_r}R</td>
                <td>${trade.exit_type}</td>
                <td>${isSMCValid(trade)}</td>
                <td>${trade.mistake ? "Yes" : "No"}</td>
                <td>
                    <button
                        class="review-button"
                        onclick="reviewTrade(${trade.id})"
                    >
                        Review
                    </button>

                    <button onclick="editTrade(${trade.id})">
                        Edit
                    </button>
                </td>
            `;

            tableBody.appendChild(row);

        });

    } catch (error) {

        console.error(
            "Error loading trades:",
            error
        );
         const tradeList = document.getElementById("tradeList");
        const tableBody = document.getElementById("tradeTableBody");

        tradeList.textContent = "Unable to load recent trades.";

        tableBody.innerHTML = `
            <tr>
                <td colspan="9">
                    Unable to load trades. Please try again later.
                </td>
            </tr>
        `;

    }
}

async function loadDashboard() {
    await loadStats();
    await loadTrades();
    await loadDailyStats();
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

    const poi = document.getElementById("poi").checked;

    if (
        !liquiditySweep ||
        !bos ||
        !structuralLiquidity ||
        !poi
    ) {
        document.getElementById("formMessage").textContent =
            "All four SMC conditions must be confirmed before saving a trade.";

        return;
    }

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
const mistakeCheckbox =
    document.getElementById("mistake");

const mistakeTypeInput =
    document.getElementById("mistakeType");

mistakeTypeInput.required = mistakeCheckbox.checked;

mistakeCheckbox.addEventListener("change", function() {

    mistakeTypeInput.required = this.checked;

    if (!this.checked) {
        mistakeTypeInput.value = "";
    }

});

function editTrade(tradeId) {

    const trade = currentTrades.find(
        trade => trade.id === tradeId
    );

    if (!trade) {
        console.error("Trade not found");
        return;
    }

    document.getElementById("editTradeSection").style.display = "block";

    document.getElementById("editTradeId").value = trade.id;
    document.getElementById("editPair").value = trade.pair;
    document.getElementById("editDirection").value = trade.direction;
    document.getElementById("editRisk").value = trade.risk;
    document.getElementById("editResultR").value = trade.result_r;
    document.getElementById("editEntryType").value = trade.entry_type;

    document.getElementById("editLiquiditySweep").checked =
        trade.liquidity_sweep;

    document.getElementById("editBos").checked =
        trade.bos;

    document.getElementById("editStructuralLiquidity").checked =
        trade.structural_liquidity;

    document.getElementById("editPoi").checked =
        trade.poi;

    document.getElementById("editExitType").value =
        trade.exit_type;

    document.getElementById("editPlannedTp").value =
        trade.planned_tp;

    document.getElementById("editMistake").checked =
        trade.mistake;

    document.getElementById("editMistakeType").value =
        trade.mistake_type;
    
    editMistakeTypeInput.required = editMistakeCheckbox.checked;
}

document
    .getElementById("editTradeForm")
    .addEventListener("submit", updateTrade);


async function updateTrade(event) {

    event.preventDefault();

    const tradeId =
        document.getElementById("editTradeId").value;

    const updatedTrade = {
        pair: document.getElementById("editPair").value,
        direction: document.getElementById("editDirection").value,
        risk: Number(document.getElementById("editRisk").value),
        result_r: Number(document.getElementById("editResultR").value),
        entry_type: document.getElementById("editEntryType").value,

        liquidity_sweep:
            document.getElementById("editLiquiditySweep").checked,

        bos:
            document.getElementById("editBos").checked,

        structural_liquidity:
            document.getElementById("editStructuralLiquidity").checked,

        poi:
            document.getElementById("editPoi").checked,

        exit_type:
            document.getElementById("editExitType").value,

        planned_tp:
            Number(document.getElementById("editPlannedTp").value),

        mistake:
            document.getElementById("editMistake").checked,

        mistake_type:
            document.getElementById("editMistakeType").value
    };

    try {

        const response = await fetch(
            `${API_URL}/trades/${tradeId}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(updatedTrade)
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Failed to update trade"
            );
        }

        console.log("Trade updated:", result);

        document.getElementById("editTradeSection").style.display =
            "none";

        alert("Trade updated successfully!");

        await loadDashboard();

    } catch (error) {

        console.error("Update error:", error);

        alert(`Error updating trade: ${error.message}`);

    }
}
const editMistakeCheckbox =
    document.getElementById("editMistake");

const editMistakeTypeInput =
    document.getElementById("editMistakeType");

editMistakeCheckbox.addEventListener("change", function() {

    editMistakeTypeInput.required = this.checked;

    if (!this.checked) {
        editMistakeTypeInput.value = "";
    }

});
async function reviewTrade(tradeId) {

    const reviewSection =
        document.getElementById("tradeReview");

    const reviewContent =
        document.getElementById("reviewContent");

    reviewSection.style.display = "block";

    reviewContent.innerHTML = "<p>Loading trade review...</p>";

    try {

        const response = await fetch(
            `${API_URL}/trades/${tradeId}/review`
        );

        const trade = await response.json();

        if (!response.ok) {
            throw new Error(
                trade.detail || "Failed to load trade review"
            );
        }

        reviewContent.innerHTML = `

            <h3>
                ${trade.pair} — ${trade.direction}
            </h3>

            <h3>Performance</h3>

            <p>
                <strong>Result:</strong>
                ${trade.result_r}R
            </p>

            <p>
                <strong>Risk:</strong>
                $${trade.risk}
            </p>

            <p>
                <strong>PnL:</strong>
                $${Number(trade.pnl).toFixed(2)}
            </p>

            <h3>Entry Analysis</h3>

            <p>
                <strong>Entry Type:</strong>
                ${trade.entry_type}
            </p>

            <p>
                <strong>SMC Validity:</strong>
                ${trade.valid_smc ? "Valid" : "Invalid"}
            </p>

            <p>
                <strong>Trade Quality:</strong>
                ${trade.trade_quality}/5
            </p>

            <h3>SMC Conditions</h3>

            <p>
                ${trade.liquidity_sweep ? "✓" : "✗"}
                Liquidity Sweep
            </p>

            <p>
                ${trade.bos ? "✓" : "✗"}
                BOS
            </p>

            <p>
                ${trade.structural_liquidity ? "✓" : "✗"}
                Structural Liquidity
            </p>

            <p>
                ${trade.poi ? "✓" : "✗"}
                POI
            </p>

            <h3>Exit Analysis</h3>

            <p>
                <strong>Exit Type:</strong>
                ${trade.exit_type}
            </p>

            <p>
                <strong>Planned TP:</strong>
                ${trade.planned_tp}R
            </p>

            <p>
                <strong>TP Capture:</strong>
                ${Number(trade.tp_capture).toFixed(2)}%
            </p>

            <p>
                <strong>Early Exit:</strong>
                ${trade.early_exit ? "Yes" : "No"}
            </p>

            <p>
                <strong>R Left:</strong>
                ${Number(trade.r_left).toFixed(2)}R
            </p>

            <h3>Mistake</h3>

            <p>
                ${trade.mistake ? "Yes" : "No"}
            </p>

            ${
                trade.mistake
                    ? `<p>${trade.mistake_type}</p>`
                    : ""
            }

        `;

    } catch (error) {

        console.error("Review error:", error);

        reviewContent.innerHTML =
            `<p>Error: ${error.message}</p>`;

    }
}

// Add Trade navigation
document
    .getElementById("addTradeButton")
    .addEventListener("click", function() {

        const addTradeSection =
            document.getElementById("addTradeSection");

        addTradeSection.scrollIntoView({
            behavior: "smooth"
        });

        document.getElementById("pair").focus();
    });


// View All navigation
document
    .getElementById("viewTradesButton")
    .addEventListener("click", function() {

        const tradeHistorySection =
            document.getElementById("tradeHistorySection");

        tradeHistorySection.scrollIntoView({
            behavior: "smooth"
        });

    });
loadDashboard();