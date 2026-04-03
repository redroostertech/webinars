/* ==========================================================================
   Dashboard JavaScript — Chart rendering and data refresh
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    // Only render the Reddit chart if data and canvas exist
    if (typeof redditData !== "undefined" && redditData.length > 0) {
        renderRedditScoreChart(redditData);
    }
});


function renderRedditScoreChart(data) {
    var canvas = document.getElementById("redditScoreChart");
    if (!canvas) return;

    // Take top 10 posts by score
    var top10 = data.slice(0, 10);

    var labels = top10.map(function (post) {
        var title = post.title || "Untitled";
        return title.length > 40 ? title.substring(0, 40) + "..." : title;
    });

    var scores = top10.map(function (post) {
        return post.score || 0;
    });

    var comments = top10.map(function (post) {
        return post.comments || 0;
    });

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Score",
                    data: scores,
                    backgroundColor: "rgba(37, 99, 235, 0.8)",
                    borderColor: "rgba(37, 99, 235, 1)",
                    borderWidth: 1,
                    borderRadius: 4,
                },
                {
                    label: "Comments",
                    data: comments,
                    backgroundColor: "rgba(22, 163, 74, 0.6)",
                    borderColor: "rgba(22, 163, 74, 1)",
                    borderWidth: 1,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: "Top 10 Reddit Posts — Score vs Comments",
                    font: { size: 16, weight: "600" },
                    color: "#1f2937",
                    padding: { bottom: 16 },
                },
                legend: {
                    position: "top",
                    labels: {
                        usePointStyle: true,
                        padding: 16,
                    },
                },
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0,
                        font: { size: 11 },
                    },
                    grid: { display: false },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: "rgba(0,0,0,0.05)" },
                    ticks: { font: { size: 12 } },
                },
            },
        },
    });
}


function refreshData() {
    var btn = document.getElementById("refresh-btn");
    if (!btn) return;

    btn.textContent = "Refreshing...";
    btn.disabled = true;

    fetch("/api/refresh", { method: "POST" })
        .then(function (response) { return response.json(); })
        .then(function (result) {
            if (result.status === "success") {
                window.location.reload();
            } else {
                alert("Refresh failed: " + result.message);
                btn.textContent = "Refresh Data";
                btn.disabled = false;
            }
        })
        .catch(function (err) {
            alert("Refresh error: " + err.message);
            btn.textContent = "Refresh Data";
            btn.disabled = false;
        });
}
