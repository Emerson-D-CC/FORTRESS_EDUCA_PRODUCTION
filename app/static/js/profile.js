document.getElementById('fechaNacMenorActualizar').addEventListener('change', function () {
    const fechaNac = new Date(this.value);
    const hoy = new Date();
    let edad = hoy.getFullYear() - fechaNac.getFullYear();
    const mes = hoy.getMonth() - fechaNac.getMonth();
    if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
        edad--;
    }
    document.getElementById('edadMenorActualizar').value = isNaN(edad) || edad < 0 ? '' : edad;
});

// Calcular edad al cargar si hay valor
const fechaInput = document.getElementById('fechaNacMenorActualizar');
if (fechaInput && fechaInput.value) {
    fechaInput.dispatchEvent(new Event('change'));
}

// profile.html: Grado próximo automático
document.addEventListener("DOMContentLoaded", function () {
    const gradoActual  = document.getElementById("gradoActualPerfilActualizar");
    const gradoProximo = document.getElementById("gradoProximoPerfilActualizar");
    const hidden       = document.getElementById("gradoProximoHiddenPerfilActualizar");
    const msg          = document.getElementById("gradoProximoMsgPerfilActualizar");

    function actualizarGradoProximo() {
        const opciones = Array.from(gradoActual.options);
        const indexSeleccionado = gradoActual.selectedIndex;

        // Limpiar estado anterior
        gradoProximo.value = "";
        hidden.value = "";
        msg.style.display = "none";
        gradoProximo.style.display = "block";

        // Si está en el placeholder (valor 0) o nada seleccionado, no hacer nada
        if (!gradoActual.value || gradoActual.value === "0") return;

        // Buscar el siguiente option (saltando el placeholder en índice 0)
        const siguienteIndex = indexSeleccionado + 1;

        if (siguienteIndex < opciones.length) {
            // Existe un grado siguiente → seleccionarlo
            gradoProximo.selectedIndex = siguienteIndex;
            hidden.value = gradoProximo.value;
        } else {
            // Es el último grado → mostrar "No aplica"
            gradoProximo.style.display = "none";
            msg.textContent = "No aplica";
            msg.style.display = "block";
            hidden.value = "0";
        }
    }

    gradoActual.addEventListener("change", actualizarGradoProximo);

    // Ejecutar al cargar por si el form viene con un valor pre-seleccionado (ej: edición)
    actualizarGradoProximo();
});