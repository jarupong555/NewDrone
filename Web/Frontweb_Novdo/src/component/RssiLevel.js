// src/component/RssiLevel.js
import React, { useEffect, useState, useRef } from 'react';
import Log from './Log'; // Import the Log component
import { useWebSocket } from '../context/WebSocketContext';
import './RssiLevel.css';

const RssiLevel = () => {
  const { ws } = useWebSocket(); // Use WebSocket from context
  const [rssi, setRssi] = useState(null);
  const [isLogVisible, setIsLogVisible] = useState(false); // Track visibility state
  const logRef = useRef(null); // Reference to the Log component

  useEffect(() => {
    if (!ws) return; // Return if WebSocket is not available

    const handleMessage = (event) => {
      try {
        const message = event.data.replace(/^Message: /, '').replace(/'/g, '"');

        const isJSON = message.startsWith('{') && message.endsWith('}');
        if (isJSON) {
          const data = JSON.parse(message);
          if (typeof data.rssi === 'number') {
            setRssi(data.rssi); // Set RSSI value from message data
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', event.data, error);
      }
    };

    ws.addEventListener('message', handleMessage);

    return () => {
      ws.removeEventListener('message', handleMessage);
    };
  }, [ws]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isLogVisible && logRef.current && !logRef.current.contains(event.target)) {
        setIsLogVisible(false); // Hide the Log component when clicking outside
      }
    };

    if (isLogVisible) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isLogVisible]);

  const getRssiBars = () => {
    if (rssi >= -60) return 5;
    if (rssi >= -75) return 4;
    if (rssi >= -85) return 3;
    if (rssi >= -95) return 2;
    if (rssi > -94) return 1;
    return 0;
  };

  const bars = getRssiBars();

  const handleClick = () => {
    setIsLogVisible((prev) => !prev); // Toggle log visibility on click
  };

  return (
    <div className="rssi-container">
      <div className="rssi-bars" onClick={handleClick}>
        {[...Array(5)].map((_, i) => (
          <div key={i} className={`bar ${i < bars ? 'filled' : ''}`} />
        ))}
      </div>
      {/* Pass visibility state and reference to Log component */}
      <Log isVisible={isLogVisible} ref={logRef} />
    </div>
  );
};

export default RssiLevel;
