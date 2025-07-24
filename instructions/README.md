# Electrical Connection
You can ofcourse hook this up however you want, to whatever circuitpython capable board you want, the 2 options I present here are what I tried with the RP2040-Zero from waveshare, I like that board to its small form factor, USB-C option, and built-in reset button (great for debugging).

<b> Option 1 </b>  
I started out designing option 1, which I feel is a very clean and nice design, but actually soldering it together was quite the hassle and not having access to a large part of the pins is a downside as well, since it limits the possibilites of how they can be used (using physical buttons to trigger animations for example)

<b> Opttion 2</b>  
Then I decided to start again from scratch, thinking "what is the simplest way to hook the 2 together", using the "wrong"* side of the PCA9685 board I can align the I2C pins directly on the RP2040-Zero and the PCA9685, but it still required power ofcourse, since it draws very little power (the board itself, not the servos) setting the GPIO connected to VCC to high and the GPIO connected to GND as low, we can provide power to the PCA9685.

<b> Powering the servos </b>  
If you are using a RP2040-Zero, a good USB-C power source and not a lot of servos, directly powering the the PCA9685 from the RP2040-Zero is an option since the 5V pin on the RP2040-Zero is coming directly from the USB-C cable(1)
If you are powering the RP2040-Zero with a good USB-C source and not running many servos you can connect the RP2040-Zero 5V pin, directly to V+ on the PCA9685 and a GND pin from each side  (in option 1 it can be soldered directly, in option 2 due to the locations on the pins that is not an option, a short cable from 5V on the RP2040-Zero to the screw

<b>"USB-C is okay if you don't have a lot of servos" .......   </b> 
I have no number or actual source for this claim, it just sounds iffy to me personally to be drawing to much power from such a small board, but keep in mind that the lower limit of USB-C power draw is 3A, a single SG90 servo can draw as much as 500mA according to some sources (without citations) and up to 360mA according to a source that claims to have measured it (that is under stall conditions, in normal operation it goes up to 250mA (but can be as little as 100mA)    
According to these numbers, with the minimum of 3A (since none of us would ever use some cheap cable, psu or hook the other end up to USB-A and have less then 3A avaivable).... at 500mA that supports 6x SG90 servos, at 360mA it supports 8,3 SG90 servos and at 250mA it supports 12 SG90 servos. the PCA9685 has pins for 16 servos, so with standard USB-C power, running all 16 servos at max power goes beyond what is capable of being delivered by the USB-C connector.

And keep in mind, that is for SG90, that is a small servo, a MG996R has a stall current of 2.5A, which almost maxes out your amperage budget


\* since it's I2C there is no actual input/output side on this board, but it usually comes packaged with headers on the left side of the board and the right side being for daisy chaining another board to it 

(1) ["The VSYS pin of the RP2040 is connected to the VUSB pin directly in RP2040-zero"](https://www.waveshare.com/wiki/RP2040-Zero#accordion11)

# Option 1

<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/refs/heads/main/images/connection_diagram_framed.svg" alt="diagram" width="90%"/>

| RP2040 | PCA9685 | Notes |
| ------ | ------- | ----- |
| GND    | GND     | Ground |
| GP2    | OE      | Output Enable |
| GP1    | SCL     | I2C Clock |
| GP0    | SDA     | I2C Data |
| 3.3V   | VCC     | PCA9685 Power |
|  ** 5V ** | ** V+  **    | Powers the Servo's from the Pi, should not be used except for debugging |

# Option 2 
### Pin V+ on the PCA9685 should !!NOT!! have a header and should !!NOT!! be connected to GP14 
Electrical connections:  
<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/refs/heads/main/images/connection_diagram_alt_framed.svg" alt="diagram" width="90%"/>  

Layout:  
<img src="https://raw.githubusercontent.com/gbit-is/Servo-ducky/refs/heads/main/images/connection_option_2_3d.png" alt="conection_2" width="90%"/>  

| RP2040 | PCA9685 | Notes |
| ------ | ------- | ----- |
| GP29    | GND     | Ground |
| GP28   | OE      | Output Enable |
| GP27    | SCL     | I2C Clock |
| GP26   | SDA     | I2C Data |
| GP15   | VCC     | PCA9685 Power |
|  ** 5V ** | ** V+  **    | Powers the Servo's from the Pi, should not be used except for debugging |




# Assemble the frame For Connection Option 1

<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/refs/heads/main/images/assembly.gif" alt="diagram" width="90%"/>

