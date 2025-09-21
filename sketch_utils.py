import os
import subprocess
import config


def verify_sketches():
    print("--- Verifying sketches ---")
    for sketch_name, sketch_code in config.SKETCH_MAP.items():
        sketch_path = f"./{sketch_name}"
        ino_path = f"{sketch_path}/{sketch_name}.ino"
        if not os.path.isdir(sketch_path) or not os.path.exists(ino_path):
            print(f"Sketch {sketch_name} not found, creating it.")
            os.makedirs(sketch_path, exist_ok=True)
            with open(ino_path, "w") as f:
                f.write(sketch_code)
        else:
            with open(ino_path, "r") as f:
                if f.read() != sketch_code:
                    print(f"Sketch {sketch_name} has changed, updating it.")
                    with open(ino_path, "w") as f:
                        f.write(sketch_code)
                else:
                    print(f"Sketch {sketch_name} is up to date.")


def compile_sketches(board_fqbn):
    print("--- Pre-compiling sketches ---")
    for sketch in config.SKETCHES:
        print(f"Compiling {sketch}...")
        compile_command = f"arduino-cli compile --fqbn {board_fqbn} {sketch}"
        result = subprocess.run(
            compile_command, shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Error compiling {sketch}:")
            print(result.stderr)
            exit(1)
    print("--- Compilation complete ---")
