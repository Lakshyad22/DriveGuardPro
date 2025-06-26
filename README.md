🚗 DriveGuardPro
Advanced Driver Assistance System (ADAS) for hobbyist RC cars / small vehicles, featuring:

Adaptive Cruise Control (ACC)

Automatic Emergency Braking (AEB)

Lane Keeping Assist (LKS)

Adaptive Light Control (ALC)

Firmware Over-the-Air (FOTA)

Remote control via Bluetooth

Real‑time scheduling using FreeRTOS

📦 Project Structure
graphql
Copy
Edit
/ (root)
├── Application/         # Main STM32 application code
├── Bootloader/         # Flash bootloader supporting FOTA
├── FOTA/               # OTA client code (runs on Raspberry Pi)
├── GERBER/             # PCB layout and fabrication files
├── pictures/           # Diagrams and demonstration images
└── CONTRIBUTING.md     # Contribution guidelines
⚙️ Features Overview
1. Firmware Over‑the‑Air (FOTA)
A Raspberry Pi client checks your server every 5 s for firmware updates.

If available, it notifies via LED/Bluetooth, awaits confirmation, and transmits over UART.

The bootloader handles CRC checks, flash writes, and safe fallback if update fails.

2. Adaptive Cruise Control (ACC)
Ultrasonic sensor measures distance.

If ≥ 50 cm, full speed; if between 10–50 cm, speed adjusts adaptively when ACC flag is set.

3. Automatic Emergency Braking (AEB)
If obstacle < 10 cm, vehicle halts and triggers alarm + rear LED for 3 s.

4. Lane Keeping System (LKS)
IR sensors detect lane edges; if drift is detected, corrective steering is applied.

5. Adaptive Light Control (ALC)
LDR sensor reads ambient light and adjusts headlights:

≥ 93 → full brightness

80–92 → medium brightness

20–79 → dim

<20 → off

6. Bluetooth Remote Control
Commands via UART:

ini
Copy
Edit
J = activate ACC
B = initiate FOTA
H = halt all flags
F = forward
L = steer left
R = steer right
S = stop
7. FreeRTOS Integration
Tasks & priorities:

Task	Priority
AEB	Highest
LKS	High
ACC	Medium
ALC, FOTA, Bluetooth	Low

Event flags enable smooth inter-task communication.

🧰 Getting Started
Requirements:

Hardware:

STM32 microcontroller board

Ultrasonic + IR + LDR sensors

Raspberry Pi for OTA client

Bluetooth module (e.g. HC‑05)

Software: GCC toolchain (arm-none-eabi), FreeRTOS, Raspberry Pi with Python or C

Installation Steps:

git clone https://github.com/Lakshyad22/DriveGuardPro.git

Assemble hardware per GERBER/ documentation.

Build & flash:

Bootloader: compile under Bootloader/, flash to first sectors.

Application: compile under Application/, flash via bootloader or ST‑Link.

Configure the Raspberry Pi FOTA client (edit server URL/paths).

Power on Pi + MCU; monitor boot logs and LED indicators.

Use a Bluetooth terminal app to send commands and enable demos.

🛠️ Contribution
Contributions are welcome! Please:

Fork → branch off feature/bugfix.

Commit adhering to current style.

Test all behavioral changes.

Submit a PR with description of your changes.

Refer to CONTRIBUTING.md for details.

📄 License
This project is licensed under Apache License 2.0 — see LICENSE.

📞 Contact & Acknowledgements
Maintainer: Lakshya D.

Original FOTA Concept: Adapted from Ahmed Abdelghafar’s implementation.

Inspired By: ITI Course on Embedded Systems (Mahmoud Sayed, Sondos Ghieth, Mohamed Haggag, Yousef Ahmad).

🛡️ Safety Notice
This code is intended ONLY for hobbyist/educational demonstrations. Do not attempt vehicle integration on public roads. Ensure all tests are conducted in controlled environments with adult supervision.

📌 To Do / Future Enhancements
Integrate camera-based lane detection (via small CV module).

Add obstacle recognition using ultrasonic + IR fusion.

Develop smartphone GUI for remote video monitoring + alerts.
