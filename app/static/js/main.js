function togglePassword(fieldId, btn) {
    const field = document.getElementById(fieldId);
    const icon  = btn.querySelector('i');
    if (field.type === 'password') {
        field.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        field.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function reloadOnBackNavigation() {
    window.addEventListener('pageshow', function(event) {
        const navigationEntries = performance.getEntriesByType ? performance.getEntriesByType('navigation') : [];
        const fromBackForward = event.persisted || (navigationEntries.length > 0 && navigationEntries[0].type === 'back_forward');

        if (!fromBackForward) {
            return;
        }

        // Evitar recargar si estamos en un login con mensaje flash visible.
        const loginFlashModal = document.getElementById('loginErrorModal');
        if (loginFlashModal) {
            return;
        }

        const loginRoutes = [
            '/auth/login_user',
            '/auth/login_admin',
            '/auth/login_technical'
        ];

        if (loginRoutes.some(path => window.location.pathname.startsWith(path))) {
            return;
        }

        window.location.reload();
    });
}

document.addEventListener('DOMContentLoaded', reloadOnBackNavigation);
