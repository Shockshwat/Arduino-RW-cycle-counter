SKETCHES = ["pattern_A", "pattern_B"]
CACHE_FILE = "cycle_count_cache.txt"

SKETCH_A_CODE = """
#include <avr/pgmspace.h>

const PROGMEM byte flash_pattern[28000] = {0x55};

void setup() {
  volatile uint32_t dummy_sum = 0;
  for (unsigned int i = 0; i < sizeof(flash_pattern); i++) {
    dummy_sum += pgm_read_byte_near(flash_pattern + i);
  }

  Serial.begin(9600);
  Serial.print('A');
}

void loop() {
}
"""

SKETCH_B_CODE = """
#include <avr/pgmspace.h>

const PROGMEM byte flash_pattern[28000] = {0xAA};

void setup() {
  volatile uint32_t dummy_sum = 0;
  for (unsigned int i = 0; i < sizeof(flash_pattern); i++) {
    dummy_sum += pgm_read_byte_near(flash_pattern + i);
  }

  Serial.begin(9600);
  Serial.print('B');
}

void loop() {
}
"""

SKETCH_MAP = {
    "pattern_A": SKETCH_A_CODE,
    "pattern_B": SKETCH_B_CODE,
}
