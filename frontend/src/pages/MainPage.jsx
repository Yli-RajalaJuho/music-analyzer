import { useState } from "react";
import FileUploader from "../components/FileUploader";
import ResultsDisplay from "../components/ResultsDisplay";

function MainPage() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="mainpage-body">
      <FileUploader
        onResults={setResults}
        loading={loading}
        setLoading={setLoading}
        previousSessionId={results?.session_id}
      />

      <ResultsDisplay results={results} loading={loading} />
    </div>
  );
}

export default MainPage;
