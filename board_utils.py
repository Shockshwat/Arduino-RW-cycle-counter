import os
import subprocess
import json
from typing import Optional


def select_from_list(prompt: str, options: list) -> Optional[str]:
    print(prompt)
    if not options:
        return None
    for i, option in enumerate(options):
        print(f"  [{i+1}] {option}")

    while True:
        try:
            choice = int(input(f"Enter your choice (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def discover_board():
    BOARD_CACHE_FILE = ".board_cache.json"
    board_cache = {}
    if os.path.exists(BOARD_CACHE_FILE):
        with open(BOARD_CACHE_FILE, "r") as f:
            try:
                board_cache = json.load(f)
            except json.JSONDecodeError:
                pass

    print("--- Discovering connected Arduino boards ---")
    try:
        result = subprocess.run(
            "arduino-cli board list --format json",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        board_data = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(
            "Error: Could not run 'arduino-cli board list'. Is arduino-cli installed and in your PATH?"
        )
        print(f"Details: {e}")
        exit(1)

    plausible_boards = [
        p
        for p in board_data.get("detected_ports", [])
        if "VID:PID" in p.get("port", {}).get("properties", {})
        or "usb" in p.get("port", {}).get("protocol_label", "").lower()
    ]

    if not plausible_boards:
        print(
            "Error: No plausible Arduino boards found (no USB serial ports). Please connect a board and try again."
        )
        exit(1)

    selected_port_address = None
    if len(plausible_boards) == 1:
        board = plausible_boards[0]
        selected_port_address = board["port"]["address"]
        print(f"Automatically selected port: {selected_port_address}")
    else:
        print("Multiple plausible boards found. Please select one:")
        port_options = [
            f"{b['port']['address']} ({b.get('matching_boards', [{'name': 'Unknown'}])[0]['name']})"
            for b in plausible_boards
        ]
        selected_option = select_from_list(
            "Select the port for your target Arduino:", port_options
        )
        if not selected_option:
            print("No port selected. Exiting.")
            exit(1)
        selected_port_address = selected_option.split(" ")[0]

    if selected_port_address in board_cache:
        board_fqbn = board_cache[selected_port_address]
        print(f"Using cached FQBN for {selected_port_address}: {board_fqbn}")
        return selected_port_address, board_fqbn

    print(
        f"No cached board type for {selected_port_address}. Please specify the board type."
    )
    try:
        result = subprocess.run(
            "arduino-cli board listall --format json",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        all_boards = json.loads(result.stdout).get("boards", [])
        fqbn_options = sorted(list(set([b["fqbn"] for b in all_boards])))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        print(
            "Could not get a list of all possible boards. Please enter the FQBN manually."
        )
        board_fqbn = input("Enter the FQBN for your board (e.g., arduino:avr:nano): ")
    else:
        if not fqbn_options:
            print(
                "No cores found, Have you installed any board packages via arduino-cli?"
            )
            exit(1)
        board_fqbn = select_from_list("Select the board type (FQBN):", fqbn_options)

    if not board_fqbn:
        print("Error: No board type selected. Exiting.")
        exit(1)

    board_cache[selected_port_address] = board_fqbn
    with open(BOARD_CACHE_FILE, "w") as f:
        json.dump(board_cache, f, indent=2)

    print(
        f"You selected: {board_fqbn} on port {selected_port_address}. This will be cached."
    )
    return selected_port_address, board_fqbn
