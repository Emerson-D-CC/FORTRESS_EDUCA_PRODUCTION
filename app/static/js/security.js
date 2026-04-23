/* Toggle visibilidad contraseña */
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

document.addEventListener('DOMContentLoaded', function () {

    /* Validación Bootstrap */
    document.querySelectorAll('.needs-validation').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    /* Solo números en inputs MFA */
    document.querySelectorAll('input[inputmode="numeric"]').forEach(function (input) {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);
        });
    });


    const modalCerrarUna = document.getElementById('modalCerrarUnaSesion');
    if (modalCerrarUna) {
        modalCerrarUna.addEventListener('show.bs.modal', function (event) {
            const btn         = event.relatedTarget;
            const dispositivo = btn.getAttribute('data-dispositivo');
            const url         = btn.getAttribute('data-url'); // ← URL ya resuelta, sin Jinja en JS

            document.getElementById('modalDispositivoNombre').textContent = dispositivo;
            document.getElementById('formCerrarUnaSesion').action = url; // ← asigna directo
        });
    }
});