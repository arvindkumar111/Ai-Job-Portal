import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import JobsPage from "./pages/JobsPage";
import ResumePage from "./pages/ResumePage";
import JobDetailPage from "./pages/JobDetailPage";
import "./styles/index.css";

function App() {
  return (
    <BrowserRouter>
      <nav className="navbar">
        <div className="nav-links">
          <NavLink to="/" end>Explore jobs</NavLink>
          <NavLink to="/resume" className="resume-nav-link"><span>✦</span> Resume matches</NavLink>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<JobsPage />} />
        <Route path="/jobs/:id" element={<JobDetailPage />} />
        <Route path="/resume" element={<ResumePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
