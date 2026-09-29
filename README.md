![CTEK Nanogrid Air](logo.png)

# CTEK-Nanogrid-Air
Home Assistant Custom Component for reading data from CTEK Nanogrid Air






**Disclaimer:** This is a third-party integration developed independently and is **not affiliated with CTEK**. Use at your own discretion.

## Features
This integration provides the following sensor data for your CTEK Nanogrid Air devices:
* Chargebox connection status and outlet states.
* Chargebox state, endpoint and TCP port, and WiFi signal strength.
* Power metrics such as active power, current, and voltage for all phases.
* Energy import/export statistics.
* Device serial number, firmware, and MAC address.
* Meter vendor, type and id.


## Installation

### Installation via HACS (Recommended)
1. Open Home Assistant and go to the **HACS** section in the sidebar.
2. Click on the **Custom repositories** tab (found under **Settings** in HACS).
3. In the **Custom repositories** section, click the **+** button in the bottom right corner.
4. Enter the following repository URL: [https://github.com/FreshJonte/CTEK-Nanogrid-Air](https://github.com/FreshJonte/CTEK-Nanogrid-Air)
5. Select **Integration** as the Type.
6. Click **Add**.
7. Go back to the **Integrations** tab in HACS and click the **+** button at the bottom right.
8. Search for **CTEK Nanogrid Air** and select it from the list.
9. Follow the on-screen instructions to install the integration.
10. Once installed, restart Home Assistant to apply the changes.

### Manual Installation
If you prefer to install the integration manually, follow these steps:

1. Download this repository as a ZIP file and extract it.
2. Copy the `ctek_nanogrid_air` folder to your Home Assistant `custom_components` directory:
- If the `custom_components` directory doesn’t exist, create it.
- The directory structure should be:  
  `custom_components/ctek_nanogrid_air/`
3. Restart Home Assistant to complete the installation and enable the integration.


### Configuration
1. In Home Assistant, go to **Settings** > **Devices & Services** > **Integrations**.
2. Click on **Add Integration** and search for `CTEK Nanogrid Air`.
3. Enter the following details:
- **Host**: The IP address of your CTEK device.
- **Port**: The API port (default: `80`).
- **Username** (optional): Leave blank unless your device requires API authentication.
- **Password** (optional): Leave blank unless your device requires API authentication. If needed, enter both username and password.
4. Click **Submit**.

If the configuration is correct, sensors will automatically appear in Home Assistant.
The integration first tries API requests without authentication. If the device
requires HTTP Basic Auth, provide both credentials; the integration retries
those requests with them.

## Sensors Provided
Here are the sensors available with this integration:

| Sensor ID                            | Friendly Name                      | Description                                                       |
| ------------------------------------ | ---------------------------------- | ----------------------------------------------------------------- |
| `chargebox_serial`                   | Chargebox Serial                   | Serial number of the chargebox.                                   |
| `chargebox_firmware`                 | Chargebox Firmware                 | Firmware version of the chargebox.                                |
| `chargebox_state`                    | Chargebox State                    | Connection state between Nanogrid Air and chargebox               |
| `chargebox_endpoint`                 | Chargebox Endpoint                 | Endpoint (URI) used by the chargebox (e.g. `mqtt://...`).         |
| `chargebox_port`                     | Chargebox Endpoint TCP Port        | TCP port for the chargebox endpoint.                              |
| `chargebox_connection_status`        | Chargebox Connection Status        | Current connection status of the chargebox EVSE.                  |
| `chargebox_outlet_1_state`           | Chargebox Outlet 1 State           | Current state of the chargebox outlet 1.                          |
| `chargebox_outlet_1_energy`          | Chargebox Outlet 1 Energy          | Total energy used by chargebox outlet 1 in kilowatt-hours (kWh).  |
| `chargebox_outlet_1_power`           | Chargebox Outlet 1 Power           | Current power usage of chargebox outlet 1 in kilowatts (kW).      |
| `chargebox_outlet_1_current_phase_1` | Chargebox Outlet 1 Current Phase 1 | Current output from outlet 1 in Phase 1 (Amperes).                |
| `chargebox_outlet_1_current_phase_2` | Chargebox Outlet 1 Current Phase 2 | Current output from outlet 1 in Phase 2 (Amperes).                |
| `chargebox_outlet_1_current_phase_3` | Chargebox Outlet 1 Current Phase 3 | Current output from outlet 1 in Phase 3 (Amperes).                |
| `device_serial`                      | Device Serial                      | The serial number of the Nanogrid Air device.                     |
| `device_firmware`                    | Device Firmware                    | Firmware version of the Nanogrid Air device.                      |
| `device_mac`                         | Device MAC                         | MAC address of the Nanogrid Air device.                           |												| `wifi_ssid`                          | WiFi SSID                          | SSID of the connected WiFi network.                               |
| `wifi_rssi`                          | WiFi Signal Strength               | WiFi RSSI in dBm, indicating signal strength.                     |
| `active_power_in_watt`               | Active Power In (Watt)             | Incoming power to the system in Watts.                            |
| `active_power_in_kw`                 | Active Power In (kW)               | Incoming power to the system in kilowatts.                        |
| `active_power_out`                   | Active Power Out                   | Outgoing power from the system in Watts.                          |
| `current_phase_1`                    | Current Phase 1                    | Electrical current in Phase 1 in Amperes (A).                     |
| `current_phase_2`                    | Current Phase 2                    | Electrical current in Phase 2 in Amperes (A).                     |
| `current_phase_3`                    | Current Phase 3                    | Electrical current in Phase 3 in Amperes (A).                     |
| `voltage_phase_1`                    | Voltage Phase 1                    | Voltage in Phase 1 in Volts (V).                                  |
| `voltage_phase_2`                    | Voltage Phase 2                    | Voltage in Phase 2 in Volts (V).                                  |
| `voltage_phase_3`                    | Voltage Phase 3                    | Voltage in Phase 3 in Volts (V).                                  |
| `total_energy_import`                | Total Energy Import                | Total imported energy measured in kilowatt-hours (kWh).           |
| `total_energy_export`                | Total Energy Export                | Total exported energy measured in kilowatt-hours (kWh).           |
| `meter_vendor`                       | Meter Vendor                       | Vendor name of the attached meter.                                |
| `meter_type`                         | Meter Type                         | Meter model/type.                                                 |
| `meter_id`                           | Meter ID                           | Meter identifier.                                                 |


## Polling and error handling

The integration shares one update coordinator across all 31 sensors. It reads
`/status/`, `/meter/`, and `/evse/` once per cycle, with a 30-second polling
interval and a 10-second timeout per request. Requests are sequential to limit
load on the device. The interval starts after the previous cycle completes.

If one endpoint fails, only its sensors become unavailable. If all endpoints
fail during startup, Home Assistant retries setup. Invalid or missing individual
measurements become unknown instead of being recorded as zero. Authentication
errors prompt you to provide or update credentials when required. Configuration
validates the address, port, optional credentials, and `/status/` response before
saving, and rejects duplicate host/port entries.

Existing sensor unique IDs, device grouping, names, units, and conversions are
preserved. The outlet energy sensor retains its last valid nonzero reading when
the device temporarily reports zero, including after a missing reading or network
outage. This safeguard is in memory and does not persist through a restart.

## Development and tests

Use Python 3.12 for the Home Assistant 2024.12 baseline:

```shell
python -m venv .venv
# Activate the virtual environment, then:
python -m pip install -r requirements-test.txt
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

Tests use actual Home Assistant classes, mocked application services, and a local
HTTP server. They do not require a CTEK device. GitHub Actions runs these checks
on Linux. A live Home Assistant installation and physical device should also be
tested before releasing, including recovery from device disconnection and an
actual charging session.

## Firmware Update

Ensure your device is running the latest firmware. For the best experience, it is recommended to update to **version 1.3.2**, which is the latest tested version.

You can download the latest firmware and instructions from the following links:

- [CTEK Firmware and Software](https://www.ctek.com/support/software-firmware#evsoftware)
- [Firmware Upgrade Instructions](https://www.ctek.com/storage/497AC4458015B3E8FAD37E648F487262A195814233840026D8BD92B258D080FF/86db5b7884c54f67bb18ecbddfe5b7cf/pdf/media/359668f65f084697984b036c4abd30fe/Firmware%20Upgrade%20Instructions%20-%20Nanogrid%20Air%203007%20-%2020231009002.pdf)

## API Documentation

For detailed information on the CTEK Nanogrid Air API, you can refer to the official [Local API Instructions for Nanogrid Air](https://www.ctek.com/storage/58B03CE11555207527045C1182860D36F0612F00232E61B4C383A0F15E1486BB/7b2ea9914c73429092a6426a8103da71/pdf/media/45fb7752636d4a5a8e5aad5b6b264074/Local%20API%20Instructions%20-%20Nanogrid%20Air%203007%20-%2020231009003.pdf).

## Troubleshooting

1. **Integration won't load**

   * Verify `custom_components/ctek_nanogrid_air/` is placed correctly and restart HA.
   * Check the host and port (default `80`). Username and password are optional; if authentication is required, enter both.

2. **Verify device responds (fast test)**

   * First try without credentials: `curl http://<CTEK_IP>/status/`
   * Only if the device requires authentication, try: `curl -u ctek http://<CTEK_IP>/status/` (replace `ctek` with your API username if different; `curl` prompts for the password).
   * If you get JSON, the device responds. Otherwise, check the IP address, port, firewall, and credentials if applicable.

3. **Sensors show “offline”**

   * Confirm network reachability from Home Assistant to the device (ping/curl from HA).
   * Check the port. If the device requires authentication, check both API credentials.
   * Check device firmware — update to the tested firmware if needed.

4. **Where to look for errors**

   * Home Assistant logs: *Settings → System → Logs*.
   * Add-on or Supervisor logs if you installed via HACS/Supervisor.

5. **Collect more info (enable debug)**
   Add to `configuration.yaml` (restart HA afterwards):

   ```yaml
   logger:
     default: info
     logs:
       custom_components.ctek_nanogrid_air: debug
   ```

   Then reproduce the issue and copy relevant log lines.

6. **Network / firewall / Docker notes**

   * If HA runs in Docker, ensure container can reach the device network and port 80 is open.
   * If using VLANs or IoT isolation, whitelist HA ↔ CTEK traffic.

# Quick: get a terminal in Home Assistant

Use the official **Terminal & SSH** add-on (Supervisor / Home Assistant OS) — simplest way to run `curl`.

Steps (very short):

1. Enable **Advanced Mode** in your user profile.
2. Go to **Settings → Add-ons → Add-on Store**, find **Terminal & SSH**, click **Install**.
3. In the add-on **Configuration**: set `username` + `password` or paste `authorized_keys`. Optionally enable “Show in sidebar” and “Start on boot”.
4. Start the add-on and click **Open Web UI** to get a terminal. Use it to run the appropriate `curl` command above or `ha core logs`.
