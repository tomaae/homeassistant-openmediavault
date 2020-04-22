# OpenMediaVault integration for Home Assistant
![GitHub release (latest by date)](https://img.shields.io/github/v/release/tomaae/homeassistant-openmediavault?style=plastic)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=plastic)](https://github.com/custom-components/hacs)
![Project Stage](https://img.shields.io/badge/project%20stage-development-yellow.svg?style=plastic)

![GitHub commits since latest release](https://img.shields.io/github/commits-since/tomaae/homeassistant-openmediavault/latest?style=plastic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/tomaae/homeassistant-openmediavault?style=plastic)

![OpenMediaVault Logo](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/header.png)

Monitor your OpenMediaVault NAS from Home Assistant.

Features:
* Filesystem usage sensors
* System sensors (CPU, Memory)

# Features
## Filesystem usage
Monitor you filesystem usage.

![Filesystem usage](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/filesystem_sensor.png)

## System
Monitor you OpenMediaVault system.

![System](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/system_sensors.png)

# Install integration
This integration is distributed using [HACS](https://hacs.xyz/).

You can find it under "Integrations", named "OpenMediaVault"

## Setup integration
Setup this integration for your OpenMediaVault NAS in Home Assistant via `Configuration -> Integrations -> Add -> OpenMediaVault`.
You can add this integration several times for different devices.

![Add Integration](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/setup_integration.png)
* "Name of the integration" - Friendly name for this NAS
* "Host" - Use hostname or IP

# Development
## Enabling debug
To enable debug for OpenMediaVault integration, add following to your configuration.yaml:
```
logger:
  default: info
  logs:
    custom_components.openmediavault: debug
```
