import AudioPlayer from "../components/AudioPlayer";

function ResultsDisplay({ results }) {
  if (!results) return null;

  const { bpm, key, session_id } = results;

  return (
    <div className="results-display">
      <h1>Results</h1>
      <div className="results-div-row">
        <p className="results-box">🥁 {bpm} bpm</p>
        <p className="results-box">🎶 {key}</p>
      </div>

      {session_id !== "no separation" && (
        <div className="results-container">
          <div className="stem-results-box">
            <p>Vocals</p>
            <AudioPlayer
              url={`http://localhost:8000/download/${results.session_id}/vocals`}
            />
            <a
              className="stem-download-btn"
              href={`http://localhost:8000/download/${session_id}/vocals`}
              download
            >
              Download
            </a>
          </div>
          <div className="stem-results-box">
            <p>Instrumental</p>
            <AudioPlayer
              url={`http://localhost:8000/download/${results.session_id}/no_vocals`}
            />
            <a
              className="stem-download-btn"
              href={`http://localhost:8000/download/${session_id}/no_vocals`}
              download
            >
              Download
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsDisplay;
