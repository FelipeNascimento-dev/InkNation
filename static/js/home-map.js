(function () {
    const mapEl = document.getElementById('ink-map');
    if (!mapEl || typeof L === 'undefined') return;

    const map = L.map('ink-map', {
        scrollWheelZoom: true,
    }).setView([-14.235, -51.9253], 4);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
    }).addTo(map);

    fetch('/api/studios/locations/')
        .then(function (response) {
            if (!response.ok) throw new Error('Falha ao carregar estúdios.');
            return response.json();
        })
        .then(function (studios) {
            if (!studios.length) return;

            const bounds = [];
            studios.forEach(function (studio) {
                const lat = studio.latitude;
                const lng = studio.longitude;
                const marker = L.marker([lat, lng]).addTo(map);

                const popupHtml =
                    '<div class="ink-map-popup">' +
                    '<strong>' + escapeHtml(studio.name) + '</strong>' +
                    '<a href="/studios/' + encodeURIComponent(studio.slug) + '/">Ver estúdio</a>' +
                    '</div>';

                marker.bindPopup(popupHtml, {
                    closeButton: false,
                    className: 'ink-leaflet-popup',
                });

                marker.on('mouseover', function () {
                    marker.openPopup();
                });
                marker.on('mouseout', function () {
                    marker.closePopup();
                });

                bounds.push([lat, lng]);
            });

            if (bounds.length === 1) {
                map.setView(bounds[0], 13);
            } else if (bounds.length > 1) {
                map.fitBounds(bounds, { padding: [40, 40] });
            }
        })
        .catch(function () {
            mapEl.classList.add('ink-map-error');
        });

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
})();
