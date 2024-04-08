from contextlib import asynccontextmanager
import logging
from logger import syslog
import uvicorn
from pathlib import Path
from logger import syslog
from ip2cc import IP2CC, IP2CCState
from fastapi import FastAPI, HTTPException
from config import device_settings, database_path, settings, log_path
from database import create_connection


app = FastAPI(root_path="/api/v1")
cfg = device_settings()
ip2c3 = IP2CC(cfg["host"], cfg["port"])

# READING:
# https://github.com/tiangolo/fastapi/discussions/7457
# https://stackoverflow.com/questions/60715275/fastapi-logging-to-file
# - https://stackoverflow.com/a/67310566
# https://fastapi.tiangolo.com/advanced/events/

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up options here
    FORMAT = "{'timestamp':'%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}"
    logging.basicConfig(filename=log_path(), level=logging.INFO, format=FORMAT)
    
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    
    yield
    # any clean-up actions here

@app.get("/config")
def read_configuration():
    return cfg


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


if __name__ == "__main__":
    #FORMAT = "{'timestamp':'%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}"
    #logging.basicConfig(filename=log_path(), level=logging.INFO, format=FORMAT)
    if settings()["power_loss_restore"]:
        create_connection(database_path())
    config = uvicorn.Config(
        "main:app", port=settings()["web_api_server_port"], log_level="info",
    )
    server = uvicorn.Server(config)
    server.run()
