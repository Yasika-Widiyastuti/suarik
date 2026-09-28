// checkin.js — Multi-step form untuk halaman /checkin.
(function () {
    "use strict";

    var form = document.getElementById('checkin-form');
    if (!form) return;

    var steps = form.querySelectorAll('.form-step');
    var indicators = form.querySelectorAll('.progress-step');
    var currentStep = 1;

    function showStep(n) {
        currentStep = n;
        steps.forEach(function (s) {
            s.classList.toggle('active', parseInt(s.dataset.step, 10) === n);
        });
        indicators.forEach(function (ind) {
            var idx = parseInt(ind.dataset.step, 10);
            ind.classList.remove('active', 'done');
            if (idx < n) ind.classList.add('done');
            else if (idx === n) ind.classList.add('active');
        });
        // Fokus otomatis ke elemen pertama step berjalan
        var active = form.querySelector('.form-step.active input, .form-step.active textarea, .form-step.active select');
        if (active) setTimeout(function () { active.focus({ preventScroll: false }); }, 40);
    }

    function validateStep(n) {
        clearErrors();
        if (n === 1) {
            var emo = form.querySelector('input[name="emotion"]:checked');
            if (!emo) { showError('emotion'); return false; }
        }
        if (n === 3) {
            var checked = form.querySelectorAll('input[name="areas"]:checked');
            if (checked.length === 0) { showError('areas'); return false; }
        }
        return true;
    }

    function showError(name) {
        var el = form.querySelector('[data-error-for="' + name + '"]');
        if (el) el.hidden = false;
    }
    function clearErrors() {
        form.querySelectorAll('.field-error').forEach(function (e) { e.hidden = true; });
    }

    // Next / Prev
    form.querySelectorAll('.btn-next').forEach(function (btn) {
        btn.addEventListener('click', function () {
            if (!validateStep(currentStep)) return;
            var next = parseInt(btn.dataset.next, 10);
            showStep(next);
        });
    });
    form.querySelectorAll('.btn-prev').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var prev = parseInt(btn.dataset.prev, 10);
            showStep(prev);
        });
    });

    // Emotion card selection styling
    form.querySelectorAll('.emotion-card').forEach(function (card) {
        var input = card.querySelector('input');
        card.addEventListener('click', function () {
            form.querySelectorAll('.emotion-card').forEach(function (c) { c.classList.remove('is-selected'); });
            card.classList.add('is-selected');
            input.checked = true;
        });
        input.addEventListener('change', function () {
            if (input.checked) card.classList.add('is-selected');
        });
    });

    // Area card selection styling
    form.querySelectorAll('.area-card').forEach(function (card) {
        var input = card.querySelector('input');
        card.addEventListener('click', function (e) {
            if (e.target === input) return;
            input.checked = !input.checked;
            card.classList.toggle('is-selected', input.checked);
        });
        input.addEventListener('change', function () {
            card.classList.toggle('is-selected', input.checked);
        });
    });

    // Slider label update
    var slider = document.getElementById('stress_level');
    var num = document.querySelector('.slider-number');
    var lbl = document.getElementById('stress-label');
    function updateSlider() {
        var v = parseInt(slider.value, 10);
        num.textContent = v;
        if (v <= 3) lbl.textContent = 'Ringan';
        else if (v <= 6) lbl.textContent = 'Sedang';
        else if (v <= 8) lbl.textContent = 'Berat';
        else lbl.textContent = 'Sangat berat';
    }
    if (slider) {
        slider.addEventListener('input', updateSlider);
        updateSlider();
    }

    // Character counter untuk textarea note
    var note = document.getElementById('note');
    var noteCount = document.getElementById('note-count');
    if (note && noteCount) {
        note.addEventListener('input', function () {
            noteCount.textContent = note.value.length;
        });
    }

    // Loading state saat submit
    form.addEventListener('submit', function (e) {
        if (!validateStep(3)) { e.preventDefault(); showStep(3); return; }
        var btn = document.getElementById('checkin-submit');
        if (btn) { btn.classList.add('is-loading'); btn.disabled = true; }
    });

    // Mulai dari step 1
    showStep(1);
})();
