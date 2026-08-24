from collections import defaultdict, deque
import time

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import jobs, resume, chat




app = FastAPI(title="AI-Powered Job Board")
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

request_times = defaultdict(deque)
RATE_LIMITED_PATHS = {"/api/chat", "/api/resume/upload"}
MAX_REQUESTS_PER_MINUTE = 30


@app.middleware("http")
async def protect_api(request: Request, call_next):
    if request.method == "POST" and request.url.path in RATE_LIMITED_PATHS:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        recent_requests = request_times[(client_ip, request.url.path)]
        while recent_requests and now - recent_requests[0] > 60:
            recent_requests.popleft()
        if len(recent_requests) >= MAX_REQUESTS_PER_MINUTE:
            return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})
        recent_requests.append(now)

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path not in {"/docs", "/redoc"}:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


@app.get("/")
def health_check():
    return {"status": "ok"}

