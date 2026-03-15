from fastapi import FastAPI

from app.api.v1.prices import router as prices_router

app = FastAPI(title="Crypto2 API")
app.include_router(prices_router)
