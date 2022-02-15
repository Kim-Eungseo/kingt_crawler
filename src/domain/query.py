from datetime import datetime
from pydantic import BaseModel


class SEQuery(BaseModel):
    page: int
    scDetail: str = "detail"
    scOrdBy: int = 0
    catView: str = "AL"
    scText: str
    scPeriod: str = "6m"
    scArea: str = "tc"
    scTextIn: str = ""
    scTextExt: str = ""
    scPeriodS: str = ""
    scPeriodE: str = ""
    command: str = ""
    _: int = int(datetime.now().timestamp())
