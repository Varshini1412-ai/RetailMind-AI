const analyzeBtn = document.getElementById("analyze-btn");
const clearBtn = document.getElementById("clear-btn");
const textInput = document.getElementById("text-input");
const loadingIndicator = document.getElementById("loading-indicator");
const resultsSection = document.getElementById("results-section");
const resultsList = document.getElementById("results-list");

analyzeBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) return;

    loadingIndicator.classList.remove("hidden");
    analyzeBtn.disabled = true;

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        if (!response.ok) {
            const err = await response.json();
            alert(err.error || "Something went wrong.");
            return;
        }

        const data = await response.json();
        renderResults(data.results);
    } catch (e) {
        alert("Failed to reach the server. Is the Flask app running?");
        console.error(e);
    } finally {
        loadingIndicator.classList.add("hidden");
        analyzeBtn.disabled = false;
    }
});

clearBtn.addEventListener("click", () => {
    textInput.value = "";
    resultsSection.classList.add("hidden");
    resultsList.innerHTML = "";
});

function renderResults(results) {
    resultsSection.classList.remove("hidden");
    resultsList.innerHTML = "";

    results.forEach((r) => {
        const item = document.createElement("div");
        item.className = "result-item";

        const sentimentClass = r.sentiment.label === "POSITIVE" ? "badge-positive" : "badge-negative";

        item.innerHTML = `
            <div class="result-text">${escapeHtml(r.text)}</div>
            <span class="badge ${sentimentClass}">${r.sentiment.label} (${(r.sentiment.score * 100).toFixed(0)}%)</span>
            <span class="badge badge-emotion">${r.emotion.label} (${(r.emotion.score * 100).toFixed(0)}%)</span>
        `;
        resultsList.appendChild(item);
    });

    drawSentimentChart(results);
    drawEmotionChart(results);
}

function drawSentimentChart(results) {
    const counts = {};
    results.forEach((r) => {
        counts[r.sentiment.label] = (counts[r.sentiment.label] || 0) + 1;
    });

    const labels = Object.keys(counts);
    const values = Object.values(counts);

    Plotly.newPlot(
        "sentiment-chart",
        [{
            type: "pie",
            labels,
            values,
            marker: { colors: labels.map((l) => (l === "POSITIVE" ? "#2ecc71" : "#e74c3c")) },
            hole: 0.5,
        }],
        {
            title: "Sentiment breakdown",
            paper_bgcolor: "transparent",
            font: { color: "#e8e9ed" },
            margin: { t: 40, b: 10, l: 10, r: 10 },
        },
        { responsive: true, displayModeBar: false }
    );
}

function drawEmotionChart(results) {
    const counts = {};
    results.forEach((r) => {
        counts[r.emotion.label] = (counts[r.emotion.label] || 0) + 1;
    });

    const labels = Object.keys(counts);
    const values = Object.values(counts);

    Plotly.newPlot(
        "emotion-chart",
        [{
            type: "bar",
            x: labels,
            y: values,
            marker: { color: "#6c5ce7" },
        }],
        {
            title: "Emotion breakdown",
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
            font: { color: "#e8e9ed" },
            margin: { t: 40, b: 40, l: 40, r: 10 },
            xaxis: { gridcolor: "#2a2e3a" },
            yaxis: { gridcolor: "#2a2e3a" },
        },
        { responsive: true, displayModeBar: false }
    );
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
