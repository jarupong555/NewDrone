// src/component/MapComponent.js
import React, { useEffect, useState, useRef } from 'react';
import { GoogleMap, LoadScript, MarkerF, Polyline } from '@react-google-maps/api';
import { useWebSocket } from '../context/WebSocketContext';
import Card from './Card'; // Import your Card component
import './MapComponent.css';

const containerStyle = {
  width: '100%',
  height: '200px',
};

const center = {
  lat: 13.00,
  lng: 13.00,
};

const options = {
  disableDefaultUI: true,  // Disables all default UI controls
  zoomControl: false,      // Disables zoom controls
  streetViewControl: false, // Disables Street View control
  mapTypeControl: false,   // Disables map type control
  fullscreenControl: false, // Disables fullscreen control
};

const MapComponent = () => {
  const { ws } = useWebSocket();
  const [position, setPosition] = useState(center);
  const [positions, setPositions] = useState([]);
  const mapRef = useRef(null);

  useEffect(() => {
    const handleMessage = (event) => {
      try {
        const message = event.data.replace(/^Message: /, '').replace(/'/g, '"');
        if (message.startsWith('{') && message.endsWith('}')) {
          const data = JSON.parse(message);
          const { latitude, longitude } = data;

          if (latitude !== undefined && longitude !== undefined) {
            const newPosition = { lat: latitude, lng: longitude };

            // Update positions array
            setPositions((prevPositions) => [...prevPositions, newPosition]);

            // Set the new position
            setPosition(newPosition);
          }
        }
      } catch (error) {
        console.error('Invalid message format:', event.data, error);
      }
    };

    if (ws) {
      ws.addEventListener('message', handleMessage);
      return () => {
        ws.removeEventListener('message', handleMessage);
      };
    }
  }, [ws]);

  useEffect(() => {
    if (mapRef.current && positions.length > 0) {
      const bounds = new window.google.maps.LatLngBounds();

      // Extend the bounds to include all positions
      positions.forEach(position => bounds.extend(position));
      // Include the current position
      bounds.extend(position);

      // Fit the map to the bounds
      mapRef.current.fitBounds(bounds);
    }
  }, [positions, position]);

  return (
    <Card className="map-card">
      <LoadScript googleMapsApiKey="AIzaSyB4nXk5bJajZVx1OWN4esLGd5GQxmwb10M">
        <GoogleMap
          mapContainerStyle={containerStyle}
          center={position}
          zoom={13}
          options={options}
          onLoad={(map) => {
            mapRef.current = map;
          }}
        >
          <MarkerF position={position} />
          {positions.length > 1 && (
            <Polyline
              path={positions}
              options={{ strokeColor: '#0000FF', strokeOpacity: 1.0, strokeWeight: 2 }}
            />
          )}
        </GoogleMap>
      </LoadScript>
    </Card>
  );
};

export default MapComponent;
