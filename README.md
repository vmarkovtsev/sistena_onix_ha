# Sistena Onix Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![Made with Poolside][poolside-shield]][poolside]

## Overview

This integration allows you to connect your Sistena Onix devices to Home Assistant. It provides support for climate control devices and sensors.

## Installation

### HACS Installation (Recommended)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=vmarkovtsev&repository=sistena_onix_ha&category=integration" target="_blank"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store." /></a>

1. Ensure that [HACS](https://hacs.xyz/) is installed on your Home Assistant instance.
2. Open HACS in your Home Assistant frontend.
3. Go to the **Integrations** tab.
4. Click the **Explore & Add Repositories** button at the bottom.
5. Search for "Sistena Onix" and click on the integration.
6. Click **Install** to install the integration.
7. Restart Home Assistant.
8. Go to **Configuration** > **Integrations** > **Add Integration** and search for "Sistena Onix".

### Manual Installation

1. Download the latest release from the [releases page][releases].
2. Extract the downloaded archive.
3. Copy the `sistena` directory to your Home Assistant's `custom_components` directory.
4. Restart Home Assistant.
5. Go to **Configuration** > **Integrations** > **Add Integration** and search for "Sistena Onix".

## Configuration

The integration will guide you through a configuration flow where you need to provide:

- **API Key**: Your Sistena Onix API key. Discover it by inspecting browser requests at [onix.sistena.app](https://onix.sistena.app/#/home): `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=<<<API Key>>>`
- **Email**: Your account email.
- **Password**: Your account password.

## Exposed entities per thermostat

- Climate control widget
- Temperature and humidity sensors

## Supported Devices

* [Giacomini K492AY423](https://es.giacomini.com/producto/K492A) flashed with "GC150_R02" ESP32 firmware from Sistena S.L. (Madrid, Spain).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[releases-shield]: https://img.shields.io/github/release/vmarkovtsev/sistena_onix_ha.svg
[releases]: https://github.com/vmarkovtsev/sistena_onix_ha/releases
[license-shield]: https://img.shields.io/github/license/vmarkovtsev/sistena_onix_ha.svg
[poolside-shield]: https://img.shields.io/badge/Made%20with-Poolside-blue
[poolside]: https://poolside.ai
