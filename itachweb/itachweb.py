import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .logger import syslog
from .itach.ip2cc import IP2CC, IP2CCState
from .config import device_settings, database_path, settings, log_path
from .database import create_connection


BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str("itachweb/templates"))

cfg = device_settings()
ip2c3 = IP2CC(cfg["host"], cfg["port"])


app = FastAPI(title="iTachWeb API", root_path="/api/v1")
app.mount("/static", StaticFiles(directory="itachweb/static"), name="static")


@app.get("/")
async def dashboard(request: Request):
    cfg = {
    "devices": {
        "IP2CC": [
            {
                "id": 0,
                "name": "IP2CC Device Identifier",
                "host": "192.168.1.70",
                "port": 4998,
                "contact_closure": {
                    "0": "Device One",
                    "1": "Device Two",
                    "2": "Device Three"
                }
            }
        ]
    }
}
    return templates.TemplateResponse(
        request=request, name="index.html", 
        context={'devices': cfg['devices']['IP2CC']}
    )

@app.get("/config")
def read_configuration():
    syslog().info("HTTP GET get_NET requested.")
    return cfg


@app.get("/version")
def get_version():
    syslog().info("HTTP GET version requested.")
    return {"version": ip2c3.get_version()[0]}


@app.get("/{module}/{port}/state")
def get_state(module: int, port: int):
    syslog().info("HTTP GET state requested.")
    try:
        state = ip2c3.get_state(module, port)
        return state
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.post("/state")
def set_state(state: IP2CCState):
    syslog().info("HTTP POST state requested.")
    try:
        s = ip2c3.set_state(state.module, state.port, state.state)
        return s
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/{module}/{port}/net")
def get_net(module: int, port: int):
    syslog().info("HTTP GET get_NET requested.")
    try:
        n = ip2c3.get_net(module, port)
        return n
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/devices")
def get_devices():
    syslog().info("HTTP GET devices requested.")
    try:
        devs = ip2c3.get_devices()
        return devs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


def main():
    FORMAT = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    logging.basicConfig(filename=log_path(), level=logging.INFO, format=FORMAT)
    if settings()["power_loss_restore"]:
        create_connection(database_path())
    config = uvicorn.Config(
        "itachweb.itachweb:app",
        port=settings()["web_api_server_port"],
        log_level="info",
    )
    server = uvicorn.Server(config)
    server.run()
