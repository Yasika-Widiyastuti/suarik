// planner.js — Filter task, modal edit, dan modal hapus.
(function () {
    "use strict";

    // ---- Filter task ----
    var chips = document.querySelectorAll('.filter-chips .chip-filter');
    var taskItems = document.querySelectorAll('#task-list .task-card');

    chips.forEach(function (chip) {
        chip.addEventListener('click', function () {
            chips.forEach(function (c) {
                c.classList.remove('is-active');
                c.setAttribute('aria-selected', 'false');
            });
            chip.classList.add('is-active');
            chip.setAttribute('aria-selected', 'true');
            var f = chip.dataset.filter;
            taskItems.forEach(function (item) {
                var s = item.dataset.state;
                if (f === 'all') item.hidden = false;
                else if (f === 'pending') item.hidden = (s !== 'pending');
                else if (f === 'done') item.hidden = (s !== 'done');
            });
        });
    });

    // ---- Modal edit ----
    var editForm = document.getElementById('edit-form');
    var editTitle = document.getElementById('edit-title-input');
    var editCat = document.getElementById('edit-category');
    var editDur = document.getElementById('edit-duration');
    var editDue = document.getElementById('edit-due');

    document.querySelectorAll('.task-edit-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            if (!editForm) return;
            var id = btn.dataset.id;
            editForm.action = '/planner/' + id + '/edit';
            editTitle.value = btn.dataset.title || '';
            editCat.value = btn.dataset.category || 'Personal';
            editDur.value = btn.dataset.duration || '10';
            editDue.value = btn.dataset.due || '';
            window.SuarikModal.open('edit-modal');
        });
    });

    // ---- Modal delete ----
    var deleteForm = document.getElementById('delete-form');
    var deleteDesc = document.getElementById('delete-desc');
    document.querySelectorAll('.task-delete-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            if (!deleteForm) return;
            var id = btn.dataset.id;
            deleteForm.action = '/planner/' + id + '/delete';
            deleteDesc.textContent = 'Menghapus "' + (btn.dataset.title || 'langkah ini') + '". Tindakan ini tidak dapat dibatalkan.';
            window.SuarikModal.open('delete-modal');
        });
    });
})();
