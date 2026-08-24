import { useState } from "react";
import ResumeUploader from "../components/ResumeUploader";
import { Link, useLocation } from "react-router-dom";
import ChatWidget from "../components/ChatWidget";

function ResumePage() {
  const location = useLocation();
  const [results, setResults] = useState(() => location.state?.results || null);

  return (
    <div className="resume-page modern-resume-page">
      <section className="resume-hero">
        <p className="eyebrow">PERSONALIZED JOB DISCOVERY</p>
        <h1>Let your experience<br /><em>lead the way.</em></h1>
        <p>Upload your resume and receive role recommendations shaped around the skills you already have.</p>
      </section>
      <section className="resume-workspace">
        <div className="resume-intro"><span>01</span><div><h2>Upload your resume</h2><p>We identify your strengths and compare them with active opportunities.</p></div></div>
      <ResumeUploader onResults={setResults} />
        <p className="privacy-note">⌁ Your resume is used only to create your recommendations.</p>
      </section>

      {results && (
        <div className="results recommendation-results">
          <div className="results-title"><div><p className="eyebrow">YOUR PROFILE SNAPSHOT</p><h2>Roles picked for you.</h2></div><span>{results.recommendations.length} recommendations</span></div>
          <div className="skill-panel"><div><p>RECOGNIZED SKILLS</p><h3>Your strongest signals</h3></div>
          <div className="tags">
            {results.extracted_skills.length > 0 ? (
              results.extracted_skills.map((skill) => (
                <span key={skill} className="tag">{skill}</span>
              ))
            ) : (
              <p>No recognized skills found in this resume.</p>
            )}
          </div>
          </div>

          <h2 className="recommendation-label">Recommended for you</h2>
          <div className="job-list recommendation-grid">
            {results.recommendations.map((job) => (
              <Link to={`/jobs/${job.id}`} state={{ from: "resume", results }} key={job.id} className="recommendation-card-link" aria-label={`View ${job.title} at ${job.company}`}>
                <div className="job-card recommendation-card">
                <h3>{job.title}</h3>
                <p className="company">{job.company} — {job.location}</p>
                <p className="source-tag">{job.source}</p>
                <p className="similarity">
                  Match score: {(job.similarity_score * 100).toFixed(0)}%
                </p>
                {job.matched_skills.length > 0 && (
                  <p className="matched">
                    Matched skills: {job.matched_skills.join(", ")}
                  </p>
                )}
                </div>
              </Link>
            ))}
          </div>
          <ChatWidget resumeText={results.resume_text} title="Ask your career assistant" />
        </div>
      )}
    </div>
  );
}

export default ResumePage;
