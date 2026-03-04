import { useRef, useState } from "react";

function FileUploader({ onResults, loading, setLoading, previousSessionId }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [separate, setSeparate] = useState(false);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;
    setSelectedFile(file);
    setError(null);
    onResults(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError(null);
    onResults(null); // clear previous results immediately

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("separate", separate);

      // Send previous session id back for cleanup if it already exists
      if (previousSessionId) {
        formData.append("previous_session_id", previousSessionId);
      }

      const response = await fetch("http://127.0.0.1:8000/process-audio", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
        onResults(null);
      } else {
        onResults(data);
      }
    } catch (err) {
      console.log("Error: ", err);
      setError("Failed to connect to the server.");
      onResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      {/* DROP ZONE */}
      <div
        className={`drop-zone ${loading ? "disabled" : ""}`}
        onClick={() => !loading && fileInputRef.current.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {selectedFile ? (
          <p>📄 {selectedFile.name}</p>
        ) : (
          <p>
            <span class="desktop-text">
              Drag & Drop or Click to Select a File ⬇
            </span>
            <span class="mobile-text">Select a File ⬇</span>
          </p>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,video/*"
          hidden
          onChange={(e) => {
            handleFileSelect(e.target.files[0]);
            e.target.value = null;
          }}
          disabled={loading}
        />
      </div>

      {/* TOGGLE */}
      <div className="toggle-group">
        <label className={`toggle-option ${separate ? "active" : ""}`}>
          <input
            type="radio"
            name="separate"
            checked={separate}
            onChange={() => setSeparate(true)}
            disabled={loading}
          />
          🎤 Separate vocals
        </label>

        <label className={`toggle-option ${!separate ? "active" : ""}`}>
          <input
            type="radio"
            name="separate"
            checked={!separate}
            onChange={() => setSeparate(false)}
            disabled={loading}
          />
          🚫 Don’t separate vocals
        </label>
      </div>

      {error && <p className="error-msg shake">{error}</p>}

      <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
        {loading ? "Processing…" : "Submit"}
      </button>
    </div>
  );
}

export default FileUploader;
