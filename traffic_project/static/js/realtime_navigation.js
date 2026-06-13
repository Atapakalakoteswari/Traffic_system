let map;
let currentRoute = null;
let selectedRouteIndex = null;
let startLocation = null;
let endLocation = null;
let allRoutesData = [];
let trafficConditions = null;
let refreshInterval = null;

const defaultLocation = { lat: 20.5937, lng: 78.9629 };
function formatDuration(minutes) {
    if (minutes >= 60) {
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        if (mins === 0) {
            return `${hours}h`;
        }
        return `${hours}h ${mins}min`;
    }
    return `${Math.round(minutes)}min`;
}

function initMap() {
    map = L.map('map').setView([defaultLocation.lat, defaultLocation.lng], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
}

async function geocodeAddress(address) {
    if (!address || address.trim() === '') return null;
    try {
        const searchQuery = address.includes('India') ? address : `${address}, India`;
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=1`,
            { headers: { 'User-Agent': 'TrafficPredictionSystem/1.0' } }
        );
        const data = await response.json();
        if (data && data.length > 0) {
            return {
                lat: parseFloat(data[0].lat),
                lng: parseFloat(data[0].lon),
                name: data[0].display_name
            };
        }
        return null;
    } catch (error) {
        console.error('Geocoding error:', error);
        return null;
    }
}

async function getRoutesFromBackend(startLoc, endLoc, startAddr, endAddr) {
    try {
        const response = await fetch('/calculate-route/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                start_lat: startLoc.lat,
                start_lng: startLoc.lng,
                end_lat: endLoc.lat,
                end_lng: endLoc.lng,
                start_address: startAddr,
                end_address: endAddr
            })
        });
        const data = await response.json();
        
        if (data.traffic_conditions) {
            trafficConditions = data.traffic_conditions;
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching routes:', error);
        return null;
    }
}

function displayRoutes(routes) {
    const container = document.getElementById('routes-list');
    const routesContainer = document.getElementById('routes-container');
    
    container.innerHTML = '';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'mb-3';
    headerDiv.innerHTML = `<strong>Available Routes (${routes.length})</strong>`;
    container.appendChild(headerDiv);
    
    routes.forEach((route, index) => {
        const routeCard = document.createElement('div');
        routeCard.className = 'route-card';
        if (index === 0) routeCard.classList.add('selected');
        
        const congestionColor = route.congestion === 'High' ? '#dc3545' : 
                               route.congestion === 'Medium' ? '#ffc107' : '#28a745';
        
        const timeDiff = route.duration - route.normal_duration;
        const formattedDuration = formatDuration(route.duration);
        const formattedNormalDuration = formatDuration(route.normal_duration);
        const delayText = timeDiff > 0 ? `<small class="text-danger">(+${formatDuration(timeDiff)} delay)</small>` : 
                          timeDiff < 0 ? `<small class="text-success">(-${formatDuration(Math.abs(timeDiff))} faster)</small>` : '';
        
        routeCard.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="route-icon" style="background: ${route.color}20;">
                    <i class="fas fa-${route.icon}" style="color: ${route.color}"></i>
                </div>
                <div class="flex-grow-1">
                    <h6 class="mb-1">
                        ${route.name}
                        ${route.congestion === 'High' ? '<span style="color: #dc3545; font-size: 12px;">Heavy Traffic</span>' : ''}
                        ${route.congestion === 'Medium' ? '<span style="color: #ffc107; font-size: 12px;">Moderate Traffic</span>' : ''}
                        ${route.congestion === 'Low' ? '<span style="color: #28a745; font-size: 12px;">Light Traffic</span>' : ''}
                    </h6>
                    <small class="text-muted">
                        <i class="fas fa-road"></i> ${route.distance} km &nbsp;
                        <i class="fas fa-clock"></i> ${formattedDuration}
                        ${delayText}
                    </small>
                    <br>
                    <small class="text-muted">${route.description || 'Real road route'}</small>
                </div>
                <div style="text-align: right;">
                    ${index === 0 ? '<span class="badge bg-secondary">(Recommended)</span>' : ''}
                    <div class="mt-1">
                        <span class="badge" style="background: ${congestionColor}; color: white;">
                            ${route.congestion}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        routeCard.onclick = () => selectRoute(route, index);
        container.appendChild(routeCard);
    });
    
    routesContainer.style.display = 'block';
}

function displayRouteOnMap(route, startPoint, endPoint) {
    if (currentRoute) {
        map.removeLayer(currentRoute);
    }
    
    if (route.geometry && Array.isArray(route.geometry) && route.geometry.length > 0) {
        console.log(`Displaying REAL route with ${route.geometry.length} points`);
        
        let points = route.geometry;
        
        if (points[0] && Array.isArray(points[0])) {
            if (Math.abs(points[0][0]) > 180) {
                points = points.map(p => [p[1], p[0]]);
            }
        }
        
        const lineWeight = route.congestion === 'High' ? 6 : 
                          route.congestion === 'Medium' ? 5 : 4;
        
        currentRoute = L.polyline(points, {
            color: route.color,
            weight: lineWeight,
            opacity: 0.9,
            lineJoin: 'round',
            lineCap: 'round'
        }).addTo(map);
        
        const formattedDuration = formatDuration(route.duration);
        currentRoute.bindPopup(`
            <b>${route.name}</b><br>
            <i class="fas fa-road"></i> Distance: ${route.distance} km<br>
            <i class="fas fa-clock"></i> Duration: ${formattedDuration}<br>
            <i class="fas fa-traffic-light"></i> Traffic: ${route.congestion}
        `);
        
        map.fitBounds(currentRoute.getBounds(), { padding: [50, 50] });
        
    } else {
        console.log("No geometry, creating curved line");
        const midPoint = [
            (startPoint[0] + endPoint[0]) / 2,
            (startPoint[1] + endPoint[1]) / 2
        ];
        
        if (route.type === 'shortest') {
            midPoint[0] += 0.01;
        } else if (route.type === 'alternative') {
            midPoint[0] -= 0.01;
        }
        
        const routePoints = [startPoint, midPoint, endPoint];
        
        currentRoute = L.polyline(routePoints, {
            color: route.color,
            weight: 4,
            opacity: 0.8,
            dashArray: '5, 10'
        }).addTo(map);
        
        const bounds = L.latLngBounds([startPoint, endPoint]);
        map.fitBounds(bounds, { padding: [50, 50] });
    }
    
    if (window.startMarker) window.startMarker.remove();
    if (window.endMarker) window.endMarker.remove();
    
    const startIcon = L.divIcon({
        html: '<div style="background: #28a745; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 2px #28a745;"></div>',
        iconSize: [20, 20]
    });
    
    const endIcon = L.divIcon({
        html: '<div style="background: #dc3545; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 2px #dc3545;"></div>',
        iconSize: [20, 20]
    });
    
    window.startMarker = L.marker(startPoint, { icon: startIcon }).addTo(map);
    window.endMarker = L.marker(endPoint, { icon: endIcon }).addTo(map);
    
    window.startMarker.bindTooltip('Start');
    window.endMarker.bindTooltip('Destination');
}

function selectRoute(route, index) {
    selectedRouteIndex = index;
    
    document.querySelectorAll('.route-card').forEach((card, i) => {
        card.classList.remove('selected');
    });
    
    const routeCards = document.querySelectorAll('.route-card');
    if (routeCards[index + 1]) {
        routeCards[index + 1].classList.add('selected');
    }
    
    const congestionColor = route.congestion === 'High' ? '#dc3545' : 
                           route.congestion === 'Medium' ? '#ffc107' : '#28a745';
    
    const timeDiff = route.duration - route.normal_duration;
    const formattedDuration = formatDuration(route.duration);
    const formattedNormalDuration = formatDuration(route.normal_duration);
    const formattedTimeDiff = formatDuration(Math.abs(timeDiff));
    
    // Show route info panel
    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-details').innerHTML = `
        <div style="padding: 15px; border-left: 4px solid ${route.color}; background: white; border-radius: 10px;">
            <h6 class="mb-2">
                ${route.name}
                ${index === 0 ? '<span class="badge bg-secondary ms-2">(Recommended)</span>' : ''}
            </h6>
            
            <div class="row mt-3">
                <div class="col-6">
                    <small class="text-muted">Distance</small>
                    <div class="fw-bold">${route.distance} km</div>
                </div>
                <div class="col-6">
                    <small class="text-muted">Duration</small>
                    <div class="fw-bold">${formattedDuration}</div>
                </div>
            </div>
            
            <div class="row mt-2">
                <div class="col-6">
                    <small class="text-muted">Normal Time</small>
                    <div>${formattedNormalDuration}</div>
                </div>
                <div class="col-6">
                    <small class="text-muted">Traffic Impact</small>
                    <div class="${timeDiff > 0 ? 'text-danger' : 'text-success'}">
                        ${timeDiff > 0 ? `+ ${formattedTimeDiff} delay` : timeDiff < 0 ? `${formattedTimeDiff} faster` : 'On time'}
                    </div>
                </div>
            </div>
            
            <div class="mt-2">
                <small class="text-muted">Traffic Condition</small>
                <div>
                    <span class="badge" style="background: ${congestionColor}; color: white; padding: 5px 10px;">
                        ${route.congestion} Traffic
                    </span>
                </div>
            </div>
            
            <div class="mt-2">
                <small class="text-muted">Route Description</small>
                <div class="text-muted small">${route.description || 'Real road route via OSRM'}</div>
            </div>
            
            ${route.congestion === 'High' ? 
                '<div class="alert alert-warning mt-3 mb-0 small">Heavy traffic expected. Consider leaving earlier or taking alternative route.</div>' : 
                route.congestion === 'Medium' ? 
                '<div class="alert alert-info mt-3 mb-0 small">Moderate traffic. Allow extra time for your journey.</div>' :
                '<div class="alert alert-success mt-3 mb-0 small">Light traffic. Enjoy your smooth journey!</div>'
            }
        </div>
    `;
    
    const startPoint = [startLocation.lat, startLocation.lng];
    const endPoint = [endLocation.lat, endLocation.lng];
    displayRouteOnMap(route, startPoint, endPoint);
}

async function findRoutes() {
    const startAddress = document.getElementById('start-location').value;
    const endAddress = document.getElementById('end-location').value;
    
    if (!startAddress) { alert('Please enter start location'); return; }
    if (!endAddress) { alert('Please enter destination'); return; }
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('routes-container').style.display = 'none';
    document.getElementById('route-info').style.display = 'none';
    
    const startLoc = await geocodeAddress(startAddress);
    if (!startLoc) {
        alert('Could not find start location. Please try a different address.');
        document.getElementById('loading').style.display = 'none';
        return;
    }
    
    const destLoc = await geocodeAddress(endAddress);
    if (!destLoc) {
        alert('Could not find destination. Please try a different address.');
        document.getElementById('loading').style.display = 'none';
        return;
    }
    
    startLocation = startLoc;
    endLocation = destLoc;
    
    if (window.startMarker) window.startMarker.remove();
    if (window.endMarker) window.endMarker.remove();
    
    const result = await getRoutesFromBackend(startLocation, endLocation, startAddress, endAddress);
    
    document.getElementById('loading').style.display = 'none';
    
    if (result && result.routes && result.routes.length > 0) {
        allRoutesData = result.routes;
        displayRoutes(allRoutesData);
        
        if (allRoutesData.length > 0) {
            selectRoute(allRoutesData[0], 0);
        }
    } else {
        alert('Could not find routes. Please try again.');
    }
    
    const bounds = L.latLngBounds([startLocation.lat, startLocation.lng], [endLocation.lat, endLocation.lng]);
    map.fitBounds(bounds, { padding: [50, 50] });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function startTrafficRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(() => {
        if (startLocation && endLocation) {
            console.log('Refreshing traffic data...');
            findRoutes();
        }
    }, 300000); 
}

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    startTrafficRefresh();
    
    const startInput = document.getElementById('start-location');
    const endInput = document.getElementById('end-location');
    const findBtn = document.getElementById('find-btn');
    
    if (startInput) {
        startInput.addEventListener('keypress', (e) => { 
            if (e.key === 'Enter') findRoutes(); 
        });
    }
    if (endInput) {
        endInput.addEventListener('keypress', (e) => { 
            if (e.key === 'Enter') findRoutes(); 
        });
    }
    if (findBtn) {
        findBtn.onclick = findRoutes;
    }
});