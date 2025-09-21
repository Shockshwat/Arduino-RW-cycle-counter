# Arduino RW Cycle Counter

RW stands for Read & Write.

## Overview

This script is pretty simple, it uploads 30kb files of 01 and 10 pattern (Essentially flipping the bits in the flash memory) and does a serial check to see if the arduino is still functioning.

The goal is to find how many times can you upload data to an arduino until it eventually dies.

## Getting Started

1. **Clone this repository**

   ```bash
   git clone https://github.com/yourusername/your-arduino-project.git
   ```

2. **Connect your Arduino board**  
   Plug your Arduino into your computer via USB.

3. **Run main.py**
   ```bash
   python3 main.py
   ```

## Requirements

1. pyserial
2. arduino-cli
3. arduino core package for your arduino

## Working

We generate 2 sketches, pattern A and pattern B. In either pattern, we use avr/pgmspace.h to fill up storage in the flash memory. In one pattern we fill it with 0x55 (01010101) and with 0xAA (10101010) in other. The goal is to flip the bits in the memory in each cycle so that we can find when does the flash memory fail.

The main script uses arduino-cli to first find USB ports on the computer and detects where arduino is connected. If it cannot detect which arduino is connected, it presents a list to choose from.

It caches the information, checks if there is a count cache; i.e. if the program was run before and starts the cycle. It would first upload the file, verify that it was uploaded and check the serial of that USB port if arduino reports back, If everything goes well then it adds one to the cycle count and continues with the next cycle.

Eventually when the arduino stops responding, it exits showing the final count and also cacheing it.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.
