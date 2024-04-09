# A Web API for Global Caché's iTach IP2CC

I needed a Web front-end to an industrial ethernet relay contact closure device. So now, this.

## Setup and Configuration

You will first need to edit your `config.yaml`. This outlines the devices on your network, and how
each port is configured.

```yml
devices:
  IP2CC:
    - id: 0
      name: "IP2CC Device Identifier"
      host: 192.168.1.70 # Default IP for no DHCP
      port: 4998         # Default TCP Port
      contact_closure:
        - 0: "Device One" # What will be displayed on UI for control
          1: "Device Two"
          2: "Device Three"

settings:
  web_api_server_port: 8000
  power_loss_restore: false # Currently not implemented

database:
  path: itach.db

logging:
  path: itach.log
```

Add your device to the `IP2CC`. (Currently only one device is supported). Next update the paths
to where you want the database and logs to be stored. Because the devices reset to their disconnected
state after a power loss event, this will allow you to have the ports restore to their pre-power-loss
status, assuming it didn't occur duing a port state change.

## Create the database if needed

If you wish to use the `power_loss_restore` you will first need to create the database by runing `runfirst.py`
this will initialize the database with your currrent devices and port descriptions. If you need to update your
settings or device names simply delete the database file, and run `runfirst.py` again. You will obviously lose
your power loss settings. Though I may remedy this is the future with an API call to pull the settings from
the device list using an API call.

## Ready to go!

Fire up the app with `python -m itachweb`.
