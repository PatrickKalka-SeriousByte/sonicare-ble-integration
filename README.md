# Sonicare BLE Integration

This is a custom integration for Home Assistant that enables Bluetooth Low Energy (BLE) communication with compatible **Philips Sonicare toothbrushes**. It allows automatic tracking of brushing data like duration, battery level, and session metadata — all directly in your smart home dashboard.

![GitHub Release](https://img.shields.io/github/v/release/PatrickKalka-SeriousByte/sonicare-ble-integration?style=for-the-badge)
![GitHub Downloads](https://img.shields.io/github/downloads/PatrickKalka-SeriousByte/sonicare-ble-integration/latest/total?style=for-the-badge)
![Maintenance](https://img.shields.io/maintenance/yes/2025?style=for-the-badge)

---

## ✨ Features

- BLE pairing via Home Assistant UI
- Local push communication — no polling
- Automatically connects to compatible Philips Sonicare devices
- Exposes brushing session data as Home Assistant sensors

### Provided sensors:
- Battery Level
- Brushing Time
- Routine Length
- Handle State
- Available Brushing Routine
- Intensity
- Handle Time
- Brushing Session ID
- Last Session ID
- Loaded Session ID

---

## 📦 Installation via HACS (Recommended)

1. Go to **HACS → Integrations → + Add Custom Repository**
2. Enter this repository URL:  
   `https://github.com/PatrickKalka-SeriousByte/sonicare-ble-integration`
3. Choose **Integration** as category and confirm
4. Then go to **HACS → Integrations → + Explore & Download Repositories**
5. Search for `sonicare-ble-integration` and install it
6. Restart Home Assistant

---

## 📦 Manual Installation (Alternative)

1. Download the latest [release ZIP](https://github.com/PatrickKalka-SeriousByte/sonicare-ble-integration/releases/latest)
2. Extract the contents to:
