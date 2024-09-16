// src/component/Log.js
import React, { useEffect, useState, forwardRef } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import './Log.css';

const formatMessage = (message) => {
  try {
    const jsonString = message
      .replace(/^Message: /, '') // Remove the "Message: " prefix
      .replace(/'/g, '"'); // Replace single quotes with double quotes

    const jsonObject = JSON.parse(jsonString);

    for (const key in jsonObject) {
      if (jsonObject[key] === null) {
        jsonObject[key] = 'N/A'; // Set to 'N/A' if any value is null
      }
    }

    return jsonObject;
  } catch (error) {
    return null; // Return null to indicate invalid JSON message
  }
};

const Log = forwardRef(({ isVisible }, ref) => {
  const { ws } = useWebSocket();
  const [message, setMessage] = useState({
    mcc: 'N/A',
    mnc: 'N/A',
    cellID: 'N/A',
    pcid: 'N/A',
    earfcn: 'N/A',
    freq_band_ind: 'N/A',
    ul_bandwidth: 'N/A',
    dl_bandwidth: 'N/A',
    tac: 'N/A',
    rsrp: 'N/A',
    rsrq: 'N/A',
    rssi: 'N/A',
    sinr: 'N/A',
    latitude: 'N/A',
    longitude: 'N/A',
    time: 'N/A',
    total_voltage_percentage: 'N/A',
  });

  useEffect(() => {
    const handleMessage = (event) => {
      const newMessage = formatMessage(event.data);

      if (newMessage) {
        setMessage((prevMessage) => ({
          ...prevMessage,
          ...newMessage,
        }));
      }
    };

    if (ws) {
      ws.addEventListener('message', handleMessage);
      return () => {
        ws.removeEventListener('message', handleMessage);
      };
    }
  }, [ws]);

  // Handle the time display
  const formattedTime = message.time && message.time.includes('T') ? message.time.split('T')[1].split('.')[0] : 'N/A';

  return (
    <div className={`log-container ${isVisible ? 'visible' : 'hidden'}`} ref={ref}>
      <div className="log-card">
        <div><b>mcc:</b> {message.mcc}</div>
        <div><b>mnc:</b> {message.mnc}</div>
        <div><b>cellID:</b> {message.cellID}</div>
        <div><b>pcid:</b> {message.pcid}</div>
        <div><b>earfcn:</b> {message.earfcn}</div>
        <div><b>freq_band_ind:</b> {message.freq_band_ind}</div>
        <div><b>ul_bandwidth:</b> {message.ul_bandwidth}</div>
        <div><b>dl_bandwidth:</b> {message.dl_bandwidth}</div>
        <div><b>tac:</b> {message.tac}</div>
        <div><b>rsrp:</b> {message.rsrp}</div>
        <div><b>rsrq:</b> {message.rsrq}</div>
        <div><b>rssi:</b> {message.rssi}</div>
        <div><b>sinr:</b> {message.sinr}</div>
        <div><b>lat:</b> {parseFloat(message.latitude).toFixed(6)}</div>
        <div><b>long:</b> {parseFloat(message.longitude).toFixed(6)}</div>
        <div><b>time:</b> {formattedTime}</div>
        <div><b>battery:</b> {message.total_voltage_percentage}</div> 
      </div>
    </div>
  );
});

export default Log;
