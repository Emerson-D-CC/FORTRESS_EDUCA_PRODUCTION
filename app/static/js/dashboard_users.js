/**
 * Fortress - Dashboard Users Logic
 * Lógica para el panel de usuario (dashboard_users/index.html, dashboard_users/request.html, etc.)
 */
// user_slideboard
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle Logic for Mobile — Para user_sidebar.html
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


// Modal Global
(function () {
    let formularioEnviado = false;
    let salidaConfirmada  = false;
    let urlPendiente      = null;

    // Marcar envío legítimo del formulario
    document
        .getElementById('formRegistroEstudiante')
        .addEventListener('submit', function () {
            formularioEnviado = true;
        });

    // Modal de advertencia
    // Se muestra antes de cualquier salida (sidebar, header, botón atrás)
    const modalEl = document.getElementById('modalSalidaRegistro');
    const modal   = new bootstrap.Modal(modalEl, {
        backdrop: true,
        keyboard: true
    });

    // Botón "Continuar de todas formas" dentro del modal
    document
        .getElementById('btnConfirmarSalida')
        .addEventListener('click', function () {
            salidaConfirmada = true;
            modal.hide();

            // Navegar a la URL que el usuario intentó visitar
            if (urlPendiente) {
                window.location.href = urlPendiente;
            } else {
                history.back();
            }
        });

    // Interceptar clics en links del sidebar y header
    document.addEventListener('click', function (e) {
        // Buscar el <a> más cercano al elemento clicado
        const link = e.target.closest('a[href]');

        if (!link) return;

        const href = link.getAttribute('href');

        // Ignorar: anclas, javascript:void, logout (tiene su propio modal)
        if (!href || href.startsWith('#') || href.startsWith('javascript')) return;
        // Ignorar si el formulario ya fue enviado o salida ya confirmada
        if (formularioEnviado || salidaConfirmada) return;
        e.preventDefault();
        urlPendiente = href;
        modal.show();
    });

    // Interceptar botones atrás/adelante del navegador
    // Pushstate trampa: agrega una entrada al historial para
    // poder detectar cuando el usuario presiona "atrás"
    history.pushState(null, '', window.location.href);

    window.addEventListener('popstate', function () {

        if (formularioEnviado || salidaConfirmada) return;
        // Volver a empujar el estado para mantener al usuario aquí
        history.pushState(null, '', window.location.href);
        urlPendiente = null;  // sin URL: el modal usará history.back()
        modal.show();
    });

})();


// profile.html:


// register_student.html:
document.getElementById('fechaNacMenor').addEventListener('change', function () {
    const fechaNac = new Date(this.value);
    const hoy = new Date();
    let edad = hoy.getFullYear() - fechaNac.getFullYear();
    const mes = hoy.getMonth() - fechaNac.getMonth();
    if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
        edad--;
    }
    document.getElementById('edadMenor').value = isNaN(edad) || edad < 0 ? '' : edad;
});


document.addEventListener("DOMContentLoaded", function () {
    const gradoActual  = document.getElementById("gradoActual");
    const gradoProximo = document.getElementById("gradoProximo");
    const hiddenProximo = document.getElementById("gradoProximoHidden");
    const msgProximo   = document.getElementById("gradoProximoMsg");

    function actualizarGradoProximo() {
        const opciones = Array.from(gradoActual.options);
        const indexSeleccionado = gradoActual.selectedIndex;

        // Limpiar estado anterior
        gradoProximo.value = "";
        hiddenProximo.value = "";
        msgProximo.style.display = "none";
        gradoProximo.style.display = "block";

        // Si está en el placeholder (valor 0) o nada seleccionado, no hacer nada
        if (!gradoActual.value || gradoActual.value === "0") return;

        // Buscar el siguiente option (saltando el placeholder en índice 0)
        const siguienteIndex = indexSeleccionado + 1;

        if (siguienteIndex < opciones.length) {
            // Existe un grado siguiente → seleccionarlo
            gradoProximo.selectedIndex = siguienteIndex;
            hiddenProximo.value = gradoProximo.value;
        } else {
            // Es el último grado → mostrar "No aplica"
            gradoProximo.style.display = "none";
            msgProximo.textContent = "No aplica";
            msgProximo.style.display = "block";
            hiddenProximo.value = "0";  // o el valor que tu backend espera para "No aplica"
        }
    }

    gradoActual.addEventListener("change", actualizarGradoProximo);

    // Ejecutar al cargar por si el form viene con un valor pre-seleccionado (ej: edición)
    actualizarGradoProximo();
});


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
