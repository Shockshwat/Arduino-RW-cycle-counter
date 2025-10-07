SKETCHES = ["pattern_A", "pattern_B"]
CACHE_FILE = "cycle_count_cache.txt"
FLASH_PATTERN_SIZE = 28000
PATTERN_A_BYTE = 0xFF
PATTERN_B_BYTE = 0x00


def generate_ff_array():
    values = ",".join(["0xFF"] * 28000)
    return f"const PROGMEM byte flash_pattern[28000] = {{{values}}};"


def generate_00_array():
    values = ",".join(["0x00"] * 28000)
    return f"const PROGMEM byte flash_pattern[28000] = {{{values}}};"


SKETCH_A_CODE = f"""
#include <avr/pgmspace.h>

{generate_ff_array()}

void setup() {{
  Serial.begin(9600);
  
  for (unsigned int i = 0; i < 28000; i++) {{
    byte value = pgm_read_byte_near(flash_pattern + i);
    if (value != 0xFF) {{
      Serial.print('F');
      Serial.println(i);
      return;
    }}
  }}
  
  Serial.print('A');
}}

void loop() {{

}}
"""

SKETCH_B_CODE = f"""
#include <avr/pgmspace.h>

{generate_00_array()}

void setup() {{
  Serial.begin(9600);

  for (unsigned int i = 0; i < 28000; i++) {{
    byte value = pgm_read_byte_near(flash_pattern + i);
    if (value != 0x00) {{
      Serial.print('F');
      Serial.println(i);
      return;
    }}
  }}
  
  Serial.print('B');
}}

void loop() {{

}}
"""

SKETCH_MAP = {
    "pattern_A": SKETCH_A_CODE,
    "pattern_B": SKETCH_B_CODE,
}
