from pydantic import BaseModel


class IP2CCVersion(BaseModel):
    version: str


class IP2CCState(BaseModel):
    module: int
    port: int
    state: int


class IP2CCPortStates(BaseModel):
    port1: int
    port2: int
    port3: int


class IP2CCPortUpdate(BaseModel):
    device_id: int
    module: int = 1
    port: int
    state: int


class IP2CCPortDetail(BaseModel):
    name: str
    state: int


class IP2CCNetDetail(BaseModel):
    cfglock: str
    IPconfig: str
    IPaddr: str
    subnet: str
    gateway: str


class IP2CCClosures(BaseModel):
    port1: IP2CCPortDetail
    port2: IP2CCPortDetail
    port3: IP2CCPortDetail


class IP2CCDataModel(BaseModel):
    id: int
    name: str
    host: str
    version: str | None = None
    contact_closure: IP2CCClosures
    eth: IP2CCNetDetail | None = None
