from fastapi import FastAPI
from routers import seouleco, chosun, donga, dart, stock_price

app = FastAPI()
app.include_router(seouleco.router)
app.include_router(chosun.router)
app.include_router(donga.router)
app.include_router(dart.router)
app.include_router(stock_price.router)

@app.get("/")
async def read_root():
    return {"crawler": "isWorking"}
