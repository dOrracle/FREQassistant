from fastapi import FastAPI
from dotenv import load_dotenv
from .api_route import router

load_dotenv()

app = FastAPI(title="FreqAssistant API")
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
