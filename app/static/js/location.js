/**
 * Location handling and geocoding functionality
 */

class LocationManager {
    constructor() {
        this.userLocation = null;
        this.watchId = null;
        this.locationCallbacks = [];
        this.init();
    }

    init() {
        this.setupLocationButtons();
        this.loadSavedLocation();
        this.setupAddressAutocomplete();
    }

    setupLocationButtons() {
        document.querySelectorAll('[data-location-action]').forEach(button => {
            button.addEventListener('click', (e) => {
                const action = button.dataset.locationAction;
                switch(action) {
                    case 'detect':
                        this.detectLocation();
                        break;
                    case 'update':
                        this.updateLocation();
                        break;
                    case 'watch':
                        this.startWatching();
                        break;
                    case 'stop':
                        this.stopWatching();
                        break;
                }
            });
        });
    }

    async detectLocation(highAccuracy = true) {
        if (!navigator.geolocation) {
            this.showError('Geolocation is not supported by your browser');
            return null;
        }

        this.showLoading('Detecting your location...');

        try {
            const position = await this.getCurrentPosition(highAccuracy);
            this.userLocation = {
                lat: position.coords.latitude,
                lon: position.coords.longitude,
                accuracy: position.coords.accuracy,
                timestamp: new Date().toISOString()
            };

            this.saveLocation();
            this.updateLocationUI();
            this.reverseGeocode();
            this.triggerCallbacks();

            this.hideLoading();
            return this.userLocation;

        } catch (error) {
            console.error('Location detection error:', error);
            this.handleLocationError(error);
            return null;
        }
    }

    getCurrentPosition(highAccuracy) {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: highAccuracy,
                timeout: 10000,
                maximumAge: 0
            });
        });
    }

    startWatching() {
        if (!navigator.geolocation) return;

        this.watchId = navigator.geolocation.watchPosition(
            (position) => {
                this.userLocation = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: new Date().toISOString()
                };
                this.updateLocationUI();
                this.triggerCallbacks();
            },
            (error) => this.handleLocationError(error),
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );

        const watchBtn = document.querySelector('[data-location-action="watch"]');
        if (watchBtn) {
            watchBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Stop Watching';
            watchBtn.dataset.locationAction = 'stop';
        }
    }

    stopWatching() {
        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;

            const watchBtn = document.querySelector('[data-location-action="stop"]');
            if (watchBtn) {
                watchBtn.innerHTML = '<i class="fas fa-eye"></i> Start Watching';
                watchBtn.dataset.locationAction = 'watch';
            }
        }
    }

    async reverseGeocode() {
        if (!this.userLocation) return;

        const displayElement = document.getElementById('locationDisplay');
        if (!displayElement) return;

        displayElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting address...';

        try {
            // Using OpenStreetMap Nominatim API
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${this.userLocation.lat}&lon=${this.userLocation.lon}`
            );
            const data = await response.json();

            if (data.display_name) {
                displayElement.innerHTML = `
                    <i class="fas fa-map-pin"></i>
                    ${data.display_name.split(',')[0]}
                    <small class="text-muted">${this.userLocation.lat.toFixed(4)}, ${this.userLocation.lon.toFixed(4)}</small>
                `;

                // Update address fields if they exist
                this.fillAddressFields(data.address);
            }

        } catch (error) {
            console.error('Reverse geocoding error:', error);
            displayElement.innerHTML = `
                <i class="fas fa-map-marker-alt"></i>
                ${this.userLocation.lat.toFixed(6)}, ${this.userLocation.lon.toFixed(6)}
            `;
        }
    }

    fillAddressFields(address) {
        if (!address) return;

        const fieldMappings = {
            'address': address.road || address.path,
            'city': address.city || address.town || address.village,
            'state': address.state,
            'pincode': address.postcode,
            'country': address.country
        };

        Object.entries(fieldMappings).forEach(([field, value]) => {
            const input = document.getElementById(field);
            if (input && value && !input.value) {
                input.value = value;
            }
        });
    }

    async searchLocation(query) {
        if (!query || query.length < 3) return [];

        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`
            );
            const results = await response.json();

            return results.map(result => ({
                display: result.display_name,
                lat: parseFloat(result.lat),
                lon: parseFloat(result.lon)
            }));

        } catch (error) {
            console.error('Location search error:', error);
            return [];
        }
    }

    setupAddressAutocomplete() {
        const searchInput = document.getElementById('locationSearch');
        if (!searchInput) return;

        let timeout = null;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            const query = e.target.value;

            if (query.length < 3) {
                this.hideAutocomplete();
                return;
            }

            timeout = setTimeout(async () => {
                const results = await this.searchLocation(query);
                this.showAutocomplete(results);
            }, 500);
        });
    }

    showAutocomplete(results) {
        const container = document.getElementById('autocompleteResults');
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = '<div class="autocomplete-item disabled">No results found</div>';
            container.style.display = 'block';
            return;
        }

        let html = '';
        results.forEach(result => {
            html += `
                <div class="autocomplete-item" onclick="locationManager.selectLocation('${result.lat}', '${result.lon}', '${result.display}')">
                    <i class="fas fa-map-marker-alt"></i>
                    ${result.display}
                </div>
            `;
        });

        container.innerHTML = html;
        container.style.display = 'block';
    }

    hideAutocomplete() {
        const container = document.getElementById('autocompleteResults');
        if (container) {
            container.style.display = 'none';
        }
    }

    selectLocation(lat, lon, display) {
        this.userLocation = {
            lat: parseFloat(lat),
            lon: parseFloat(lon),
            timestamp: new Date().toISOString()
        };

        // Update inputs
        document.querySelectorAll('.latitude-input').forEach(input => {
            input.value = this.userLocation.lat;
        });
        document.querySelectorAll('.longitude-input').forEach(input => {
            input.value = this.userLocation.lon;
        });

        // Update display
        const displayElement = document.getElementById('locationDisplay');
        if (displayElement) {
            displayElement.innerHTML = `<i class="fas fa-map-pin"></i> ${display}`;
        }

        // Hide autocomplete
        this.hideAutocomplete();

        // Update map
        this.updateMap();

        // Trigger callbacks
        this.triggerCallbacks();
    }

    saveLocation() {
        if (!this.userLocation) return;

        localStorage.setItem('userLocation', JSON.stringify({
            ...this.userLocation,
            saved: new Date().toISOString()
        }));

        // Also save to session for current session
        sessionStorage.setItem('currentLocation', JSON.stringify(this.userLocation));
    }

    loadSavedLocation() {
        const saved = localStorage.getItem('userLocation');
        if (saved) {
            try {
                this.userLocation = JSON.parse(saved);
                this.updateLocationUI();
            } catch (e) {
                console.error('Error loading saved location:', e);
            }
        }
    }

    updateLocationUI() {
        if (!this.userLocation) return;

        // Update all location inputs
        document.querySelectorAll('.latitude-input, [id*="latitude"]').forEach(input => {
            input.value = this.userLocation.lat.toFixed(6);
        });

        document.querySelectorAll('.longitude-input, [id*="longitude"]').forEach(input => {
            input.value = this.userLocation.lon.toFixed(6);
        });

        // Update display elements
        document.querySelectorAll('.location-coords').forEach(el => {
            el.textContent = `${this.userLocation.lat.toFixed(6)}, ${this.userLocation.lon.toFixed(6)}`;
        });

        // Update status indicators
        document.querySelectorAll('.location-status').forEach(el => {
            el.innerHTML = '<i class="fas fa-check-circle text-success"></i> Location available';
            el.classList.add('text-success');
        });
    }

    updateMap() {
        if (!this.userLocation || typeof window.map === 'undefined') return;

        window.map.setView([this.userLocation.lat, this.userLocation.lon], 14);

        if (window.userMarker) {
            window.map.removeLayer(window.userMarker);
        }

        window.userMarker = L.marker([this.userLocation.lat, this.userLocation.lon])
            .addTo(window.map)
            .bindPopup('Your Location')
            .openPopup();
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
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

    onLocationChange(callback) {
        if (typeof callback === 'function') {
            this.locationCallbacks.push(callback);
        }
    }

    triggerCallbacks() {
        this.locationCallbacks.forEach(callback => {
            try {
                callback(this.userLocation);
            } catch (e) {
                console.error('Location callback error:', e);
            }
        });
    }

    showLoading(message) {
        const loader = document.getElementById('locationLoader');
        if (loader) {
            loader.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${message}`;
            loader.style.display = 'block';
        }
    }

    hideLoading() {
        const loader = document.getElementById('locationLoader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    handleLocationError(error) {
        let message = 'Location error occurred';

        switch(error.code) {
            case error.PERMISSION_DENIED:
                message = 'Location permission denied. Please enable location services.';
                break;
            case error.POSITION_UNAVAILABLE:
                message = 'Location information unavailable.';
                break;
            case error.TIMEOUT:
                message = 'Location request timed out.';
                break;
        }

        this.showError(message);
    }

    showError(message) {
        const errorDiv = document.getElementById('locationError');
        if (errorDiv) {
            errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }
}

// Initialize location manager
document.addEventListener('DOMContentLoaded', () => {
    window.locationManager = new LocationManager();
});