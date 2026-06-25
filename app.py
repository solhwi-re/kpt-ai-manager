from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.notion import get_kpt_items, reset_kpt_board

app = FastAPI(
    title="KPT AI Manager API",
    version="1.0.0",
    description="Reads KPT items from a Notion data source for My GPT Actions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "KPT AI Manager",
        "status": "running",
        "endpoints": [
            "/health",
            "/kpt/items",
            "/kpt/reset",
        ],
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/kpt/items")
def kpt_items():
    """Return KPT rows grouped by Keep / Problem / Try."""
    return get_kpt_items()


# 브라우저에서 직접 호출할 때
@app.get("/kpt/reset")
def kpt_reset():
    return reset_kpt_board()


# 노션 웹훅에서 호출할 때
@app.post("/kpt/reset")
def kpt_reset_post():
    return reset_kpt_board()
