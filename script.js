function initMap() {
    const map = L.map('map').setView([28.5383, -81.3792], 10); // Orlando, FL

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const floodedZones = [
        { lat: 28.5383, lng: -81.3792, title: 'Zone 1: Accessible' },
        { lat: 28.5500, lng: -81.4000, title: 'Zone 2: Limited Access' },
        { lat: 28.5400, lng: -81.3700, title: 'Zone 3: No Access' },
        { lat: 28.5450, lng: -81.3750, title: 'Zone 4: Accessible' },
        { lat: 28.5300, lng: -81.3950, title: 'Zone 5: Limited Access' },
        { lat: 28.5250, lng: -81.3850, title: 'Zone 6: No Access' }
    ];

    floodedZones.forEach(zone => {
        L.marker([zone.lat, zone.lng]).addTo(map).bindPopup(zone.title);
    });

    const geocoder = L.Control.geocoder({
        defaultMarkGeocode: false
    })
    .on('markgeocode', function(e) {
        const latlng = e.geocode.center;
        const marker = L.marker(latlng).addTo(map);
        map.setView(latlng, 16);
        marker.bindPopup(e.geocode.name).openPopup();

        // Check if the searched location is within a flooded zone
        let inFloodZone = false;
        floodedZones.forEach(zone => {
            const distance = map.distance(latlng, L.latLng(zone.lat, zone.lng));
            if (distance < 500) { // Assuming a 500-meter radius for simplicity
                inFloodZone = true;
                alert(`Warning: You are in a flooded zone - ${zone.title}`);
            }
        });

        if (!inFloodZone) {
            alert('You are not in a flooded zone.');
        }
    })
    .addTo(map);

    // Event listeners for checkboxes
    document.getElementById('disability').addEventListener('change', function() {
        document.getElementById('disabilityCount').disabled = !this.checked;
    });

    document.getElementById('children').addEventListener('change', function() {
        document.getElementById('childrenCount').disabled = !this.checked;
    });

    document.getElementById('pets').addEventListener('change', function() {
        document.getElementById('petsCount').disabled = !this.checked;
    });

    document.getElementById('elders').addEventListener('change', function() {
        document.getElementById('eldersCount').disabled = !this.checked;
    });
}

function submitUserInfo() {
    const disability = document.getElementById('disability').checked;
    const disabilityCount = document.getElementById('disabilityCount').value || 0;
    const children = document.getElementById('children').checked;
    const childrenCount = document.getElementById('childrenCount').value || 0;
    const pets = document.getElementById('pets').checked;
    const petsCount = document.getElementById('petsCount').value || 0;
    const elders = document.getElementById('elders').checked;
    const eldersCount = document.getElementById('eldersCount').value || 0;
    const evacuationRoutes = document.getElementById('evacuationRoutes').checked;

    alert(`User Info:
Disability: ${disability} (${disabilityCount})
Children: ${children} (${childrenCount})
Pets: ${pets} (${petsCount})
Elders: ${elders} (${eldersCount})
Need Evacuation Routes: ${evacuationRoutes}`);

    if (evacuationRoutes) {
        displayEvacuationRoutes();
    }
}

function displayEvacuationRoutes() {
    const map = L.map('map').setView([28.5383, -81.3792], 10); // Ensure map instance

    const evacuationRoutes = [
        // Connect each flooded zone to a safe zone (example coordinates)
        [
            [28.5383, -81.3792], // Zone 1
            [28.6000, -81.4000]  // Safe Zone
        ],
        [
            [28.5500, -81.4000], // Zone 2
            [28.6000, -81.4000]  // Safe Zone
        ],
        [
            [28.5400, -81.3700], // Zone 3
            [28.6000, -81.4000]  // Safe Zone
        ],
        [
            [28.5450, -81.3750], // Zone 4
            [28.6000, -81.4000]  // Safe Zone
        ],
        [
            [28.5300, -81.3950], // Zone 5
            [28.6000, -81.4000]  // Safe Zone
        ],
        [
            [28.5250, -81.3850], // Zone 6
            [28.6000, -81.4000]  // Safe Zone
        ]
    ];

    evacuationRoutes.forEach(route => {
        L.polyline(route, { color: 'blue' }).addTo(map);
    });
}

document.addEventListener('DOMContentLoaded', initMap);





