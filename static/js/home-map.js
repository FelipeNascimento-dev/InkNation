(function () {
    const mapEl = document.getElementById('ink-map');
    if (!mapEl || typeof L === 'undefined') return;

    const map = L.map('ink-map', {
        scrollWheelZoom: true,
        zoomControl: true,
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

                const marker = L.circleMarker([lat, lng], {
                    radius: 8,
                    fillColor: '#e31b23',
                    color: '#ffffff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 1,
                    className: 'ink-map-marker',
                }).addTo(map);

                const popupHtml = buildPopupHtml(studio);

                marker.bindPopup(popupHtml, {
                    closeButton: false,
                    className: 'ink-leaflet-popup',
                    offset: [0, -4],
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
                map.fitBounds(bounds, { padding: [48, 48] });
            }
        })
        .catch(function () {
            mapEl.classList.add('ink-map-error');
        });

    function buildPopupHtml(studio) {
        const coverHtml = '<img src="' + escapeAttr(studio.cover_url) + '" alt="">';

        const location = escapeHtml(studio.city) + ' · ' + escapeHtml(studio.state);
        const artistLabel = studio.artist_count === 1 ? 'artista' : 'artistas';
        const detailUrl = '/studios/' + encodeURIComponent(studio.slug) + '/';

        return (
            '<div class="ink-map-popup">' +
                '<div class="ink-map-popup-cover">' + coverHtml + '</div>' +
                '<div class="ink-map-popup-body">' +
                    '<strong>' + escapeHtml(studio.name) + '</strong>' +
                    '<span class="ink-map-popup-location">' + location + '</span>' +
                    '<div class="ink-map-popup-meta">' +
                        '<span>' + studio.artist_count + ' ' + artistLabel + '</span>' +
                    '</div>' +
                    '<a href="' + detailUrl + '" class="ink-map-popup-btn">Ver estúdio</a>' +
                '</div>' +
            '</div>'
        );
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeAttr(text) {
        return escapeHtml(text).replace(/"/g, '&quot;');
    }
})();
