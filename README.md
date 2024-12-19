# A Web API for Global Caché's iTach IP2CC

I needed a Web front-end to an industrial ethernet relay contact closure device. So now, this.

## Add the devices to your network

First you will need to add the devices to your network and take down their details,
notably their IP addresses. Update your configuration file with the details.

## Setup and Configuration

Now to edit your `config.yml`. This outlines the devices on your network, and how
each port is configured.

```yml
devices:
  IP2CC:
    - id: 0
      name: "IP2CC Device Identifier"
      host: 192.168.1.70 # Default IP for no DHCP
      contact_closure:
        port1: 
          name: "Device One" # What will be displayed on UI for control panel
          default_state : 0   # After power loss what should be the port state (default: 0)
        port2: 
          name: "Device Two"
          default_state: 0
        port3: 
          name: "Device Three"
          default_state : 0

settings:
  server_port: 8000

database:
  path: itach.db

logging:
  path: itach.log
```

Add your device to the `IP2CC`. (Currently only one device is supported). Next update the paths
to where you want the database and logs to be stored. Because the devices reset to their disconnected
state after a power loss event, this will allow you to have the ports restore to their pre-power-loss
status, assuming it didn't occur duing a port state change.

## Ready to go!

Fire up the app with `python3 -m itachweb`, or using docker with `docker compose up -d`, and access the UI from `http://localhost:8000/ip2cc`.
