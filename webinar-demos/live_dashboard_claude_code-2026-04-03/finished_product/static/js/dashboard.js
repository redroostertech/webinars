/* ==========================================================================
   Business Command Center — JavaScript
   Chart rendering, sync, email modal, calendar, table filters, toasts
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    // Render revenue chart if data exists
    if (typeof chartLabels !== "undefined" && chartLabels.length > 0) {
        renderRevenueChart(chartLabels, chartValues);
    }
});


/* --- Revenue Chart --- */

function renderRevenueChart(labels, values) {
    var canvas = document.getElementById("revenueChart");
    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Revenue (Paid Invoices)",
                data: values,
                backgroundColor: "rgba(37, 99, 235, 0.8)",
                borderColor: "rgba(37, 99, 235, 1)",
                borderWidth: 1,
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: "Monthly Revenue from Paid Invoices",
                    font: { size: 16, weight: "600" },
                    color: "#1f2937",
                    padding: { bottom: 16 },
                },
                legend: { display: false },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 12 } },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: "rgba(0,0,0,0.05)" },
                    ticks: {
                        font: { size: 12 },
                        callback: function (value) {
                            return "$" + value.toLocaleString();
                        },
                    },
                },
            },
        },
    });
}


/* --- Sync Drive Button --- */

function syncDrive() {
    var btn = document.getElementById("sync-btn");
    if (!btn) return;

    btn.textContent = "Syncing...";
    btn.disabled = true;

    fetch("/api/sync", { method: "POST" })
        .then(function (response) { return response.json(); })
        .then(function (result) {
            if (result.status === "success") {
                showToast("success", result.message);
                setTimeout(function () { window.location.reload(); }, 1500);
            } else if (result.status === "partial") {
                showToast("info", result.message);
                setTimeout(function () { window.location.reload(); }, 1500);
            } else {
                showToast("error", "Sync failed: " + result.message);
                btn.textContent = "Sync Drive";
                btn.disabled = false;
            }
        })
        .catch(function (err) {
            showToast("error", "Sync error: " + err.message);
            btn.textContent = "Sync Drive";
            btn.disabled = false;
        });
}


/* --- Email Modal --- */

function openEmailModal(to, subject) {
    document.getElementById("email-to").value = to || "";
    document.getElementById("email-subject").value = subject || "";
    document.getElementById("email-body").value = "";
    document.getElementById("email-modal").style.display = "flex";
}

function closeEmailModal() {
    document.getElementById("email-modal").style.display = "none";
}

function sendEmail(event) {
    event.preventDefault();

    var btn = document.getElementById("email-send-btn");
    btn.textContent = "Sending...";
    btn.disabled = true;

    var payload = {
        to: document.getElementById("email-to").value,
        subject: document.getElementById("email-subject").value,
        body: document.getElementById("email-body").value,
    };

    fetch("/api/email/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then(function (response) { return response.json(); })
        .then(function (result) {
            if (result.status === "success") {
                showToast("success", result.message);
                closeEmailModal();
            } else {
                showToast("error", result.message);
            }
            btn.textContent = "Send";
            btn.disabled = false;
        })
        .catch(function (err) {
            showToast("error", "Email error: " + err.message);
            btn.textContent = "Send";
            btn.disabled = false;
        });
}


/* --- Calendar Reminder --- */

function createReminder(title, date, description) {
    if (!date) {
        showToast("error", "No date available for this reminder.");
        return;
    }

    var payload = {
        title: title,
        date: date,
        description: description || "",
    };

    fetch("/api/calendar/remind", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then(function (response) { return response.json(); })
        .then(function (result) {
            if (result.status === "success") {
                showToast("success", result.message);
                if (result.event_link) {
                    setTimeout(function () {
                        window.open(result.event_link, "_blank");
                    }, 500);
                }
            } else {
                showToast("error", result.message);
            }
        })
        .catch(function (err) {
            showToast("error", "Calendar error: " + err.message);
        });
}


/* --- Table Filters --- */

function filterTable(tableId, attribute, value) {
    var table = document.getElementById(tableId);
    if (!table) return;

    var rows = table.querySelectorAll("tbody tr");
    rows.forEach(function (row) {
        if (!value) {
            row.style.display = "";
        } else {
            var rowVal = row.getAttribute("data-" + attribute) || "";
            row.style.display = (rowVal === value) ? "" : "none";
        }
    });
}


/* --- Project Card Expand Toggle --- */

function toggleExpand(card) {
    var details = card.querySelector(".project-card__details");
    if (!details) return;

    if (details.style.display === "none") {
        details.style.display = "block";
    } else {
        details.style.display = "none";
    }
}


/* --- Toast Notifications --- */

function showToast(type, message) {
    var container = document.getElementById("toast-container");
    if (!container) return;

    var toast = document.createElement("div");
    toast.className = "toast toast--" + type;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(function () {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.3s";
        setTimeout(function () { toast.remove(); }, 300);
    }, 4000);
}
