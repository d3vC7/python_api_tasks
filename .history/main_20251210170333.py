from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="Prueba Técnica",
    description="API REST CRUD",
    version="1.0.0"
)

# Include the router
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Task Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )