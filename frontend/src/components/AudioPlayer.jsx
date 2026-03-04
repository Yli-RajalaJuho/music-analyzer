import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";

// Global registry of active players so we can stop others when starting a new one
window.__wavesurfer_players = window.__wavesurfer_players || [];

function AudioPlayer({ url }) {
  const waveformRef = useRef(null);
  const wavesurfer = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (waveformRef.current) {
      if (wavesurfer.current) {
        wavesurfer.current.destroy();
      }

      wavesurfer.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: ["#ffff", "#242424"],
        progressColor: "#ffff",
        height: 70,
        responsive: true,
      });

      wavesurfer.current.load(url);

      // Handle play/pause state updates
      wavesurfer.current.on("play", () => setIsPlaying(true));
      wavesurfer.current.on("pause", () => setIsPlaying(false));
      wavesurfer.current.on("finish", () => setIsPlaying(false));

      // Register this instance globally
      window.__wavesurfer_players.push(wavesurfer.current);
    }

    return () => {
      // Remove from registry on unmount
      window.__wavesurfer_players = window.__wavesurfer_players.filter(
        (ws) => ws !== wavesurfer.current,
      );

      wavesurfer.current?.destroy();
    };
  }, [url]);

  const playPause = () => {
    if (!wavesurfer.current) return;

    if (!wavesurfer.current.isPlaying()) {
      // Pause ALL other players
      window.__wavesurfer_players.forEach((ws) => {
        if (ws !== wavesurfer.current) ws.pause();
      });
    }

    wavesurfer.current.playPause();
  };

  return (
    <div className="player-wrapper">
      <div className="waveform-container">
        <button onClick={playPause} className="playpause-btn">
          {isPlaying ? "⏸" : "▶"}
        </button>
        <div ref={waveformRef} className="waveform"></div>
      </div>
    </div>
  );
}

export default AudioPlayer;
