/* import { useState } from "react";

function FileUploader({ onResults }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [separate, setSeparate] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setError(null);
    onResults(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("separate", separate);

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
      setError("Failed to connect to the server. Please try again.");
      onResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <label className="custom-file-upload">
        Select File
        <input
          type="file"
          accept="audio/*,video/*"
          onChange={(e) => {
            handleFileChange(e);
            e.target.value = null; // <-- Allow reuploading same file
          }}
        />
      </label>
      <div className="toggle-group">
        <label className={`toggle-option ${separate ? "active" : ""}`}>
          <input
            type="radio"
            name="separate"
            checked={separate === true}
            onChange={() => setSeparate(true)}
          />
          🎤 Separate vocals
        </label>

        <label className={`toggle-option ${!separate ? "active" : ""}`}>
          <input
            type="radio"
            name="separate"
            checked={separate === false}
            onChange={() => setSeparate(false)}
          />
          🚫 Don’t separate vocals
        </label>
      </div>

      {loading && <div className="loader"></div>}
      {error && <p className="error-msg">{error}</p>}
    </div>
  );
}

export default FileUploader;
*/

import { useRef, useState } from "react";

function FileUploader({ onResults }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [separate, setSeparate] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  // --- File selection ---
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

  // --- Submit ---
  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("separate", separate);

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
        className="drop-zone"
        onClick={() => fileInputRef.current.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {selectedFile ? (
          <p>📄 {selectedFile.name}</p>
        ) : (
          <p>⬇ Drag & drop or click to select a file ⬇</p>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,video/*"
          hidden
          onChange={(e) => {
            handleFileSelect(e.target.files[0]);
            e.target.value = null; // allow same file again
          }}
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
          />
          🎤 Separate vocals
        </label>

        <label className={`toggle-option ${!separate ? "active" : ""}`}>
          <input
            type="radio"
            name="separate"
            checked={!separate}
            onChange={() => setSeparate(false)}
          />
          🚫 Don’t separate vocals
        </label>
      </div>

      {error && <p className="error-msg">{error}</p>}

      <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
        {loading ? "Processing…" : "Submit"}
      </button>

      {loading && <div className="loader"></div>}
    </div>
  );
}

export default FileUploader;
