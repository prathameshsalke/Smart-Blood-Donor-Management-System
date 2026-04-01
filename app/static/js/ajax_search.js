/**
 * AJAX Search functionality for blood donors and hospitals
 */

class SearchManager {
    constructor() {
        this.searchTimeout = null;
        this.init();
    }
    
    init() {
        this.setupDonorSearch();
        this.setupHospitalSearch();
        this.setupLocationSearch();
        this.setupBloodTypeFilter();
    }
    
    setupDonorSearch() {
        const donorSearch = document.getElementById('donorSearch');
        if (!donorSearch) return;
        
        donorSearch.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.searchDonors(e.target.value);
            }, 500);
        });
    }
    
    setupHospitalSearch() {
        const hospitalSearch = document.getElementById('hospitalSearch');
        if (!hospitalSearch) return;
        
        hospitalSearch.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.searchHospitals(e.target.value);
            }, 500);
        });
    }
    
    setupLocationSearch() {
        const locationBtn = document.getElementById('useMyLocation');
        if (!locationBtn) return;
        
        locationBtn.addEventListener('click', () => {
            this.getUserLocation();
        });
    }
    
    setupBloodTypeFilter() {
        const bloodTypeFilter = document.getElementById('bloodTypeFilter');
        if (!bloodTypeFilter) return;
        
        bloodTypeFilter.addEventListener('change', () => {
            this.filterByBloodType();
        });
    }
    
    async searchDonors(query) {
        const resultsContainer = document.getElementById('donorResults');
        if (!resultsContainer) return;
        
        // Show loading
        resultsContainer.innerHTML = this.getLoadingSpinner();
        
        try {
            // Get location from URL or use default
            const urlParams = new URLSearchParams(window.location.search);
            const lat = urlParams.get('lat') || '28.6139';
            const lon = urlParams.get('lon') || '77.2090';
            const radius = document.getElementById('radiusFilter')?.value || 10;
            
            const response = await fetch(`/api/donors/search?q=${encodeURIComponent(query)}&lat=${lat}&lon=${lon}&radius=${radius}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayDonorResults(data.donors, resultsContainer);
            } else {
                this.showError(resultsContainer, data.message);
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError(resultsContainer, 'Failed to search donors');
        }
    }
    
    async searchHospitals(query) {
        const resultsContainer = document.getElementById('hospitalResults');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = this.getLoadingSpinner();
        
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const lat = urlParams.get('lat') || '28.6139';
            const lon = urlParams.get('lon') || '77.2090';
            
            const response = await fetch(`/api/hospitals/search?q=${encodeURIComponent(query)}&lat=${lat}&lon=${lon}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayHospitalResults(data.hospitals, resultsContainer);
            } else {
                this.showError(resultsContainer, data.message);
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError(resultsContainer, 'Failed to search hospitals');
        }
    }
    
    displayDonorResults(donors, container) {
        if (!donors || donors.length === 0) {
            container.innerHTML = this.getNoResultsHTML();
            return;
        }
        
        let html = '<div class="donor-grid">';
        donors.forEach(donor => {
            html += `
                <div class="donor-card">
                    <div class="donor-avatar">
                        <img src="${donor.avatar || '/static/images/default-avatar.png'}" alt="${donor.name}">
                    </div>
                    <div class="donor-info">
                        <h5>${donor.name}</h5>
                        <span class="blood-type">${donor.blood_type}</span>
                        <p class="location"><i class="fas fa-map-marker-alt"></i> ${donor.distance_km} km away</p>
                        <p class="address">${donor.city}, ${donor.state}</p>
                        <button class="btn-contact" onclick="contactDonor(${donor.id})">
                            <i class="fas fa-phone"></i> Contact
                        </button>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
        
        // Update results count
        const countElement = document.getElementById('resultsCount');
        if (countElement) {
            countElement.textContent = donors.length;
        }
    }
    
    displayHospitalResults(hospitals, container) {
        if (!hospitals || hospitals.length === 0) {
            container.innerHTML = this.getNoResultsHTML();
            return;
        }
        
        let html = '<div class="hospital-grid">';
        hospitals.forEach(hospital => {
            html += `
                <div class="hospital-card">
                    <div class="hospital-icon">
                        <i class="fas fa-hospital"></i>
                    </div>
                    <div class="hospital-info">
                        <h5>${hospital.name}</h5>
                        <p class="address">${hospital.address}</p>
                        <p class="phone"><i class="fas fa-phone"></i> ${hospital.phone}</p>
                        <p class="distance"><i class="fas fa-map-marker-alt"></i> ${hospital.distance_km} km</p>
                        ${hospital.has_blood_bank ? '<span class="badge blood-bank">Has Blood Bank</span>' : ''}
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }
    
    async getUserLocation() {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser');
            return;
        }
        
        const locationBtn = document.getElementById('useMyLocation');
        if (locationBtn) {
            locationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting...';
            locationBtn.disabled = true;
        }
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                
                // Update URL with location
                const url = new URL(window.location);
                url.searchParams.set('lat', lat);
                url.searchParams.set('lon', lon);
                window.history.pushState({}, '', url);
                
                // Update location display
                const locationDisplay = document.getElementById('currentLocation');
                if (locationDisplay) {
                    locationDisplay.innerHTML = `Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}`;
                }
                
                // Refresh search
                const searchInput = document.getElementById('donorSearch');
                if (searchInput) {
                    this.searchDonors(searchInput.value);
                }
                
                if (locationBtn) {
                    locationBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Use My Location';
                    locationBtn.disabled = false;
                }
            },
            (error) => {
                console.error('Geolocation error:', error);
                alert('Failed to get your location. Please check permissions.');
                
                if (locationBtn) {
                    locationBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Use My Location';
                    locationBtn.disabled = false;
                }
            }
        );
    }
    
    filterByBloodType() {
        const bloodType = document.getElementById('bloodTypeFilter')?.value;
        if (!bloodType) return;
        
        const donorCards = document.querySelectorAll('.donor-card');
        donorCards.forEach(card => {
            const cardBloodType = card.querySelector('.blood-type')?.textContent;
            if (bloodType === 'all' || cardBloodType === bloodType) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    getLoadingSpinner() {
        return `
            <div class="text-center py-5">
                <div class="spinner-border text-danger" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Searching...</p>
            </div>
        `;
    }
    
    getNoResultsHTML() {
        return `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No Results Found</h5>
                <p class="text-muted">Try adjusting your search criteria</p>
            </div>
        `;
    }
    
    showError(container, message) {
        container.innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
            </div>
        `;
    }
}

// Initialize search manager
document.addEventListener('DOMContentLoaded', () => {
    window.searchManager = new SearchManager();
});

// Contact donor function
function contactDonor(donorId) {
    fetch(`/api/donors/${donorId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const donor = data.donor;
                alert(`Contact ${donor.name} at ${donor.phone}`);
                // You can also show a modal with contact info
            }
        })
        .catch(error => {
            console.error('Error fetching donor details:', error);
        });
}