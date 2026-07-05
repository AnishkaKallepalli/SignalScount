# SignalStrengthTest

SignalStrengthTest is a simple Android application built in Java that reads and displays the phone's current cellular signal strength (dBm) using Android's Telephony APIs.

## Features
- Displays real-time cellular signal strength
- Supports LTE, GSM, and WCDMA networks
- Refresh button to update the current reading
- Requests the necessary Android permissions for telephony access

## Purpose
This application serves as the Android component of a larger embedded systems project: a remote-controlled ESP32-based rover that generates cellular connectivity heatmaps. Future versions of this app will send signal strength data to an ESP32 over Wi-Fi for logging alongside GPS coordinates.

## Technologies
- Java
- Android Studio
- Android TelephonyManager API

## Future Improvements
- Automatic periodic signal updates
- 5G (NR) support
- HTTP communication with ESP32
- Background data collection
- Signal logging and export
