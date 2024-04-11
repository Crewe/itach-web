import logging
from typing import List
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .app import app

# from .routers.api import v1_api_router
from .datamodels.ip2cc import IP2CCDataModel, IP2CCNetDetail
from .datamodels.config import IP2CCConfigDataModel
from .itach.ip2cc import IP2CC
from .logger import syslog
from .datamodels.ip2cc import (
    IP2CCPortStates,
    IP2CCState,
    IP2CCPortUpdate,
    IP2CCVersion,
)
from .config import device_settings, database_path, settings, log_path
from .database import create_connection


BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str("itachweb/templates"))

cfg = device_settings()
ip2c3 = [IP2CC(host=ip, port=4998) for key, ip in cfg[0].items() if key == "host"]


@app.get("/ip2cc", response_class=HTMLResponse)
async def dashboard(request: Request):

    dvm = []
    for i in range(len(cfg)):
        port = get_port_states(device_id=i)
        device = IP2CCConfigDataModel(**cfg[i])
        dvm.append(
            {
                "id": device.id,
                "name": device.name,
                "host": device.host,
                "ports": {
                    device.contact_closure.port1.name: port["port1"],
                    device.contact_closure.port2.name: port["port2"],
                    device.contact_closure.port3.name: port["port3"],
                },
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_title": "Dashboard", "devices": dvm},
    )


@app.get("/ip2cc/{device_id}/details", response_class=HTMLResponse)
async def device_detail(request: Request, device_id: int):

    dvm = []
    port = get_port_states(device_id=device_id)
    device = IP2CCConfigDataModel(**cfg[device_id])
    dvm.append(
        {
            "id": device.id,
            "name": device.name,
            "host": device.host,
            "version": get_version(device_id=device_id).version,
            "ports": {
                device.contact_closure.port1.name: port["port1"],
                device.contact_closure.port2.name: port["port2"],
                device.contact_closure.port3.name: port["port3"],
            },
            "eth": get_net(0, 1, device_id),
        }
    )
    del dvm[0]["eth"]["module"]
    del dvm[0]["eth"]["port"]

    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={"page_title": dvm[0]["name"], "device": dvm[0]},
    )


@app.get("/config")
def read_configuration() -> IP2CCConfigDataModel:
    syslog().info("HTTP GET config requested.")
    return IP2CCConfigDataModel(**cfg[0])


@app.get("/version")
def get_version(device_id: int) -> IP2CCVersion:
    syslog().info("HTTP GET version requested.")
    return ip2c3[device_id].get_version()


@app.get("/{module}/{port}/state")
def get_state(module: int, port: int, device_id: int) -> IP2CCState:
    syslog().info("HTTP GET state requested.")
    try:
        state = ip2c3[device_id].get_state(module, port)
        return state
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/ip2cc/portstates")
def get_port_states(device_id: int) -> IP2CCPortStates:
    syslog().info("HTTP GET state requested.")
    try:
        states = ip2c3[device_id].get_all_port_states()
        return states
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.post("/state")
def set_state(state: IP2CCPortUpdate) -> IP2CCState:
    syslog().info("HTTP POST state requested.")
    try:
        s = ip2c3[state.device_id].set_state(state.module, state.port, state.state)
        return s
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/{module}/{port}/net")
def get_net(module: int, port: int, device_id: int) -> IP2CCNetDetail:
    syslog().info("HTTP GET get_NET requested.")
    try:
        n = ip2c3[device_id].get_net(module, port)
        return n
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/modules")
def get_modules(device_id: int):
    syslog().info("HTTP GET device modules requested.")
    try:
        devs = ip2c3[device_id].get_modules()
        return devs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


def main():
    FORMAT = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    logging.basicConfig(filename=log_path(), level=logging.INFO, format=FORMAT)
    config = uvicorn.Config(
        "itachweb.itachweb:app",
        port=settings()["server_port"],
        log_level="info",
    )
    server = uvicorn.Server(config)
    server.run()
