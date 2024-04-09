import re
from pydantic import BaseModel
from ..logger import syslog
from .itach import ItachClient
from ..error import check_response


class IP2CCState(BaseModel):
    module: int  # = 1
    port: int
    state: int


class IP2CCNet(BaseModel):
    module: int  # = 0
    port: int


class IP2CC(ItachClient):
    def __init__(self, host, port, client_type="IP2CC"):
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
                syslog().error(f"An error occurred sending a command to the device at \'{self.svr_host}\'")

        # Throw out the used socket it's trash.
        self.client.close()
        self.client = None
        return r

    def get_version(self):
        try:
            self.connect()
            return self.send("getversion\r")[0]
        except Exception as e:
            syslog().error(f"Unable to get device version for device at \'{self.svr_host}\'")
            raise Exception("An error has occurred.")

    def get_state(self, module, port):
        try:
            self.connect()
            resp = self.send(f"getstate,{module}:{port}\r")[0]
            err = check_response(resp)
            if err is not None:
                raise ValueError(err[1])

            return self._serialize(resp)

        except ValueError as ve:
            syslog().error(f"Incorrect value used retrieving state for device at \'{self.svr_host}\'", extra=err[1])
            raise ve
        except Exception as e:
            syslog().error(f"Exception occurred retrieving state for device at \'{self.svr_host}\'")
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
            syslog().error(f"Incorrect value used setting state for device at \'{self.svr_host}\'", extra=err[1])
            raise ve
        except Exception as e:
            syslog().error(f"Exception occurred setting state for device at \'{self.svr_host}\'")
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
            syslog().error(f"Incorrect value used getting NET for device at \'{self.svr_host}\'", extra=err[1])
            raise ve
        except Exception as e:
            syslog().error(f"An exception occurred getting NET for device at \'{self.svr_host}\'")
            raise e

    def get_devices(self):
        try:
            self.connect()
            resp = self.send(f"getdevices\r")
            err = check_response(resp)
            if err is not None:
                syslog().error(f"Incorrect value used getting devices at \'{self.svr_host}\'", extra=err[1])
                raise ValueError(err[1])

            return self._serialize(resp)

        except Exception as e:
            syslog().error(f"An exception occurred getting devices at \'{self.svr_host}\'")
            raise e

    def _serialize(self, response: str) -> str:
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
            r["module"] = mod_port[0]
            r["port"] = mod_port[1]
            r["state"] = resp[2]

        return r
