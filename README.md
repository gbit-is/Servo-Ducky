<img src="https://raw.githubusercontent.com/gbit-is/Servo-Ducky/e62c152b98f82520968ef0eb3d0a9bc073e9e210/images/servo_ducky_logo_full.svg" alt="diagram" width="90%"/>


# Servo Ducky 
#### Work In Progress servo automation system



# Big Picture

Using a raspberry pi pico and a PCA9685 16 Servos can be controlled  
Using a simple machine instruction language, scripts can be created   
Using USB serial commands, those scripts can be executed   


# S-Code
like g-code ... but for servos ... so ... s-code, I didn't work overly hard on that name

#### Structure
The code is split into sections, defined by [headers]  
only one header must exist, [main] and it is called when a script is started   
any number of headers can exist, think of them as functions and they can be called by [main],

#### Commands
Legend:   
    \<Must Be specified\>   
    [can be specified]

M\<Servo Number\> \<Degree to move to\> [Time to move there]  
DELAY \<time\>  
F \<function to execute\>  \[Variables to pass to function [[WIP]]\]  
\# can be placed anywhere, lines beginning with \# are ignored and any text in lines after \# is ignored

# Example



```
[main] # The codeblock that get's executed when a script is run
M0 0          # Motor 0, go to position 0°
M1 0          # Motor 1, go to position 0°
M2 90         # Motor 2, go to position 90°
DELAY 500     # Wait for half a second
M0 90 2500    # Motor 0, go to position 90° in linear steps, over a period of 2,5 seconds
DELAY 2500    # wait for motor 0 to go to position 90°
M1 180        # Motor 1, go to position 180°
```

