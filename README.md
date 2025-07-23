<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/e62c152b98f82520968ef0eb3d0a9bc073e9e210/images/servo_ducky_logo_full.svg" alt="diagram" width="90%"/>


# Servo Ducky 
#### Work In Progress servo automation system



# Big Picture

Using a raspberry pi pico and a PCA9685 16 Servos can be controlled  
Using a simple machine instruction language, scripts can be created   
Using USB serial commands, those scripts can be executed   
Having an easy-to-use web interface

# S-Code
like g-code ... but for servos ... so ... s-code, I didn't work overly hard on that name

#### Structure
The code is split into sections, defined by [headers]  
only one header must exist, [main] and it is called when a script is started   
any number of headers can exist, think of them as functions and they can be called by [main],

# Commands

Legend:   
    \<Must Be specified\>   
    [can be specified]

#### Basic commands
S\<Servo Number\> \<Degree to move to\> [Time to move there]  # Expanded on in 
DELAY \<time\>  
R \<routine to execute\>  \[Variables to pass to a routine \]  

#### Advanced commands

Lists:
If you want servo 1,2 and 4 all to go degree 90, you could write that as:
```
S1 90
S2 90
S4 90
```
or you could use a list and write it as
```
S[1,2,4] 90
```

Ranges:
If you want servo 1,2,3,4 and 5 all to move to 90, you could write that as:
```
S1 90
S2 90
S3 90
S4 90
S5 90
```
or you could use a range and write it as:
```
S[1...5] 90
```


#### Comments
\# Comments can be placed anywhere, lines beginning with \# are ignored and any text in lines after \# is ignored




# Example



```
[main] # The codeblock that get's executed when a script is run
S0 0          # Servo 0, go to position 0°
S1 0          # Servo 1, go to position 0°
S2 90         # Servo 2, go to position 90°
DELAY 500     # Wait for half a second
S0 90 2500    # Servo 0, go to position 90° in linear steps, over a period of 2,5 seconds
DELAY 2500    # wait for Servo 0 to go to position 90°
S1 180        # Servo 1, go to position 180°
R some_routine S4 S5 0   # Execute routine "some_routine" with variables 0 and 1 as S4 and S5, and variable 2 as 0
delay 500    # wait for half a second
R some_routine S5 S4 180  # execute routime "some_routine" with the servo variables from before, but switched around and the final variable as 180


[some_routine]    # Create header for new routine
_0 0              # First specified servo, go to position 0
_1 0              # Second specified servo, go to position 0
DELAY 500         # wait for half a second
_0 90             # First specified Servo, go to position 90
_1 45             # Second specified servo, go to position 45
DELAY 1000        # wait for a second
_0 _2             # First specified Servo, go to the position specified in the third varialbe
_1 _2             # Second specified Servo, go to the position specified in the third varialbe


```

# Web Interface (SDCC - Servo Ducky Command Center ) 

### How the interface looks 
<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/refs/heads/main/images/sdcc.png" alt="SDCC look" width="90%"/>

### How the interface works

<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/refs/heads/main/images/sdcc_annotated.png" alt="SDCC annotations " width="90%"/>


| Number    | explination |
| -------- | ------- |
| 1  | Select the Servo Ducky serial device and connect to it    |
| 2 | Disconnect the serial device     |
| 3    | enable/disable debug logging from Servo Ducky    |
| 4 | Send a command to servo ducky to cancel all running tasks |
| 5 | serial terminal, communications with Servo Ducky |
| 6 | type and send serial commands manually to Servo Ducky |
| 7 | Control the positions of servos |
| 8 | Add the current position of the servo, to the cursor location of the script editor |
| 9 | Trigger scripts present on servo ducky |
| 10 | Run the script in the script editor (does not save it to the device)
| 11 | Open a file picker, select a  script and load it to the script editor |
| 12 | Opens a file picker to save the script from the script editor |
| 13 | Built in script editor |


[live web interface](https://gbit-is.github.io/ServoDuckyCommandCenter/)
[Repo for web interface](https://github.com/gbit-is/ServoDuckyCommandCenter)

