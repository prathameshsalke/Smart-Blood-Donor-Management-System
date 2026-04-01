// Map functions for Leaflet.js

let map;
let userMarker;
let donorMarkers = [];
let hospitalMarkers = [];
let circle;

// Initialize map
function initMap(elementId, lat, lon, zoom = 12) {
    map = L.map(elementId).setView([lat, lon], zoom);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    return map;
}

// Add user marker
function addUserMarker(lat, lon, title = 'Your Location') {
    if (userMarker) {
        map.removeLayer(userMarker);
    }
    
    const customIcon = L.divIcon({
        className: 'custom-div-icon',
        html: '<div style="background-color: #dc3545; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white;"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });
    
    userMarker = L.marker([lat, lon], { icon: customIcon })
        .addTo(map)
        .bindPopup(title)
        .openPopup();
    
    map.setView([lat, lon]);
}

// Add donor markers
function addDonorMarkers(donors) {
    // Clear existing markers
    donorMarkers.forEach(marker => map.removeLayer(marker));
    donorMarkers = [];
    
    const donorIcon = L.icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    
    donors.forEach(donor => {
        if (donor.latitude && donor.longitude) {
            const marker = L.marker([donor.latitude, donor.longitude], { icon: donorIcon })
                .addTo(map)
                .bindPopup(`
                    <b>${donor.name}</b><br>
                    Blood Type: ${donor.blood_type}<br>
                    Distance: ${donor.distance_km} km<br>
                    <a href="/donor/profile/${donor.id}" class="btn btn-sm btn-danger mt-2">View Profile</a>
                `);
            
            donorMarkers.push(marker);
        }
    });
}

// Add hospital markers
function addHospitalMarkers(hospitals) {
    // Clear existing markers
    hospitalMarkers.forEach(marker => map.removeLayer(marker));
    hospitalMarkers = [];
    
    const hospitalIcon = L.icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    
    hospitals.forEach(hospital => {
        const marker = L.marker([hospital.latitude, hospital.longitude], { icon: hospitalIcon })
            .addTo(map)
            .bindPopup(`
                <b>${hospital.name}</b><br>
                ${hospital.address}<br>
                Phone: ${hospital.phone}<br>
                Distance: ${hospital.distance_km} km
            `);
        
        hospitalMarkers.push(marker);
    });
}

// Draw radius circle
function drawRadiusCircle(lat, lon, radius) {
    if (circle) {
        map.removeLayer(circle);
    }
    
    circle = L.circle([lat, lon], {
        color: '#dc3545',
        fillColor: '#f03',
        fillOpacity: 0.1,
        radius: radius * 1000 // Convert km to meters
    }).addTo(map);
}

// Search within radius
function searchWithinRadius(lat, lon, radius) {
    drawRadiusCircle(lat, lon, radius);
    
    // Fetch donors within radius
    fetch(`/api/donors/nearby?lat=${lat}&lon=${lon}&radius=${radius}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                addDonorMarkers(data.donors);
                
                // Show count
                const count = data.donors.length;
                alert(`Found ${count} donors within ${radius}km`);
            }
        })
        .catch(error => {
            console.error('Error searching donors:', error);
        });
}

// Get current location and center map
function centerOnUser() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                
                map.setView([lat, lon], 14);
                addUserMarker(lat, lon);
            },
            error => {
                console.error('Error getting location:', error);
                alert('Unable to get your location. Please enable location services.');
            }
        );
    } else {
        alert('Geolocation is not supported by your browser');
    }
}

// Add search control
function addSearchControl() {
    L.Control.geocoder({
        defaultMarkGeocode: false
    }).on('markgeocode', function(e) {
        const lat = e.geocode.center.lat;
        const lon = e.geocode.center.lng;
        
        map.setView([lat, lon], 14);
        addUserMarker(lat, lon, e.geocode.name);
    }).addTo(map);
}

// Export map as image
function exportMap() {
    // This would require additional libraries like leaflet-image
    console.log('Map export functionality would go here');
}