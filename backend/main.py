# main.py
from fastapi import FastAPI
from chat import router as chat_router
from dispute import router as dispute_router

app = FastAPI()

app.include_router(chat_router, prefix="/chat")
app.include_router(dispute_router, prefix="/dispute")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
