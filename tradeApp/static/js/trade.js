
let tradeDirection = "up";
let modalPrice = 0;
let selectedProfit = 40;
let userBalance = {{ user.wallet.amount|default: 0 }};
let countdownInterval;

// === Open modal with coin details ===
function openTradeModal(direction, coinName, coinSymbol, price) {
    tradeDirection = direction;
    modalPrice = parseFloat(price) || 0;
    document.getElementById("modalCoin").innerText = `${coinSymbol}/USDT`;
    document.getElementById("modalType").innerText = direction === "up" ? "Buy Up" : "Buy Down";
    document.getElementById("modalType").className = direction === "up" ? "badge bg-success" : "badge bg-danger";
    document.getElementById("modalPrice").innerText = `$${modalPrice.toLocaleString()}`;
    document.getElementById("tradeError").classList.add("d-none");
    document.getElementById("tradeSuccess").classList.add("d-none");
    new bootstrap.Modal(document.getElementById("tradeModal")).show();
}

// === Duration buttons ===
document.querySelectorAll(".duration-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".duration-btn").forEach((b) => b.classList.remove("btn-primary"));
        btn.classList.add("btn-primary");
        selectedProfit = parseInt(btn.getAttribute("data-profit"));
        updateProfit();
    });
});

// === Quick amount buttons ===
document.querySelectorAll(".quick-amount").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.getElementById("modalAmount").value = btn.getAttribute("data-amount");
        updateProfit();
    });
});

// === Update profit when typing ===
document.getElementById("modalAmount").addEventListener("input", updateProfit);

function updateProfit() {
    const amount = parseFloat(document.getElementById("modalAmount").value) || 0;
    const profit = (amount * (selectedProfit / 100)).toFixed(2);
    document.getElementById("expectedProfit").innerText = `$${profit}`;
    document.getElementById("occupationDeposit").innerText = `$${amount.toFixed(2)}`;
}

// === Confirm trade ===
function confirmTrade() {
    const errorBox = document.getElementById("tradeError");
    const successBox = document.getElementById("tradeSuccess");
    if (errorBox) {
        errorBox.classList.add("d-none");
        errorBox.innerText = "";
    }
    if (successBox) {
        successBox.classList.add("d-none");
        successBox.innerText = "";
    }

    const amount = parseFloat(document.getElementById("modalAmount").value) || 0;
    if (amount < 10) {
        errorBox.innerText = "⚠️ Minimum trade is $10.";
        errorBox.classList.remove("d-none");
        return;
    }
    if (amount > userBalance) {
        errorBox.innerText = "❌ Insufficient balance. Please deposit to continue.";
        errorBox.classList.remove("d-none");
        return;
    }

    const selectedPlan = document.querySelector(".duration-btn.btn-primary");
    const duration = selectedPlan ? parseInt(selectedPlan.getAttribute("data-duration")) : 30;
    const profit = selectedPlan ? parseInt(selectedPlan.getAttribute("data-profit")) : 40;

    console.log("Confirming trade:", { amount, duration, profit, tradeDirection });

    userBalance -= amount;
    document.getElementById("userBalanceDisplay").innerText = `$${userBalance.toFixed(2)}`;
    updateBalanceSmall(userBalance, null);

    fetch("/chart/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}",
        },
        body: JSON.stringify({
            amount: amount,
            direction: tradeDirection,
            coin: document.getElementById("modalCoin").innerText,
            price: modalPrice,
            profit: profit,
            duration: duration,
        }),
    })
        .then((res) => {
            console.log("Chart endpoint response status:", res.status);
            return res.json();
        })
        .then((data) => {
            console.log("Chart endpoint response data:", data);
            if (data.error) {
                userBalance += amount;
                document.getElementById("userBalanceDisplay").innerText = `$${userBalance.toFixed(2)}`;
                updateBalanceSmall(userBalance, null);
                errorBox.innerText = data.error;
                errorBox.classList.remove("d-none");
                return;
            }

            successBox.innerText = `✅ Trade started — ${duration}s`;
            successBox.classList.remove("d-none");
            console.log("Calling showCountdownOnBalance with tradeId:", data.trade_id);
            showCountdownOnBalance(duration, data.trade_id, amount, profit);
        })
        .catch((err) => {
            console.error("Network error in confirmTrade:", err);
            userBalance += amount;
            document.getElementById("userBalanceDisplay").innerText = `$${userBalance.toFixed(2)}`;
            updateBalanceSmall(userBalance, null);
            errorBox.innerText = "⚠️ Network/server error. Please try again.";
            errorBox.classList.remove("d-none");
        });
}

// === Show countdown with progressive profit ===
function showCountdownOnBalance(duration, tradeId, amount, profitPct) {
    console.log("Starting countdown:", { duration, tradeId, amount, profitPct });

    const wallet = document.querySelector(".wallet-content");
    if (!wallet) {
        console.error("Wallet content element not found. Check if .wallet-content exists in the DOM.");
        console.log("Current DOM:", document.body.innerHTML.substring(0, 500) + "..."); // Log partial DOM for debugging
        const errorBox = document.getElementById("tradeError");
        if (errorBox) {
            errorBox.innerText = "⚠️ Unable to display countdown. Please refresh the page.";
            errorBox.classList.remove("d-none");
        }
        return;
    }

    let countdownEl = document.getElementById("tradeCountdown");
    if (!countdownEl) {
        countdownEl = document.createElement("div");
        countdownEl.id = "tradeCountdown";
        countdownEl.style.marginTop = "8px";
        countdownEl.style.fontWeight = "600";
        countdownEl.style.color = "#ffc107";
        wallet.appendChild(countdownEl);
    }

    let remaining = parseInt(duration);
    if (isNaN(remaining) || remaining <= 0) {
        console.error("Invalid duration:", duration);
        return;
    }

    // Calculate total expected profit and locked amount
    const profit = amount * (profitPct / 100);
    const totalLocked = amount + profit; // Amount + profit to be locked at the end

    clearInterval(window.countdownInterval);
    countdownEl.innerText = `Trade ends in ${remaining}s`;
    updateBalanceSmall(userBalance, 0, true); // Initialize locking as 0 (estimated)

    window.countdownInterval = setInterval(() => {
        remaining--;
        countdownEl.innerText = `Trade ends in ${remaining}s`;
        console.log("Countdown:", remaining);

        // Update estimated locked amount (linear progression)
        const progress = (duration - remaining) / duration;
        const estimatedLocked = (totalLocked * progress).toFixed(2);
        updateBalanceSmall(userBalance, estimatedLocked, true);

        if (remaining < 0) {
            clearInterval(window.countdownInterval);
            countdownEl.innerText = `Finalizing trade...`;
            console.log("Calling finalizeTrade with tradeId:", tradeId);
            finalizeTrade(tradeId, countdownEl, amount, profitPct);
        }
    }, 1000);
}

// === Finalize trade ===
function finalizeTrade(tradeId, countdownEl, amount, profitPct) {
    console.log("Finalizing trade with ID:", tradeId);

    const successBox = document.getElementById("tradeSuccess");
    const errorBox = document.getElementById("tradeError");

    fetch("/finalize_trade/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}",
        },
        body: JSON.stringify({ trade_id: tradeId }),
    })
        .then((res) => {
            console.log("Finalize trade response status:", res.status);
            return res.json();
        })
        .then((data) => {
            console.log("Finalize trade response data:", data);
            if (data.error) {
                console.error("Finalize trade error:", data.error);
                if (errorBox) {
                    errorBox.innerText = data.error;
                    errorBox.classList.remove("d-none");
                }
                if (countdownEl) countdownEl.innerText = "Finalization failed";
                return;
            }

            userBalance = parseFloat(data.available) || 0;
            document.getElementById("userBalanceDisplay").innerText = `$${userBalance.toFixed(2)}`;
            updateBalanceSmall(data.available, data.locked);

            if (countdownEl) countdownEl.innerText = "🎉 Trade completed!";
            if (successBox) {
                successBox.innerText = "🎉 Trade completed! Profit credited to locked balance.";
                successBox.classList.remove("d-none");
            }

            setTimeout(() => {
                if (countdownEl && countdownEl.parentNode) countdownEl.parentNode.removeChild(countdownEl);
            }, 2000);
        })
        .catch((err) => {
            console.error("Network error in finalizeTrade:", err);
            if (errorBox) {
                errorBox.innerText = "Network error while finalizing.";
                errorBox.classList.remove("d-none");
            }
            if (countdownEl) countdownEl.innerText = "Finalization error";
        });
}

// === Update balance display ===
function updateBalanceSmall(available, locking, isEstimate = false) {
    const smallEl = document.querySelector(".wallet-content small");
    if (!smallEl) {
        console.error("Small element not found in wallet-content");
        return;
    }

    const availableText = typeof available === "number" ? `$${available.toFixed(2)}` : `$${parseFloat(available).toFixed(2)}`;
    if (locking == null) {
        const existing = smallEl.innerText;
        const parts = existing.split("|");
        smallEl.innerText = parts.length === 2 ? `Available: ${availableText} | ${parts[1].trim()}` : `Available: ${availableText}`;
    } else {
        const lockText = isEstimate ? `~$${parseFloat(locking).toFixed(2)}` : `$${parseFloat(locking).toFixed(2)}`;
        smallEl.innerText = `Available: ${availableText} | Locking: ${lockText}`;
    }
}

// === Initialize ===
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded, checking for wallet-content");
    const wallet = document.querySelector(".wallet-content");
    if (wallet) {
        console.log("Wallet-content found in DOM");
    } else {
        console.error("Wallet-content not found on page load");
    }
    async function init() {
        await fetchAllCryptos();
        await loadChart();
        setInterval(fetchAllCryptos, 30000);
    }
    init();
});
