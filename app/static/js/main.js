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

// Update user marker position
function updateUserMarker(lat, lon, title = 'Your Location') {
    if (userMarker) {
        userMarker.setLatLng([lat, lon]);
        userMarker.setPopupContent(title);
    } else {
        addUserMarker(lat, lon, title);
    }
}

// Add donor markers with custom styling based on distance
function addDonorMarkers(donors, userLat = null, userLon = null, radius = 10) {
    // Clear existing markers
    donorMarkers.forEach(marker => map.removeLayer(marker));
    donorMarkers = [];
    
    donors.forEach(donor => {
        if (donor.latitude && donor.longitude) {
            // Calculate distance if user location provided
            let distance = null;
            let isNearby = false;
            
            if (userLat && userLon) {
                distance = calculateDistance(userLat, userLon, donor.latitude, donor.longitude);
                isNearby = distance <= radius;
            }
            
            // Choose marker color based on distance
            const markerColor = isNearby ? '#28a745' : '#ffc107';
            
            const customIcon = L.divIcon({
                className: 'donor-marker',
                html: `<div style="background-color: ${markerColor}; width: 15px; height: 15px; border-radius: 50%; border: 2px solid white;"></div>`,
                iconSize: [15, 15]
            });
            
            const popupContent = `
                <b>${donor.name}</b><br>
                Blood Type: ${donor.blood_type}<br>
                ${distance ? `Distance: ${distance.toFixed(1)} km<br>` : ''}
                ${isNearby ? '<span class="badge bg-success">Nearby</span><br>' : ''}
                <button class="btn btn-sm btn-danger mt-2" onclick="window.showContactOptions(${donor.id}, '${donor.name.replace(/'/g, "\\'")}', '${donor.phone || ''}', '${donor.email || ''}')">
                    <i class="fas fa-phone-alt"></i> Contact
                </button>
            `;
            
            const marker = L.marker([donor.latitude, donor.longitude], { icon: customIcon })
                .addTo(map)
                .bindPopup(popupContent);
            
            donorMarkers.push(marker);
        }
    });
}

// Add hospital markers
function addHospitalMarkers(hospitals) {
    // Clear existing markers
    hospitalMarkers.forEach(marker => map.removeLayer(marker));
    hospitalMarkers = [];
    
    const hospitalIcon = L.divIcon({
        className: 'hospital-marker',
        html: '<i class="fas fa-hospital" style="color: #17a2b8; font-size: 20px;"></i>',
        iconSize: [20, 20]
    });
    
    hospitals.forEach(hospital => {
        const marker = L.marker([hospital.latitude, hospital.longitude], { icon: hospitalIcon })
            .addTo(map)
            .bindPopup(`
                <b>${hospital.name}</b><br>
                ${hospital.address}<br>
                Phone: ${hospital.phone}<br>
                ${hospital.distance_km ? `Distance: ${hospital.distance_km.toFixed(1)} km` : ''}
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
    
    return circle;
}

// Remove radius circle
function removeRadiusCircle() {
    if (circle) {
        map.removeLayer(circle);
        circle = null;
    }
}

// Calculate distance between two points
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Fit map bounds to show all markers
function fitMapBounds(markers) {
    if (markers.length === 0) return;
    
    const bounds = L.latLngBounds();
    markers.forEach(marker => {
        bounds.extend(marker.getLatLng());
    });
    map.fitBounds(bounds, { padding: [50, 50] });
}

// Center map on coordinates
function centerMap(lat, lon, zoom = 12) {
    map.setView([lat, lon], zoom);
}

// Clear all markers
function clearAllMarkers() {
    if (donorMarkers.length > 0) {
        donorMarkers.forEach(marker => map.removeLayer(marker));
        donorMarkers = [];
    }
    
    if (hospitalMarkers.length > 0) {
        hospitalMarkers.forEach(marker => map.removeLayer(marker));
        hospitalMarkers = [];
    }
}

// Get current map center
function getMapCenter() {
    return map.getCenter();
}

// Get current map zoom
function getMapZoom() {
    return map.getZoom();
}