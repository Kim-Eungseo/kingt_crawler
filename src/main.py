from fastapi import FastAPI
from routers import seouleco

app = FastAPI()
app.include_router(seouleco.router)


@app.get("/")
async def read_root():
    return {"crawler": "isWorking"}
