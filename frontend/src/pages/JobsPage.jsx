import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getJobs, getJobSources } from "../api/client";

function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [sources, setSources] = useState({ primary_sources: [], other_sources: [] });
  const [selectedSource, setSelectedSource] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);

  useEffect(() => {
    getJobSources()
      .then(setSources)
      .catch(() => setError("Could not load sources."));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setPage(1);
    getJobs(selectedSource || undefined, 1)
      .then((data) => {
        setJobs(data.jobs);
        setTotal(data.total);
      })
      .catch(() => setError("Could not load jobs. Is the backend running?"))
      .finally(() => setLoading(false));
  }, [selectedSource]);

  const loadMoreJobs = () => {
    if (loadingMore || jobs.length >= total) return;

    const nextPage = page + 1;
    setLoadingMore(true);
    setError(null);
    getJobs(selectedSource || undefined, nextPage)
      .then((data) => {
        setJobs((currentJobs) => [...currentJobs, ...data.jobs]);
        setPage(nextPage);
        setTotal(data.total);
      })
      .catch(() => setError("Could not load more jobs."))
      .finally(() => setLoadingMore(false));
  };

  const filteredJobs = jobs.filter((job) => {
    const text = [job.title, job.company, job.location, job.role_category, ...(job.tags || [])].join(" ").toLowerCase();
    return text.includes(search.trim().toLowerCase());
  });

  return (
    <main className="jobs-page modern-jobs-page">
      <section className="jobs-hero">
        <div>
          <p className="eyebrow">YOUR NEXT CHAPTER STARTS HERE</p>
          <h1>Find work that feels<br /><em>like a great fit.</em></h1>
          <p className="hero-description">Discover opportunities from the platforms you trust, all in one focused place.</p>
          <div className="hero-stats"><span><strong>{total.toLocaleString()}</strong> open roles</span><span><strong>{sources.primary_sources.length + sources.other_sources.length || "—"}</strong> sources</span></div>
        </div>
        <div className="hero-badge" aria-hidden="true"><span>YOUR</span><b>next</b><span>MOVE</span><i>✦</i></div>
      </section>

      <section className="job-explorer">
        <div className="search-panel">
          <label className="search-box" htmlFor="job-search"><span>⌕</span><input id="job-search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search roles, skills, companies, or locations" />{search && <button type="button" onClick={() => setSearch("")}>×</button>}</label>
          <div className="source-filter">
            <button type="button" className={!selectedSource ? "filter-chip active" : "filter-chip"} onClick={() => setSelectedSource("")}>All roles</button>
            {sources.primary_sources.map((source) => <button type="button" key={source} className={selectedSource === source ? "filter-chip active" : "filter-chip"} onClick={() => setSelectedSource(source)}>{source}</button>)}
          </div>
        </div>

        <div className="results-bar"><div><h2>Explore opportunities</h2><p>{loading ? "Finding the newest roles…" : `${filteredJobs.length}${search ? " matching" : ""} roles loaded`}</p></div><span>{total.toLocaleString()} total jobs</span></div>
        {error && <div className="feedback-card error"><strong>Something went wrong.</strong>{error}</div>}
        {loading && <div className="job-grid loading-grid">{[1, 2, 3, 4, 5, 6].map((n) => <div className="job-skeleton" key={n}><span /><span /><span /><span /></div>)}</div>}
        {!loading && !error && filteredJobs.length > 0 && <div className="job-grid">{filteredJobs.map((job) => <Link to={`/jobs/${job.id}`} key={job.id} className="job-card-link"><article className="modern-job-card"><div className="job-top"><span>{job.source || "Verified"}</span><small>Open ↗</small></div><h3>{job.title}</h3><p className="company">{job.company || "Confidential company"}</p><div className="job-meta"><span>⌖ {job.location || "Flexible"}</span>{job.experience_required && <span>◷ {job.experience_required}</span>}</div><div className="job-footer"><div className="skill-list">{(job.tags || []).slice(0, 3).map((tag) => <b key={tag}>{tag}</b>)}</div><strong>View role →</strong></div></article></Link>)}</div>}
        {!loading && !error && jobs.length < total && <button type="button" className="load-more-button" onClick={loadMoreJobs} disabled={loadingMore}>{loadingMore ? "Loading more roles..." : `Load more roles (${jobs.length} of ${total})`}</button>}
        {!loading && !error && filteredJobs.length === 0 && <div className="empty-state"><span>⌕</span><h2>No matching roles</h2><p>Try another search or explore all available roles.</p><button type="button" onClick={() => { setSearch(""); setSelectedSource(""); }}>Show all roles</button></div>}
      </section>
    </main>
  );
}

export default JobsPage;
