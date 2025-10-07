import os
import subprocess
import serial
import config
import board_utils
import sketch_utils


def run_cycle(cycle_count, serial_port, board_fqbn):
    sketch_to_upload = config.SKETCHES[cycle_count % len(config.SKETCHES)]
    expected_serial_char = "A" if sketch_to_upload == "pattern_A" else "B"

    print(f"--- Cycle {cycle_count + 1}: Uploading {sketch_to_upload} ---")

    upload_command = (
        f"arduino-cli upload -p {serial_port} --fqbn {board_fqbn} {sketch_to_upload}"
    )
    result = subprocess.run(upload_command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FATAL: Arduino upload/verify failed at cycle {cycle_count + 1}.")
        print("This likely indicates flash memory failure.")
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        return False, cycle_count

    print("Upload and verification successful. Waiting for serial...")

    try:
        with serial.Serial(serial_port, 9600, timeout=10) as serialPort:
            data = serialPort.read(10).decode(errors="ignore").strip()
    except serial.SerialException as e:
        print(f"FATAL: Could not open serial port {serial_port} after upload.")
        print(f"Details: {e}")
        return False, cycle_count

    if data == expected_serial_char:
        cycle_count += 1
        print(f"Serial check passed. Cycle count: {cycle_count}")
    elif data.startswith("F"):
        failed_address = data[1:] if len(data) > 1 else "unknown"
        print(f"FATAL: Flash memory verification failed at cycle {cycle_count + 1}.")
        print(f"Failed address: {failed_address}")
        print(f"Expected pattern: {expected_serial_char} (0xFF if A, 0x00 if B)")
        print("This indicates flash memory bit failure.")
        return False, cycle_count
    else:
        print(f"FATAL: Serial check failed at cycle {cycle_count + 1}.")
        print(f"Expected '{expected_serial_char}' but got '{data}'.")
        print("This could indicate a CPU or other hardware failure.")
        return False, cycle_count

    return True, cycle_count


def main():
    serial_port, board_fqbn = board_utils.discover_board()
    sketch_utils.verify_sketches()
    sketch_utils.compile_sketches(board_fqbn)

    cycle_count = 0
    if os.path.exists(config.CACHE_FILE):
        with open(config.CACHE_FILE, "r") as f:
            try:
                cycle_count = int(f.read().strip())
            except (ValueError, TypeError):
                cycle_count = 0
    print(f"Starting from cached cycle count: {cycle_count}")

    try:
        while True:
            success, cycle_count = run_cycle(cycle_count, serial_port, board_fqbn)
            if not success:
                break
    except KeyboardInterrupt:
        print("\nExiting due to user interrupt.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        with open(config.CACHE_FILE, "w") as f:
            f.write(str(cycle_count))
        print(f"Exiting. Total successful cycles: {cycle_count}")


if __name__ == "__main__":
    main()
