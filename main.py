from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/search/{keyword}")
def read_item(keyword: int, kw: Optional[str] = None):
    return {"keyword": keyword, "kw": kw}

