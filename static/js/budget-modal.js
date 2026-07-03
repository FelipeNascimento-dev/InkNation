(function () {
    const modal = document.getElementById('ink-budget-modal');
    if (!modal) return;

    const openBtn = document.getElementById('ink-budget-open');
    const closeBtn = document.getElementById('ink-budget-close');
    const backdrop = modal.querySelector('.ink-modal-backdrop');
    const form = document.getElementById('ink-budget-form');

    function openModal() {
        modal.hidden = false;
        document.body.classList.add('ink-modal-open');
    }

    function closeModal() {
        modal.hidden = true;
        document.body.classList.remove('ink-modal-open');
    }

    if (openBtn) openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (backdrop) backdrop.addEventListener('click', closeModal);

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && !modal.hidden) {
            closeModal();
        }
    });
})();
