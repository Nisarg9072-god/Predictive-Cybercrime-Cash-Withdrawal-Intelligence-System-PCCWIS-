import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';

// Custom icons for the map
const customMarkerIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const bankMarkerIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

export interface PredictedLocation {
  id: string;
  lat: number;
  lng: number;
  name: string;
  riskScore: number;
  probability: number;
}

function MapController({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
}

interface RiskMapProps {
  locations: PredictedLocation[];
  onLocationSelect: (loc: PredictedLocation) => void;
}

export function RiskMap({ locations, onLocationSelect }: RiskMapProps) {
  // Center on first location, or default NCR
  const defaultCenter: [number, number] = locations.length > 0 
    ? [locations[0].lat, locations[0].lng] 
    : [28.5355, 77.3910]; 

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '500px', borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--border-strong)' }}>
      <MapContainer center={defaultCenter} zoom={13} style={{ width: '100%', height: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapController center={defaultCenter} />

        {locations.map(loc => (
          <div key={`circles-${loc.id}`}>
            {loc.riskScore > 80 && (
              <>
                <Circle center={[loc.lat, loc.lng]} radius={800} pathOptions={{ color: 'var(--status-critical)', fillColor: 'var(--status-critical)', fillOpacity: 0.1 }} />
                <Circle center={[loc.lat, loc.lng]} radius={300} pathOptions={{ color: 'var(--status-critical)', fillColor: 'var(--status-critical)', fillOpacity: 0.2 }} />
              </>
            )}
          </div>
        ))}

        {locations.map(loc => (
          <Marker 
            key={loc.id} 
            position={[loc.lat, loc.lng]} 
            icon={loc.riskScore > 80 ? customMarkerIcon : bankMarkerIcon}
            eventHandlers={{
              click: () => onLocationSelect(loc),
            }}
          >
            <Popup className="dark-popup">
              <div style={{ color: 'var(--bg-primary)', padding: '0.25rem' }}>
                <h4 style={{ margin: '0 0 5px 0', fontSize: '14px', fontWeight: 'bold' }}>{loc.name}</h4>
                <p style={{ margin: '0', fontSize: '12px' }}>Risk Score: <span style={{ color: loc.riskScore > 80 ? '#e11d48' : '#2563eb', fontWeight: 'bold' }}>{loc.riskScore}%</span></p>
                <p style={{ margin: '2px 0 0 0', fontSize: '12px' }}>Cash-out Probability: {loc.probability}%</p>
                {loc.riskScore > 80 && (
                  <button 
                    onClick={() => alert(`SIMULATION: Dispatching PCR unit to ${loc.name}`)}
                    style={{ marginTop: '10px', padding: '4px 8px', backgroundColor: '#e11d48', color: '#fff', border: 'none', borderRadius: '4px', fontSize: '11px', cursor: 'pointer', width: '100%', fontWeight: 'bold' }}
                  >
                    DISPATCH UNIT
                  </button>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
