from fastapi import FastAPI
from routers import seouleco, chosun, donga

app = FastAPI()
app.include_router(seouleco.router)
app.include_router(chosun.router)
app.include_router(donga.router)


@app.get("/")
async def read_root():
    return {"crawler": "isWorking"}
