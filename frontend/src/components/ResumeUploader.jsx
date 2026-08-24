import { useState } from "react";
import { uploadResume } from "../api/client";

function ResumeUploader({ onResults }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const result = await uploadResume(file);
      onResults(result);
    } catch (err) {
      const detail = err.response?.data?.detail || "Upload failed. Please try again.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="resume-uploader modern-uploader">
      <label className="upload-dropzone" htmlFor="resume-file">
        <span className="upload-icon">↑</span>
        <strong>{file ? file.name : "Drop your resume here"}</strong>
        <span>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB ready to analyze` : "or click to browse your files"}</span>
        <small>PDF or DOCX · maximum 5 MB</small>
        <input id="resume-file" type="file" accept=".pdf,.docx" onChange={(e) => setFile(e.target.files[0])} />
      </label>
      <button type="submit" disabled={!file || loading}>{loading ? "Finding your matches..." : "Reveal my recommendations →"}</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}

export default ResumeUploader;
