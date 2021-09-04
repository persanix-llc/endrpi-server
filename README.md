![Endrpi logo](https://assets.persanix.com/endrpi/logo-padded/logo-padded.svg)

[![power on test](https://github.com/persanix-llc/endrpi-server/actions/workflows/power-on-test.yml/badge.svg)](https://github.com/persanix-llc/endrpi-server/actions/workflows/power-on-test.yml)
[![unit tests](https://github.com/persanix-llc/endrpi-server/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/persanix-llc/endrpi-server/actions/workflows/unit-tests.yml)
[![coverage](https://github.com/persanix-llc/endrpi-server/actions/workflows/coverage.yml/badge.svg)](https://github.com/persanix-llc/endrpi-server/actions/workflows/coverage.yml)
[![CodeQL](https://github.com/persanix-llc/endrpi-server/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/persanix-llc/endrpi-server/actions/workflows/codeql-analysis.yml)

Endpoints for Raspberry Pi (Endrpi) is a web API server for the [Raspberry Pi](https://raspberrypi.org)
that provides basic statuses and GPIO controls through a collection of HTTP endpoints.

Powered by [Fast API](https://github.com/tiangolo/fastapi), 
[GPIO Zero](https://github.com/gpiozero/gpiozero), 
and [others](requirements.txt).

## Features

#### REST API
* Reads system statuses such as temperature, memory usage, throttling, etc.
* Reads/updates GPIO pin state, function, and pull 
* Generates interactive documentation via [Swagger UI](https://swagger.io/tools/swagger-ui)

#### Websocket
* Maintains a persistent, low-latency connection
* Mirrors the REST API through a request/response action pattern

## Requirements

≥ Python 3.7

≥ Raspberry Pi 3
* Compatible with the standard [Raspberry Pi OS](https://www.raspberrypi.org/documentation/raspbian) image
* Previous Raspberry Pi versions may work but have not been verified

## Quickstart

##### 1. Clone project
```
git clone https://github.com/persanix-llc/endrpi-server.git && cd endrpi-server
```

##### 2. Install dependencies
```
pip3 install -r requirements.txt
```

##### 3. Start server
```
python3 endr.py
```

## Project documentation
Project documentation is hosted at [https://endrpi.io](https://endrpi.io).

The project documentation source can be found at 
[https://github.com/persanix-llc/endrpi-docs](https://github.com/persanix-llc/endrpi-docs).

## License

Licensed under the Apache License, Version 2.0.

Copyright &copy; 2020 - 2021 Persanix LLC. All rights reserved.