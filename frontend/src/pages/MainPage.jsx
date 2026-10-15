import { useState } from "react";
import FileUploader from "../components/FileUploader";
import ResultsDisplay from "../components/ResultsDisplay";

function MainPage() {
  const [results, setResults] = useState(null);

  return (
    <div className="mainpage-body">
      <FileUploader onResults={setResults} />
      <ResultsDisplay results={results} />
    </div>
  );
}

export default MainPage;
