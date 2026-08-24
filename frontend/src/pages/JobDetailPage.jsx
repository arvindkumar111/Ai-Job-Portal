import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { getJobById } from "../api/client";
import ChatWidget from "../components/ChatWidget";

function JobDetailPage() {
  const { id } = useParams();
  const location = useLocation();
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getJobById(id)
      .then(setJob)
      .catch((err) => setError(err.response?.data?.detail || "Could not load this job."));
  }, [id]);

  if (error) return <div className="job-detail-page"><Link to="/">Back to jobs</Link><p className="error">{error}</p></div>;
  if (!job) return <div className="job-detail-page"><p>Loading job...</p></div>;

  return (
    <div className="job-detail-page">
      <div className="job-detail-actions">
        <Link to="/" className="back-button">← <span>Back to jobs</span></Link>
        {location.state?.from === "resume" && <Link to="/resume" state={{ results: location.state.results }} className="back-button resume-back-button">✦ <span>Back to resume matches</span></Link>}
      </div>
      <h1>{job.title}</h1>
      <p className="company">{job.company} — {job.location}</p>
      <p className="source-tag">{job.source}</p>
      {job.experience_required && <p>Experience: {job.experience_required}</p>}
      {job.tags?.length > 0 && <div className="tags">{job.tags.map((tag) => <span key={tag} className="tag">{tag}</span>)}</div>}
      <h2>Description</h2>
      <p className="description">{job.description}</p>
      <ChatWidget jobId={job.id} />
    </div>
  );
}

export default JobDetailPage;
