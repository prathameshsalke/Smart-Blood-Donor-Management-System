/**
 * Emergency Request Handling JavaScript
 */

class EmergencyManager {
    constructor() {
        this.userLocation = null;
        this.emergencyInterval = null;
        this.init();
    }

    init() {
        this.setupEmergencyForm();
        this.setupLocationDetection();
        this.setupEmergencyHotkey();
        this.checkEmergencyParams();
    }

    setupEmergencyForm() {
        const form = document.getElementById('emergencyForm');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitEmergencyRequest();
        });
    }

    setupLocationDetection() {
        const detectBtn = document.getElementById('detectLocation');
        if (!detectBtn) return;

        detectBtn.addEventListener('click', () => {
            this.detectUserLocation();
        });
    }

    setupEmergencyHotkey() {
        // Emergency hotkey (Ctrl+Shift+E)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'E') {
                e.preventDefault();
                this.showEmergencyModal();
            }
        });
    }

    checkEmergencyParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const bloodType = urlParams.get('blood_type');
        const lat = urlParams.get('lat');
        const lon = urlParams.get('lon');

        if (bloodType) {
            document.getElementById('bloodType')?.value = bloodType;
        }

        if (lat && lon) {
            this.userLocation = { lat: parseFloat(lat), lon: parseFloat(lon) };
            this.updateLocationDisplay();
        }
    }

    async detectUserLocation() {
        const detectBtn = document.getElementById('detectLocation');
        const locationStatus = document.getElementById('locationStatus');

        if (!navigator.geolocation) {
            this.showError('Geolocation is not supported by your browser');
            return;
        }

        // Update UI
        if (detectBtn) {
            detectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting...';
            detectBtn.disabled = true;
        }

        if (locationStatus) {
            locationStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting your location...';
        }

        try {
            const position = await this.getCurrentPosition();
            this.userLocation = {
                lat: position.coords.latitude,
                lon: position.coords.longitude
            };

            this.updateLocationDisplay();
            this.searchNearbyDonors();

            if (detectBtn) {
                detectBtn.innerHTML = '<i class="fas fa-check"></i> Location Detected';
                setTimeout(() => {
                    detectBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Detect My Location';
                    detectBtn.disabled = false;
                }, 2000);
            }

        } catch (error) {
            console.error('Location detection error:', error);
            this.showError('Failed to detect location. Please enter manually.');

            if (detectBtn) {
                detectBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Detect My Location';
                detectBtn.disabled = false;
            }

            if (locationStatus) {
                locationStatus.innerHTML = '<i class="fas fa-exclamation-circle"></i> Location detection failed';
            }
        }
    }

    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            });
        });
    }

    updateLocationDisplay() {
        if (!this.userLocation) return;

        const locationInputs = document.querySelectorAll('.location-coords');
        locationInputs.forEach(input => {
            if (input.id === 'latitude') {
                input.value = this.userLocation.lat.toFixed(6);
            }
            if (input.id === 'longitude') {
                input.value = this.userLocation.lon.toFixed(6);
            }
        });

        const locationDisplay = document.getElementById('currentLocation');
        if (locationDisplay) {
            locationDisplay.innerHTML = `
                <i class="fas fa-map-marker-alt"></i> 
                ${this.userLocation.lat.toFixed(6)}, ${this.userLocation.lon.toFixed(6)}
            `;
        }

        const locationStatus = document.getElementById('locationStatus');
        if (locationStatus) {
            locationStatus.innerHTML = '<i class="fas fa-check-circle text-success"></i> Location detected';
        }

        // Update map if exists
        this.updateMapLocation();
    }

    async submitEmergencyRequest() {
        const form = document.getElementById('emergencyForm');
        const submitBtn = document.getElementById('submitEmergency');

        // Validate form
        if (!this.validateEmergencyForm()) {
            return;
        }

        // Get form data
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Add location if available
        if (this.userLocation) {
            data.latitude = this.userLocation.lat;
            data.longitude = this.userLocation.lon;
        }

        // Show loading
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting Emergency...';
            submitBtn.disabled = true;
        }

        try {
            const response = await fetch('/api/requests/emergency', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showEmergencySuccess(result);
                this.startEmergencyTracking(result.request_id);
            } else {
                throw new Error(result.message || 'Failed to submit emergency request');
            }

        } catch (error) {
            console.error('Emergency submission error:', error);
            this.showError(error.message);

            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Try Again';
                submitBtn.disabled = false;
            }
        }
    }

    validateEmergencyForm() {
        const requiredFields = [
            'patient_name',
            'blood_type',
            'contact_name',
            'contact_phone'
        ];

        let isValid = true;

        requiredFields.forEach(field => {
            const input = document.getElementById(field);
            if (!input || !input.value.trim()) {
                this.highlightField(input, true);
                isValid = false;
            } else {
                this.highlightField(input, false);
            }
        });

        // Validate phone number
        const phone = document.getElementById('contact_phone')?.value;
        if (phone && !/^\d{10}$/.test(phone)) {
            this.showError('Please enter a valid 10-digit phone number');
            this.highlightField(document.getElementById('contact_phone'), true);
            isValid = false;
        }

        // Validate location
        if (!this.userLocation) {
            this.showError('Please detect your location first');
            isValid = false;
        }

        return isValid;
    }

    highlightField(field, isError) {
        if (!field) return;
        if (isError) {
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    }

    async searchNearbyDonors() {
        if (!this.userLocation) return;

        const bloodType = document.getElementById('bloodType')?.value;
        const resultsContainer = document.getElementById('nearbyDonors');

        if (!resultsContainer) return;

        resultsContainer.innerHTML = this.getLoadingHTML();

        try {
            const response = await fetch(
                `/api/donors/nearby?lat=${this.userLocation.lat}&lon=${this.userLocation.lon}&radius=10&blood_type=${bloodType || ''}`
            );
            const data = await response.json();

            if (data.status === 'success') {
                this.displayNearbyDonors(data.donors);
            } else {
                resultsContainer.innerHTML = this.getNoDonorsHTML();
            }

        } catch (error) {
            console.error('Error searching nearby donors:', error);
            resultsContainer.innerHTML = this.getErrorHTML();
        }
    }

    displayNearbyDonors(donors) {
        const container = document.getElementById('nearbyDonors');
        if (!container) return;

        if (!donors || donors.length === 0) {
            container.innerHTML = this.getNoDonorsHTML();
            return;
        }

        let html = '<div class="donors-list">';
        donors.slice(0, 5).forEach(donor => {
            html += `
                <div class="donor-item">
                    <div class="donor-info">
                        <strong>${donor.name}</strong>
                        <span class="blood-badge">${donor.blood_type}</span>
                        <span class="distance">${donor.distance_km} km</span>
                    </div>
                    <button class="btn-contact" onclick="emergencyManager.contactDonor(${donor.id})">
                        <i class="fas fa-phone"></i>
                    </button>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    }

    showEmergencySuccess(result) {
        const form = document.getElementById('emergencyForm');
        const successDiv = document.getElementById('emergencySuccess');

        if (form) form.style.display = 'none';
        
        if (successDiv) {
            successDiv.style.display = 'block';
            successDiv.innerHTML = `
                <div class="success-animation">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h3>Emergency Request Submitted!</h3>
                <p>Request ID: <strong>${result.request_id}</strong></p>
                <p>${result.notified_donors} donors have been notified.</p>
                <p>You will receive updates via SMS.</p>
                <div class="emergency-actions">
                    <button onclick="window.location.reload()" class="btn btn-outline-danger">
                        <i class="fas fa-plus"></i> New Request
                    </button>
                    <button onclick="window.print()" class="btn btn-outline-secondary">
                        <i class="fas fa-print"></i> Print Details
                    </button>
                </div>
            `;
        }

        // Play notification sound
        this.playEmergencySound();
    }

    startEmergencyTracking(requestId) {
        // Start polling for updates
        this.emergencyInterval = setInterval(() => {
            this.checkEmergencyStatus(requestId);
        }, 10000); // Check every 10 seconds

        // Show tracking info
        const trackingDiv = document.getElementById('emergencyTracking');
        if (trackingDiv) {
            trackingDiv.style.display = 'block';
        }
    }

    async checkEmergencyStatus(requestId) {
        try {
            const response = await fetch(`/api/requests/${requestId}/status`);
            const data = await response.json();

            if (data.status === 'fulfilled') {
                this.stopEmergencyTracking();
                this.showEmergencyFulfilled();
            } else {
                this.updateTrackingDisplay(data);
            }

        } catch (error) {
            console.error('Error checking status:', error);
        }
    }

    stopEmergencyTracking() {
        if (this.emergencyInterval) {
            clearInterval(this.emergencyInterval);
            this.emergencyInterval = null;
        }
    }

    updateTrackingDisplay(data) {
        const acceptedDonors = document.getElementById('acceptedDonors');
        const notifiedDonors = document.getElementById('notifiedDonors');

        if (acceptedDonors) {
            acceptedDonors.textContent = data.accepted_donors || 0;
        }

        if (notifiedDonors) {
            notifiedDonors.textContent = data.notified_donors || 0;
        }
    }

    showEmergencyFulfilled() {
        const trackingDiv = document.getElementById('emergencyTracking');
        if (trackingDiv) {
            trackingDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i>
                    Emergency request has been fulfilled!
                </div>
            `;
        }
    }

    showEmergencyModal() {
        const modal = new bootstrap.Modal(document.getElementById('emergencyModal'));
        if (modal) {
            modal.show();
            this.detectUserLocation(); // Auto-detect location
        }
    }

    showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container-fluid') || document.body;
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    playEmergencySound() {
        const audio = new Audio('/static/sounds/emergency.mp3');
        audio.play().catch(e => console.log('Audio play failed:', e));
    }

    contactDonor(donorId) {
        window.location.href = `/donor/contact/${donorId}?emergency=true`;
    }

    getLoadingHTML() {
        return `
            <div class="text-center py-4">
                <div class="spinner-border text-danger"></div>
                <p class="mt-2">Searching for nearby donors...</p>
            </div>
        `;
    }

    getNoDonorsHTML() {
        return `
            <div class="text-center py-4">
                <i class="fas fa-users-slash fa-3x text-muted"></i>
                <p class="mt-2">No donors found nearby</p>
                <p class="small text-muted">Try increasing search radius</p>
            </div>
        `;
    }

    getErrorHTML() {
        return `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-3x text-warning"></i>
                <p class="mt-2">Failed to search donors</p>
                <button onclick="emergencyManager.searchNearbyDonors()" class="btn btn-sm btn-outline-danger">
                    <i class="fas fa-redo"></i> Retry
                </button>
            </div>
        `;
    }

    updateMapLocation() {
        if (!this.userLocation || typeof initMap === 'undefined') return;

        if (window.map) {
            window.map.setView([this.userLocation.lat, this.userLocation.lon], 14);
            L.marker([this.userLocation.lat, this.userLocation.lon])
                .addTo(window.map)
                .bindPopup('Your Location')
                .openPopup();

            // Draw 10km radius
            L.circle([this.userLocation.lat, this.userLocation.lon], {
                color: '#dc3545',
                fillColor: '#f03',
                fillOpacity: 0.1,
                radius: 10000
            }).addTo(window.map);
        }
    }
}

// Initialize emergency manager
document.addEventListener('DOMContentLoaded', () => {
    window.emergencyManager = new EmergencyManager();
});