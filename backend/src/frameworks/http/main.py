
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.frameworks.http.routers import pricing, items, construction

app = FastAPI(title="Alubrasa PGI API", version="1.0.0")

# CORS (Allow Frontend)
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(pricing.router)
app.include_router(items.router)
app.include_router(construction.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
