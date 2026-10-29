(function () {
    'use strict';

    const body = document.body;
    const toggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar-sate');
    const overlay = document.getElementById('sidebar-overlay');
    const closeButton = document.getElementById('sidebar-close');

    if (!toggle || !sidebar || !overlay) {
        return;
    }

    const media = window.matchMedia('(max-width: 900px)');
    let temporizadorOverlay = null;

    function esMovil() {
        return media.matches;
    }

    function actualizarInert() {
        if (esMovil() && !sidebar.classList.contains('is-open')) {
            sidebar.setAttribute('inert', '');
        } else {
            sidebar.removeAttribute('inert');
        }
    }

    function abrirMenu() {
        if (!esMovil()) {
            return;
        }

        if (temporizadorOverlay) {
            window.clearTimeout(temporizadorOverlay);
            temporizadorOverlay = null;
        }

        body.classList.add('sidebar-open');
        sidebar.classList.add('is-open');
        sidebar.removeAttribute('inert');
        overlay.hidden = false;
        window.requestAnimationFrame(function () {
            overlay.classList.add('is-visible');
        });
        toggle.setAttribute('aria-expanded', 'true');

        const primerEnfocable = sidebar.querySelector('button, a');
        if (primerEnfocable) {
            primerEnfocable.focus({ preventScroll: true });
        }
    }

    function cerrarMenu(devolverFoco) {
        body.classList.remove('sidebar-open');
        sidebar.classList.remove('is-open');
        overlay.classList.remove('is-visible');
        toggle.setAttribute('aria-expanded', 'false');
        actualizarInert();

        if (temporizadorOverlay) {
            window.clearTimeout(temporizadorOverlay);
        }
        temporizadorOverlay = window.setTimeout(function () {
            if (!sidebar.classList.contains('is-open')) {
                overlay.hidden = true;
            }
        }, 260);

        if (devolverFoco) {
            toggle.focus({ preventScroll: true });
        }
    }

    toggle.addEventListener('click', function () {
        if (sidebar.classList.contains('is-open')) {
            cerrarMenu(true);
        } else {
            abrirMenu();
        }
    });

    overlay.addEventListener('click', function () {
        cerrarMenu(true);
    });

    if (closeButton) {
        closeButton.addEventListener('click', function () {
            cerrarMenu(true);
        });
    }

    sidebar.querySelectorAll('a').forEach(function (enlace) {
        enlace.addEventListener('click', function () {
            if (esMovil()) {
                cerrarMenu(false);
            }
        });
    });

    document.addEventListener('keydown', function (evento) {
        if (evento.key === 'Escape' && sidebar.classList.contains('is-open')) {
            cerrarMenu(true);
        }
    });

    function alCambiarMedia(evento) {
        if (!evento.matches) {
            if (temporizadorOverlay) {
                window.clearTimeout(temporizadorOverlay);
                temporizadorOverlay = null;
            }
            body.classList.remove('sidebar-open');
            sidebar.classList.remove('is-open');
            overlay.classList.remove('is-visible');
            overlay.hidden = true;
            toggle.setAttribute('aria-expanded', 'false');
        }
        actualizarInert();
    }

    if (typeof media.addEventListener === 'function') {
        media.addEventListener('change', alCambiarMedia);
    } else if (typeof media.addListener === 'function') {
        media.addListener(alCambiarMedia);
    }

    actualizarInert();
})();
