document.querySelectorAll('.next-step').forEach(button => {
    button.addEventListener('click', () => {
        const currentTab = button.closest('.tab-pane');
        const nextTab = currentTab.nextElementSibling;
        if (nextTab) {
            new bootstrap.Tab(nextTab).show();
        }
    });
});

document.querySelectorAll('.prev-step').forEach(button => {
    button.addEventListener('click', () => {
        const currentTab = button.closest('.tab-pane');
        const prevTab = currentTab.previousElementSibling;
        if (prevTab) {
            new bootstrap.Tab(prevTab).show();
        }
    });
});

// Activa el tab indicado en ?tab= al cargar la página
(function () {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab');
    if (tabParam) {
        const tabEl = document.getElementById('tab-' + tabParam);
        if (tabEl) new bootstrap.Tab(tabEl).show();
    }
})();