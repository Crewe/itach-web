from pydantic import BaseModel


class IP2CCConfigPortDetail(BaseModel):
    name: str
    default_state: int


class IP2CCConfigClosures(BaseModel):
    port1: IP2CCConfigPortDetail
    port2: IP2CCConfigPortDetail
    port3: IP2CCConfigPortDetail


class IP2CCConfigDataModel(BaseModel):
    id: int
    name: str
    host: str
    contact_closure: IP2CCConfigClosures
