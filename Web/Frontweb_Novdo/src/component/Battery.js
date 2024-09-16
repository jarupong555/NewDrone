// src/component/Battery.js
import React, { useEffect, useState, useRef } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import './Battery.css';

const Battery = () => {
  const { ws } = useWebSocket();
  const [batteryPercentage, setBatteryPercentage] = useState(100); // Default to 100%
  const [batteryCells, setBatteryCells] = useState([]); // To hold battery cell data
  const [isTooltipVisible, setIsTooltipVisible] = useState(false); // Track if the tooltip is visible
  const [totalVoltage, setTotalVoltage] = useState(0); // Default to 0
  const [hasLowPercentageCell, setHasLowPercentageCell] = useState(false); // Track if there's a low percentage cell
  const batteryRef = useRef(null); // Reference to the Battery component

  useEffect(() => {
    const handleMessage = (event) => {
      try {
        const message = event.data.replace(/^Message: /, "").replace(/'/g, '"');
        if (message.startsWith("{") && message.endsWith("}")) {
          const data = JSON.parse(message);

          // Handle battery data
          if (data.total_voltage_percentage !== null) {
            setBatteryPercentage(
              data.total_voltage_percentage !== null
                ? data.total_voltage_percentage
                : "N/A"
            );
            setBatteryCells(data.battery || []); // Update battery cells data
            setTotalVoltage(
              data.total_voltage !== null ? data.total_voltage : "N/A"
            ); // Update total voltage

            // Check for percentage deviations in cells
            const lowPercentageCells = data.battery
              .filter((cell) => cell.percentage < 5)
              .map((cell) => `Cell ${cell.cell} is below 5%`);

            setHasLowPercentageCell(lowPercentageCells.length > 0); // Update the state based on low percentage cells
          }
        }
      } catch (error) {
        console.error("Invalid message format:", event.data, error);
      }
    };

    if (ws) {
      ws.addEventListener("message", handleMessage);
      return () => {
        ws.removeEventListener("message", handleMessage);
      };
    }
  }, [ws]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isTooltipVisible && batteryRef.current && !batteryRef.current.contains(event.target)) {
        setIsTooltipVisible(false); // Hide the tooltip when clicking outside
      }
    };

    if (isTooltipVisible) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isTooltipVisible]);

  const toggleTooltip = () => {
    setIsTooltipVisible((prev) => !prev); // Toggle the tooltip visibility
  };

  return (
    <div className="battery-container">
      <span className="total-voltage">
        {totalVoltage !== null ? `${totalVoltage}V` : "N/A"}
      </span>
      <div
        className={`battery-icon ${hasLowPercentageCell ? "battery-icon-warning" : ""}`}
        onClick={toggleTooltip} // Toggle tooltip visibility on click
        ref={batteryRef}
      >
        <div
          className="battery-level"
          style={{
            width: typeof batteryPercentage === "number" ? `${batteryPercentage}%` : "0%",
          }}
        ></div>
        {isTooltipVisible && (
          <div className="battery-tooltip">
            {batteryCells.length === 0 ? (
              <div>
                <div>Cell N/A: Voltage: N/A Percentage: N/A%</div>
              </div>
            ) : (
              batteryCells.map((cell) => (
                <div key={cell.cell} className="battery-tooltip-cell">
                  <div>
                    <b>Cell</b> {cell.cell}: <b>Voltage:</b> {cell.voltage.toFixed(2)}V <b>Percentage:</b> {cell.percentage}%
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      <span className="battery-percentage">
        {batteryPercentage !== null ? `${Math.floor(batteryPercentage)}%` : "N/A"}
      </span>
    </div>
  );
};

export default Battery;
