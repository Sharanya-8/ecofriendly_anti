/**
 * Live Location Support for Weather Fetching
 * Uses browser Geolocation API to get user's coordinates
 */

class LiveLocation {
    constructor() {
        this.latitude = null;
        this.longitude = null;
        this.isSupported = 'geolocation' in navigator;
    }

    /**
     * Check if geolocation is supported
     */
    isLocationSupported() {
        return this.isSupported;
    }

    /**
     * Get current position
     * Returns Promise with {latitude, longitude}
     */
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!this.isSupported) {
                reject(new Error('Geolocation is not supported by your browser'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.latitude = position.coords.latitude;
                    this.longitude = position.coords.longitude;
                    resolve({
                        latitude: this.latitude,
                        longitude: this.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                (error) => {
                    let errorMessage = 'Unable to get location';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = 'Location permission denied. Please enable location access.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = 'Location information unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMessage = 'Location request timed out.';
                            break;
                    }
                    reject(new Error(errorMessage));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }

    /**
     * Fetch weather using live location
     */
    async fetchWeatherByLocation() {
        try {
            const position = await this.getCurrentPosition();
            
            const response = await fetch('/irrigation/weather/live', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: position.latitude,
                    longitude: position.longitude
                })
            });

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to fetch weather');
            }

            return data.weather;
        } catch (error) {
            throw error;
        }
    }
}

/**
 * Initialize live location button
 * Usage: Call this function on page load
 */
function initLiveLocationButton(buttonId, onSuccess, onError) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    const liveLocation = new LiveLocation();

    // Check if geolocation is supported
    if (!liveLocation.isLocationSupported()) {
        button.disabled = true;
        button.title = 'Geolocation not supported by your browser';
        return;
    }

    button.addEventListener('click', async function() {
        // Show loading state
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Getting location...';

        try {
            const weather = await liveLocation.fetchWeatherByLocation();
            
            // Call success callback
            if (onSuccess && typeof onSuccess === 'function') {
                onSuccess(weather);
            }

            // Show success message
            showNotification('Location detected: ' + weather.city, 'success');
        } catch (error) {
            console.error('Live location error:', error);
            
            // Call error callback
            if (onError && typeof onError === 'function') {
                onError(error);
            }

            // Show error message
            showNotification(error.message, 'danger');
        } finally {
            // Restore button state
            button.disabled = false;
            button.innerHTML = originalText;
        }
    });
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Try to use Bootstrap toast if available
    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove after hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    } else {
        // Fallback to alert
        alert(message);
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LiveLocation, initLiveLocationButton };
}
