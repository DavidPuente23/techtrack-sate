document.addEventListener('DOMContentLoaded', function() {

    // 1. DataTables (protegido por si jQuery no está cargado en la página actual)
    if (typeof $ !== 'undefined' && $('#tablaActivos').length) {
        const tabla = $('#tablaActivos').DataTable({
            language: { url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json' },
            pageLength: 10,
            ordering: true,
            searching: false,
            lengthChange: false,
            info: false
        });

        // Sin paginaci?n visible cuando todo cabe en una sola p?gina.
        if (tabla.page.info().pages <= 1) {
            $('#tablaActivos_wrapper .dataTables_paginate').hide();
        }
    }

    // 2. FullCalendar: Mantenimientos
    const calendarEl = document.getElementById('calendario');
    if (calendarEl) {
        const datosCrudos = document.getElementById('datos-eventos').dataset.eventos;
        const mantenimientos = JSON.parse(datosCrudos);

        const eventos = mantenimientos.map(function(mant) {
            let colorEvento = '#10b981'; // Verde (Finalizado)
            if (mant.estado === 'Pendiente') colorEvento = '#f59e0b'; // Amarillo
            if (mant.estado === 'En proceso') colorEvento = '#3b82f6'; // Azul

            return {
                title: mant.activo_nombre + ' (' + mant.tipo + ')',
                start: mant.fecha_str,
                backgroundColor: colorEvento,
                borderColor: colorEvento
            };
        });

        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            height: 480,
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth'
            },
            buttonText: { today: 'Hoy', month: 'Mes', week: 'Lista' },
            events: eventos
        });
        calendar.render();
    }
});
