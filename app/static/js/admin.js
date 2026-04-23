/**
 * Fortress - Admin Dashboard Logic
 * Lógica para el panel administrativo (admin/dashboard.html, admin/cases.html, etc.)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle Logic for Mobile — Para admin_sidebar.html
    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.querySelector('.dashboard-sidebar');
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }

    // Close sidebar when clicking overlay
    overlay.addEventListener('click', function() {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    });
});