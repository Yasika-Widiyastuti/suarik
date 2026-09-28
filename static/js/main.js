// main.js — Interaksi global: navigasi mobile, toast, modal, dan keyboard.
(function () {
    "use strict";

    // ---- Mobile navigation ----
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.getElementById('primary-nav');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            var open = nav.classList.toggle('open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            toggle.setAttribute('aria-label', open ? 'Tutup menu navigasi' : 'Buka menu navigasi');
        });
        // Tutup menu setelah klik link di mobile
        nav.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', function () {
                if (window.innerWidth <= 960) {
                    nav.classList.remove('open');
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }

    // ---- Toast auto-dismiss ----
    var toasts = document.querySelectorAll('.toast');
    toasts.forEach(function (t) {
        var closeBtn = t.querySelector('.toast-close');
        function dismiss() {
            t.style.opacity = '0';
            t.style.transform = 'translateY(-6px)';
            setTimeout(function () { t.remove(); }, 250);
        }
        if (closeBtn) closeBtn.addEventListener('click', dismiss);
        setTimeout(dismiss, 5000);
    });

    // ---- Modal (dipakai planner) ----
    window.SuarikModal = {
        open: function (id) {
            var m = document.getElementById(id);
            if (!m) return;
            m.classList.add('is-open');
            m.setAttribute('aria-hidden', 'false');
            var focusable = m.querySelector('input, select, textarea, button');
            if (focusable) setTimeout(function () { focusable.focus(); }, 60);
        },
        close: function (id) {
            var m = document.getElementById(id);
            if (!m) return;
            m.classList.remove('is-open');
            m.setAttribute('aria-hidden', 'true');
        }
    };

    // Semua tombol dengan atribut data-close menutup modal terdekat
    document.querySelectorAll('[data-close]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            e.preventDefault();
            var modal = el.closest('.modal');
            if (modal) window.SuarikModal.close(modal.id);
        });
    });

    // Escape menutup modal / toast pertama
    document.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape') return;
        var openModal = document.querySelector('.modal.is-open');
        if (openModal) { window.SuarikModal.close(openModal.id); return; }
        var openToast = document.querySelector('.toast');
        if (openToast) openToast.remove();
    });

    // ---- Smooth scroll untuk anchor lokal ----
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        var target = link.getAttribute('href');
        if (!target || target === '#') return;
        link.addEventListener('click', function (e) {
            var el = document.querySelector(target);
            if (el) {
                e.preventDefault();
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
})();
