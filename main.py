from ip2cc import IP2CC, IP2CCState
from fastapi import FastAPI, HTTPException
from config import loadcfg

app = FastAPI()
cfg = loadcfg()["devices"]["IP2CC"][0]
ip2c3 = IP2CC(cfg["host"], cfg["port"], "IP2CC")


@app.get("/")
def read_root():
    return loadcfg()


@app.get("/version")
def get_version():
    return {"version": ip2c3.get_version()[0]}


@app.get("/{module}/{port}/state")
def get_state(module: int, port: int):
    try:
        state = ip2c3.get_state(module, port)
        return state
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.post("/state")
def set_state(state: IP2CCState):
    try:
        s = ip2c3.set_state(state.module, state.port, state.state)
        return s
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/{module}/{port}/net")
def get_net(module: int, port: int):
    try:
        n = ip2c3.get_net(module, port)
        return n
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/devices")
def get_devices():
    try:
        devs = ip2c3.get_devices()
        return devs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
