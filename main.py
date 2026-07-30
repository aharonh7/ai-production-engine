import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import yaml
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# טעינת קונפיג
with open(BASE_DIR / "config" / "config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

# שמירת הקונפיג ב-registry
from src.core.registry import CONFIG as REG_CONFIG, provider_registry
REG_CONFIG.update(CONFIG)

# מודלים
from src.core.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = DATA_DIR / "ai_production.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# ספקים
from src.providers.openai_adapter import OpenAIAdapter
from src.providers.anthropic_adapter import AnthropicAdapter
from src.providers.gemini_adapter import GeminiAdapter
from src.providers.deepseek_adapter import DeepSeekAdapter

# רישום ספקים לפי מפתחות
if os.getenv("OPENAI_API_KEY"):
    provider_registry.register("openai", OpenAIAdapter(os.getenv("OPENAI_API_KEY")))
if os.getenv("ANTHROPIC_API_KEY"):
    provider_registry.register("anthropic", AnthropicAdapter(os.getenv("ANTHROPIC_API_KEY")))
if os.getenv("GEMINI_API_KEY"):
    provider_registry.register("google", GeminiAdapter(os.getenv("GEMINI_API_KEY")))
if os.getenv("DEEPSEEK_API_KEY"):
    provider_registry.register("deepseek", DeepSeekAdapter(os.getenv("DEEPSEEK_API_KEY"), budget_limit=CONFIG.get("default_budget", 2.0)))

app = FastAPI(title="AI Production Engine", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
from src.api.routes import router as api_router
app.include_router(api_router, prefix="/api")

# UI
ui_dir = BASE_DIR / "src" / "ui"
if ui_dir.exists():
    app.mount("/", StaticFiles(directory=str(ui_dir), html=True), name="ui")

@app.get("/health")
async def health():
    return {"status": "healthy", "providers": provider_registry.list_providers()}

@app.get("/budget")
async def get_budget():
    adapter = provider_registry.get("deepseek")
    if adapter:
        return adapter.get_status()
    return {"error": "DeepSeek not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)