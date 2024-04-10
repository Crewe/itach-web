import re
from typing import List
from pydantic import BaseModel, ValidationInfo, field_validator
from dataclasses import dataclass, replace
from ..logger import syslog
from .itach import ItachClient
from ..error import check_response


@dataclass
class IP2CCState(BaseModel):
    module: int
    port: int
    state: int


@dataclass
class IP2CCPortStates(BaseModel):
    port1: int
    port2: int
    port3: int


@dataclass
class IP2CCPortUpdate(BaseModel):
    device_id: int
    module: int = 1
    port: int
    state: int

    # @field_validator('device_id', 'module', 'port', 'state')
    # @classmethod
    # def validate_atts(cls, v: int, info: ValidationInfo):
    #    if info.field_name == 'device_id':
    #        if v < 0: raise ValueError(f'{v} is not a valid device id.')
    #    elif info.field_name == 'module':
    #        if v != 1: raise ValueError(f'{v} is not a valid module.')
    #    elif info.field_name == 'port':
    #         if not v in range(1,4): raise ValueError(f'{v} is not a valid port number.')
    #    elif info.field_name == 'state':
    #        if not v in range(2): raise ValueError(f'{v} is not a valid state.')
    #    return v


@dataclass
class IP2CCPortDetail(BaseModel):
    name: str
    state: int


@dataclass
class IP2CCClosures(BaseModel):
    port1: IP2CCPortDetail
    port2: IP2CCPortDetail
    port3: IP2CCPortDetail


@dataclass
class IP2CCDataModel(BaseModel):
    id: int
    name: str
    host: str
    contact_closure: IP2CCClosures


class IP2CC(ItachClient):
    def __init__(self, host, port=4998, client_type="IP2CC"):
        super().__init__(host, port, client_type)

    def send(self, cmd):
        self.client.send(f"{cmd}\r".encode("utf-8"))
        r = []

        # check the response based on the command
        command = cmd.split(",")[0].strip("\r")
        while True:
            try:
                resp = self.client.recv(1024)
                resp = resp.decode("utf-8")

                # Check for the only command that returns multiple lines for the IP2CC
                if command != "getdevices":
                    if re.fullmatch(r".+\r", resp) is not None:
                        r.append(resp.strip("\r"))
                        break
                else:
                    if re.fullmatch(r".+endlistdevices\r", resp) is not None:
                        r = resp.split("\r")
                        r = r[:2]
                        break

            except Exception as e:
                syslog().error(
                    f"An error occurred sending a command to the device at '{self.svr_host}'"
                )

        # Throw out the used socket it's trash.
        self.client.close()
        self.client = None
        return r

    def get_version(self):
        try:
            self.connect()
            return self.send("getversion\r")
        except Exception as e:
            syslog().error(
                f"Unable to get device version for device at '{self.svr_host}'"
            )
            raise Exception("An error has occurred.")

    def get_all_port_states(self):
        states = {}
        for i in range(1, 4):
            port = f"port{i}"
            states[port] = int(self.get_state(1, i)["state"])
        return states

    def get_state(self, module, port):
        try:
            self.connect()
            resp = self.send(f"getstate,{module}:{port}\r")[0]
            err = check_response(resp)
            if err is not None:
                raise ValueError(err[1])

            return self._serialize(resp)

        except ValueError as ve:
            syslog().error(
                f"Incorrect value used retrieving state for device at '{self.svr_host}'",
                extra={"details": err[1]},
            )
            raise ve
        except Exception as e:
            syslog().error(
                f"Exception occurred retrieving state for device at '{self.svr_host}'"
            )
            raise e

    def set_state(self, module, port, state):
        try:
            self.connect()
            # TCP API appears to be broken. Works for any Module Number 0|...|5
            resp = self.send(f"setstate,{module}:{port},{state}\r")[0]
            err = check_response(resp)
            if err is not None:
                raise ValueError(err[1])

            return self._serialize(resp)

        except ValueError as ve:
            syslog().error(
                f"Incorrect value used setting state for device at '{self.svr_host}'",
                extra={"details": err[1]},
            )
            raise ve
        except Exception as e:
            syslog().error(
                f"Exception occurred setting state for device at '{self.svr_host}'"
            )
            raise e

    def get_net(self, module, port):
        try:
            self.connect()
            resp = self.send(f"get_NET,{module}:{port}\r")[0]
            err = check_response(resp)
            if err is not None:
                raise ValueError(err[1])

            return self._serialize(resp)

        except ValueError as ve:
            syslog().error(
                f"Incorrect value used getting NET for device at '{self.svr_host}'",
                extra={"details": err[1]},
            )
            raise ve
        except Exception as e:
            syslog().error(
                f"An exception occurred getting NET for device at '{self.svr_host}'"
            )
            raise e

    def get_modules(self):
        try:
            self.connect()
            resp = self.send(f"getdevices\r")
            err = check_response(resp)
            if err is not None:
                syslog().error(
                    f"Incorrect value used getting devices at '{self.svr_host}'",
                    extra={"details": err[1]},
                )
                raise ValueError(err[1])

            return self._serialize(resp)

        except Exception as e:
            syslog().error(
                f"An exception occurred getting devices at '{self.svr_host}'"
            )
            raise e

    def _serialize(self, response: str) -> object:
        r = {}
        resp = None
        if type(response) is not list:
            resp = response.split(",")

        if type(response) is not str:
            # device,<module>,<ports>␣<type>\r…\rendlistdevices\r
            r["devices"] = []
            for dvc_lst in response:
                details = dvc_lst.split(",")
                p_type = details[2].split(" ")
                r["devices"].append(
                    {"module": details[1], "ports": p_type[0], "type": p_type[1]}
                )

        elif resp[0] == "NET":
            # NET,<module>:<port>,<cfglock>,<IPconfig>,<IPaddr>,<subnet>,<gateway>
            mod_port = resp[1].split(":")
            r["module"] = mod_port[0]
            r["port"] = mod_port[1]
            r["cfglock"] = resp[2]
            r["IPconfig"] = resp[3]
            r["IPaddr"] = resp[4]
            r["subnet"] = resp[5]
            r["gateway"] = resp[6]

        else:
            # (get|set)state,<module>:<port>,<state>
            mod_port = resp[1].split(":")
            s = {"module": mod_port[0], "port": mod_port[1], "state": resp[2]}
            return s

        return r
