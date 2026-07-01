(function () {
  const mapEl = document.getElementById('map');
  if (!mapEl || typeof L === 'undefined') return;

  const map = L.map('map').setView([-14.235, -51.9253], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);

  fetch('/api/studios/')
    .then((res) => res.json())
    .then((studios) => {
      studios.forEach((studio) => {
        const popup = `
          <div class="ink-map-popup">
            <strong>${studio.name}</strong>
            <p>${studio.city}</p>
            <a href="/studios/${studio.slug}/">Ver estúdio</a>
          </div>`;
        L.marker([studio.latitude, studio.longitude])
          .addTo(map)
          .bindPopup(popup);
      });
    })
    .catch(() => {});
})();
