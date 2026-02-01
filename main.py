from fastapi import FastAPI
from src.data.database import close_mongo,connect_to_mongo
from contextlib import asynccontextmanager
from src.auth.routes.auth import router as auth_router
import uvicorn


@asynccontextmanager
async def lifespan(app:FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo()

app=FastAPI(lifespan=lifespan)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__=="__main__":
    uvicorn.run("main:app",reload=True,port=5000)


