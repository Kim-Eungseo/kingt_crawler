from fastapi import FastAPI
from routers import seouleco, chosun

app = FastAPI()
app.include_router(seouleco.router)
app.include_router(chosun.router)


@app.get("/")
async def read_root():
    return {"crawler": "isWorking"}
