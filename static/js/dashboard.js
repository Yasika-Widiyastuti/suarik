// dashboard.js — Render Chart.js untuk halaman /dashboard, dengan fallback.
(function () {
    "use strict";

    var dataEl = document.getElementById('chart-data');
    if (!dataEl) return;

    var payload;
    try { payload = JSON.parse(dataEl.textContent); }
    catch (e) { payload = null; }
    if (!payload) return;

    function renderFallback() {
        var cf = document.getElementById('categoryFallback');
        var tf = document.getElementById('trendFallback');
        if (cf) cf.hidden = false;
        if (tf) tf.hidden = false;
        var cc = document.getElementById('categoryChart');
        var tc = document.getElementById('trendChart');
        if (cc) cc.style.display = 'none';
        if (tc) tc.style.display = 'none';
    }

    function init() {
        if (typeof window.Chart === 'undefined') {
            renderFallback();
            return;
        }
        var cat = document.getElementById('categoryChart');
        var trend = document.getElementById('trendChart');

        try {
            if (cat) {
                new window.Chart(cat, {
                    type: 'bar',
                    data: {
                        labels: payload.categoryLabels,
                        datasets: [{
                            label: 'Skor',
                            data: payload.categoryValues,
                            backgroundColor: ['#8B7DB8','#E99A7A','#202A44','#6F9B7C','#7466A6'],
                            borderRadius: 10,
                            maxBarThickness: 44
                        }]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        scales: { y: { beginAtZero: true, max: 10, ticks: { stepSize: 2 } } },
                        plugins: { legend: { display: false } }
                    }
                });
            }
            if (trend) {
                new window.Chart(trend, {
                    type: 'line',
                    data: {
                        labels: payload.trendLabels,
                        datasets: [{
                            label: 'Tingkat tekanan',
                            data: payload.trendValues,
                            borderColor: '#202A44',
                            backgroundColor: 'rgba(139, 125, 184, 0.2)',
                            tension: 0.35,
                            fill: true,
                            pointBackgroundColor: '#7466A6',
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        scales: { y: { beginAtZero: true, max: 10 } },
                        plugins: { legend: { display: false } }
                    }
                });
            }
        } catch (err) {
            renderFallback();
        }
    }

    // Chart.js dimuat dengan defer; tunggu window load agar aman.
    if (document.readyState === 'complete') { init(); }
    else { window.addEventListener('load', init); }

    // Bila setelah 3 detik Chart belum ada, pakai fallback.
    setTimeout(function () {
        if (typeof window.Chart === 'undefined') renderFallback();
    }, 3000);
})();
