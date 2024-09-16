import React, { useEffect, useRef } from "react";
import JSMpeg from "@cycjimmy/jsmpeg-player";
import ServoControl from "./ServoControl";
import "./VdoFeed.css";

const VdoFeed = () => {
  const canvasRef = useRef(null);
  const playerRef = useRef(null);

  useEffect(() => {
    // เริ่มสตรีมวิดีโอเมื่อคอมโพเนนต์ถูกติดตั้ง
    playerRef.current = new JSMpeg.Player('ws://10.8.8.56:9999', {
      canvas: canvasRef.current,
    });

    return () => {
      // หยุดสตรีมวิดีโอเมื่อคอมโพเนนต์ถูกลบ
      if (playerRef.current) {
        playerRef.current.stop();
      }
    };
  }, []);

  const refreshVideo = () => {
    if (playerRef.current) {
      playerRef.current.stop();
      setTimeout(() => {
        playerRef.current.play(); // เริ่มเล่นใหม่หลังจากหยุดประมาณ 2 วินาที
      }, 2000);
    }
  };

  return (
    <div className="full-screen-video-container">
      <canvas ref={canvasRef} id="canvas"></canvas>
      <ServoControl onRefresh={refreshVideo} />
    </div>
  );
};

export default VdoFeed;
