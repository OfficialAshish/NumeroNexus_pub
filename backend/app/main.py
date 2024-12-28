from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware

from .routes import router as api_router
from .a_routes import router as auth_router  
from .db_routes import router as db_router
# from .f_routes import router as social_router # for social relations
from .filter_routes import router as filter_router

from .database import init_db, engine , get_redis_client
from .limiter import limiter  # Import the limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()   
    yield
    # Any cleanup can be added here if needed

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(filter_router, prefix="/api", tags=["Filter"])
app.include_router(db_router, prefix="/api", tags=["DB"])
app.include_router(auth_router, prefix="/api/auth", tags=["AUTH-USERS"])
# app.include_router(social_router, prefix="/api/auth", tags=["Social"])


# # Serve React static files

# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# app.mount("/static", StaticFiles(directory="static"), name="static")
# # Serve the React app
# @app.get("/{full_path:path}")
# async def serve_react(full_path: str):
#     return FileResponse("static/index.html")
# @app.get("/")
# def read_root():
#     return FileResponse("static/index.html")


# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    # "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)



# Middleware setup
app.add_middleware(GZipMiddleware, minimum_size=400)  # Compress responses  
app.add_middleware(SlowAPIMiddleware)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
