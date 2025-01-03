from pathlib import Path
from fastapi import HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .app import app

from .datamodels.ip2cc import IP2CCNetDetail
from .datamodels.config import IP2CCConfigDataModel
from .itach.ip2cc import IP2CC
from .logger import syslog
from .datamodels.ip2cc import (
    IP2CCPortStates,
    IP2CCState,
    IP2CCVersion,
)
from .config import device_settings


BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str("itachweb/templates"))

cfg = device_settings()
ip2c3 = [IP2CC(host=ip, port=4998) for key, ip in cfg[0].items() if key == "host"]


@app.get("/")
async def landing():
    return RedirectResponse(url="/ip2cc", status_code=status.HTTP_302_FOUND)


@app.get("/ip2cc", response_class=HTMLResponse)
async def dashboard(request: Request):

    dvm = []
    for i in range(len(cfg)):
        try:
            port = get_port_states(deviceId=i)
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
        except HTTPException as e:
            pass

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_title": "Dashboard", "devices": dvm},
    )


@app.get("/ip2cc/details", response_class=HTMLResponse)
async def device_detail(request: Request, deviceId: int):

    dvm = []
    port = get_port_states(deviceId=deviceId)
    device = IP2CCConfigDataModel(**cfg[deviceId])
    dvm.append(
        {
            "id": device.id,
            "name": device.name,
            "host": device.host,
            "version": get_version(deviceId=deviceId).version,
            "ports": {
                device.contact_closure.port1.name: port["port1"],
                device.contact_closure.port2.name: port["port2"],
                device.contact_closure.port3.name: port["port3"],
            },
            "eth": get_net(0, 1, deviceId),
        }
    )
    del dvm[0]["eth"]["module"]
    del dvm[0]["eth"]["port"]

    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={"page_title": dvm[0]["name"], "device": dvm[0]},
    )


@app.get("/config", response_model=IP2CCConfigDataModel)
def read_configuration() -> IP2CCConfigDataModel:
    syslog().info("HTTP GET config requested.")
    return IP2CCConfigDataModel(**cfg[0])


@app.get("/version", response_model=IP2CCVersion)
def get_version(deviceId: int) -> IP2CCVersion:
    syslog().info("HTTP GET version requested.")
    return ip2c3[deviceId].get_version()


@app.get("/{module}/{port}/state", response_model=IP2CCState)
def get_state(module: int, port: int, deviceId: int) -> IP2CCState:
    syslog().info("HTTP GET state requested.")
    try:
        state = ip2c3[deviceId].get_state(module, port)
        return state
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/ip2cc/portstates", response_model=IP2CCPortStates)
def get_port_states(deviceId: int) -> IP2CCPortStates:
    syslog().info("HTTP GET state requested.")
    try:
        states = ip2c3[deviceId].get_all_port_states()
        return states
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.post("/state", response_model=IP2CCState)
async def set_state(request: Request) -> IP2CCState:
    syslog().info("HTTP POST state requested.")
    try:
        state = await request.json()
        s = ip2c3[state["deviceId"]].set_state(
            state["module"], state["port"], state["state"]
        )
        return s
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/{module}/{port}/net", response_model=IP2CCNetDetail)
def get_net(module: int, port: int, deviceId: int) -> IP2CCNetDetail:
    syslog().info("HTTP GET get_NET requested.")
    try:
        n = ip2c3[deviceId].get_net(module, port)
        return n
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@app.get("/modules")
def get_modules(deviceId: int):
    syslog().info("HTTP GET device modules requested.")
    try:
        devs = ip2c3[deviceId].get_modules()
        return devs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
