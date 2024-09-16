// src/component/ServoControl.js
import React, { useState } from "react";
import { useWebSocket } from "../context/WebSocketContext";
import "./ServoControl.css";

const ServoControl = ({ onRefresh }) => {
  const { ws } = useWebSocket();
  const [intervalId, setIntervalId] = useState(null);

  const sendCommand = (command) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(command);
    } else {
      console.error("WebSocket is not open or not available");
    }
  };

  const handleMouseDown = (command) => {
    const id = setInterval(() => {
      sendCommand(command);
    }, 100); // ส่งคำสั่งทุก 100ms
    setIntervalId(id);
  };

  const handleMouseUp = () => {
    clearInterval(intervalId);
    setIntervalId(null);
  };

  return (
    <div className="servo-container">
      <div className="control-buttons">
        <div className="direction-buttons">
          <button
            className="btn btn-primary"
            onMouseDown={() => handleMouseDown("up")}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onClick={() => sendCommand("up")}
          >
            ↑
          </button>
          <div className="horizontal-buttons">
            <button
              className="btn btn-secondary"
              onClick={() => sendCommand("center")}
            >
              ⬤
            </button>
          </div>
          <button
            className="btn btn-primary"
            onMouseDown={() => handleMouseDown("down")}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onClick={() => sendCommand("down")}
          >
            ↓
          </button>
        </div>
        <div className="extreme-buttons">
          <button
            className="btn btn-primary"
            onClick={() => sendCommand("upmax")}
          >
            เงย
          </button>
          <button
            className="btn btn-primary"
            onClick={() => sendCommand("downmax")}
          >
            ก้ม
          </button>
        </div>
        <div className="extreme-buttons">
          <button
            className="btn btn-primary"
            onClick={() => sendCommand("on")}
          >
            เปิด
          </button>
          <button
            className="btn btn-primary"
            onClick={() => sendCommand("off")}
          >
            ปิด
          </button>
        </div>
        <div className="refresh-button">
          <button onClick={onRefresh}>รีเฟรช</button>
        </div>
      </div>
    </div>
  );
};

export default ServoControl;
