async function loadHistory() {
    const response = await fetch("/api/history");
    const data = await response.json();

    document.getElementById("total-count").textContent =
        `${data.stats.total} total analyses stored`;

    renderTable(data.records);
    renderSentimentSummary(data.stats.sentiment_breakdown);
    renderEmotionSummary(data.stats.emotion_breakdown);
}

function renderTable(records) {
    const tbody = document.getElementById("history-table-body");
    tbody.innerHTML = "";

    records.forEach((r) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${escapeHtml(r.text)}</td>
            <td>${r.sentiment_label} (${(r.sentiment_score * 100).toFixed(0)}%)</td>
            <td>${r.emotion_label} (${(r.emotion_score * 100).toFixed(0)}%)</td>
            <td>${new Date(r.created_at).toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

function renderSentimentSummary(breakdown) {
    const labels = breakdown.map((b) => b.sentiment_label);
    const values = breakdown.map((b) => b.count);

    Plotly.newPlot(
        "sentiment-summary-chart",
        [{
            type: "pie",
            labels,
            values,
            hole: 0.5,
            marker: { colors: labels.map((l) => (l === "POSITIVE" ? "#2ecc71" : "#e74c3c")) },
        }],
        {
            title: "All-time sentiment",
            paper_bgcolor: "transparent",
            font: { color: "#e8e9ed" },
            margin: { t: 40, b: 10, l: 10, r: 10 },
        },
        { responsive: true, displayModeBar: false }
    );
}

function renderEmotionSummary(breakdown) {
    const labels = breakdown.map((b) => b.emotion_label);
    const values = breakdown.map((b) => b.count);

    Plotly.newPlot(
        "emotion-summary-chart",
        [{
            type: "bar",
            x: labels,
            y: values,
            marker: { color: "#6c5ce7" },
        }],
        {
            title: "All-time emotion",
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

loadHistory();
