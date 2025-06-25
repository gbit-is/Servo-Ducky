# Electrical Connection


<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/refs/heads/main/images/connection_diagram_framed.svg" alt="diagram" width="90%"/>

| RP2040 | PCA9685 | Notes |
| ------ | ------- | ----- |
| GND    | GND     | Ground |
| GP2    | OE      | Output Enable |
| GP1    | SCL     | I2C Clock |
| GP0    | SDA     | I2C Data |
| 3.3V   | VCC     | PCA9685 Power |
|  ** 5V ** | ** V+  **    | Powers the Servo's from the Pi, should not be used except for debugging |



# Assemble the frame

<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/refs/heads/main/images/assembly.gif" alt="diagram" width="90%"/>

