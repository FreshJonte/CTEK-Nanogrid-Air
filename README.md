# CTEK-Nanogrid-Air
Home Assistant Custom Component for reading data from CTEK Nanogrid Air






**Disclaimer:** This is a third-party integration developed independently and is **not affiliated with CTEK**. Use at your own discretion.

## Features
This integration provides the following sensor data for your CTEK Nanogrid Air devices:
- Charger connection status and outlet states.
- Chargebox state and WiFi signal strength.
- Power metrics such as active power, current, and voltage for all phases.
- Energy import/export statistics.
- Device serial number, firmware, and MAC address.


## Installation

### Installation via HACS (Recommended)
1. Open Home Assistant and go to the **HACS** section in the sidebar.
2. Click on the **Custom repositories** tab (found under **Settings** in HACS).
3. In the **Custom repositories** section, click the **+** button in the bottom right corner.
4. Enter the following repository URL: https://github.com/FreshJonte/CTEK-Nanogrid-Air
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
- **Username**: Your API username.
- **Password**: Your API password.
4. Click **Submit**.

If the configuration is correct, sensors will automatically appear in Home Assistant.

## Sensors Provided
Here are the sensors available with this integration:

| Sensor ID                          | Friendly Name                | Description                                                           |
|------------------------------------|------------------------------|-----------------------------------------------------------------------|
| `charger_serial`                   | Charger Serial               | Serial number of the charger.                                         |
| `charger_connection_status`        | Charger Connection Status    | Current connection status of the charger.                             |
| `charger_outlet_1_state`           | Charger Outlet 1 State       | Current state of the charger outlet 1.                                |
| `charger_outlet_1_energy`          | Charger Outlet 1 Energy      | Total energy used by charger outlet 1 in kilowatt-hours (kWh).         |
| `charger_outlet_1_power`           | Charger Outlet 1 Power       | Current power usage of charger outlet 1 in kilowatts (kW).            |
| `charger_outlet_1_current_phase_1` | Charger Outlet 1 Current Phase 1 | Current output from charger outlet 1 in Phase 1 (Amperes).       |
| `charger_outlet_1_current_phase_2` | Charger Outlet 1 Current Phase 2 | Current output from charger outlet 1 in Phase 2 (Amperes).       |
| `charger_outlet_1_current_phase_3` | Charger Outlet 1 Current Phase 3 | Current output from charger outlet 1 in Phase 3 (Amperes).       |
| `device_serial`                    | Device Serial                | The serial number of the device.                                      |
| `device_firmware`                  | Device Firmware              | Firmware version of the device.                                       |
| `device_mac`                       | Device MAC                   | MAC address of the device.                                            |
| `chargebox_state`                  | Chargebox State              | Current state of the chargebox.                                       |
| `wifi_ssid`                        | WiFi SSID                    | SSID of the connected WiFi network.                                   |
| `wifi_rssi`                        | WiFi Signal Strength         | WiFi RSSI in dBm, indicating signal strength.                         |
| `active_power_in_watt`             | Active Power In (Watt)       | Incoming power to the system in Watts.                                |
| `active_power_in_kw`               | Active Power In (kW)         | Incoming power to the system in kilowatts.                            |
| `active_power_out`                 | Active Power Out             | Outgoing power from the system in Watts.                              |
| `current_phase_1`                  | Current Phase 1              | Electrical current in Phase 1 in Amperes (A).                         |
| `current_phase_2`                  | Current Phase 2              | Electrical current in Phase 2 in Amperes (A).                         |
| `current_phase_3`                  | Current Phase 3              | Electrical current in Phase 3 in Amperes (A).                         |
| `voltage_phase_1`                  | Voltage Phase 1              | Voltage in Phase 1 in Volts (V).                                      |
| `voltage_phase_2`                  | Voltage Phase 2              | Voltage in Phase 2 in Volts (V).                                      |
| `voltage_phase_3`                  | Voltage Phase 3              | Voltage in Phase 3 in Volts (V).                                      |
| `total_energy_import`              | Total Energy Import          | Total imported energy measured in kilowatt-hours (kWh).               |
| `total_energy_export`              | Total Energy Export          | Total exported energy measured in kilowatt-hours (kWh).               |

## Firmware Update

Ensure your device is running the latest firmware. For the best experience, it is recommended to update to **version 1.3.1**, which is the latest tested version.

You can download the latest firmware and instructions from the following links:

- [CTEK Firmware and Software](https://www.ctek.com/support/software-firmware#evsoftware)
- [Firmware Upgrade Instructions](https://www.ctek.com/storage/497AC4458015B3E8FAD37E648F487262A195814233840026D8BD92B258D080FF/86db5b7884c54f67bb18ecbddfe5b7cf/pdf/media/359668f65f084697984b036c4abd30fe/Firmware%20Upgrade%20Instructions%20-%20Nanogrid%20Air%203007%20-%2020231009002.pdf)

## API Documentation

For detailed information on the CTEK Nanogrid Air API, you can refer to the official [Local API Instructions for Nanogrid Air](https://www.ctek.com/storage/58B03CE11555207527045C1182860D36F0612F00232E61B4C383A0F15E1486BB/7b2ea9914c73429092a6426a8103da71/pdf/media/45fb7752636d4a5a8e5aad5b6b264074/Local%20API%20Instructions%20-%20Nanogrid%20Air%203007%20-%2020231009003.pdf).

## Troubleshooting

### Common Issues

1. **Integration Fails to Load**
   - Ensure the `ctek_nanogrid_air` folder is in the correct location (`custom_components` directory).
   - Check for typos in the configuration settings (host, port, username, password).
   - Review the Home Assistant logs for errors (`Settings > System > Logs`).

2. **Using `curl` for Troubleshooting**
   If you're having trouble with the integration or sensors not updating, you can verify that the device is responding correctly by running the following `curl` command in your terminal:

   ```bash
   curl -u ctek:password http://your.ip.goes.here/status/

3. **"Offline" State for Sensors**
   - Verify that the CTEK device is online and accessible at the specified IP and port.
   - Check your network settings to ensure the Home Assistant instance can communicate with the device.
   - Ensure the username and password are correct for accessing the CTEK API.

3. **Error Logs**
   If you encounter issues, review the logs:
   - Go to **Settings > System > Logs**.
   - Look for entries related to `ctek_nanogrid_air` to identify the problem.

### Debugging
Enable debug logging for this integration to gather more information:
1. Add the following to your `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.ctek_nanogrid_air: debug


