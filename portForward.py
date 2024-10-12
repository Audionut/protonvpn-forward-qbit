import re
import requests
import time
import os
import argparse

# Path to the ProtonVPN log files (Update this path)
# Script will monitor all files in this path and chose the last modified
log_dir_path = r'C:\Users\USERNAME\AppData\Local\ProtonVPN\Logs'

# qBittorrent WebUI URL and credentials (Update these)
qb_url = "http://url:port"
qb_username = "username"
qb_password = "password"

# Store the last forwarded port to avoid unnecessary updates
last_forwarded_port = None


# Function to find the latest modified log file in the log directory
def get_latest_log_file(log_dir, verbose):
    try:
        # List all files in the directory
        log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]

        # Find the most recently modified file
        latest_log_file = max(log_files, key=os.path.getmtime)

        if verbose:
            print(f"Latest log file selected: {latest_log_file}")
        return latest_log_file
    except Exception as e:
        print(f"Error selecting the latest log file: {e}")
        return None


# Function to read the log file from the bottom and find the latest port pair
def get_forwarded_port_from_log(log_file, verbose):
    try:
        with open(log_file, 'rb') as f:
            # Move the file pointer to the end of the file
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            buffer_size = 8192  # Read in chunks of 8KB

            # Start reading the file from the end
            if file_size > buffer_size:
                f.seek(-buffer_size, os.SEEK_END)
            else:
                f.seek(0)

            # Read the file from the point where we positioned the pointer
            data = f.read().decode('utf-8')

            # Split the data into lines and reverse the lines for backward reading
            lines = data.splitlines()[::-1]

            # Iterate through the lines and find the first match for "Port pair"
            for line in lines:
                match = re.search(r'Port pair (\d+)->\1', line)
                if match:
                    forwarded_port = match.group(1)
                    if verbose:
                        print(f"Found Forwarded Port: {forwarded_port}")
                    return forwarded_port

            print("Forwarded port not found in the log.")
            return None

    except FileNotFoundError:
        print("Log file not found. Please check the path.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# Function to log in to qBittorrent's WebUI
def qb_login(session, verbose):
    login_url = f"{qb_url}/api/v2/auth/login"
    data = {"username": qb_username, "password": qb_password}
    response = session.post(login_url, data=data)
    if response.text == "Ok.":
        print("Logged in successfully.")
    else:
        print(f"Failed to log in: {response.text}")
        exit(1)


# Function to update the qBittorrent listening port
def update_qbittorrent_port(session, new_port, verbose):
    settings_url = f"{qb_url}/api/v2/app/setPreferences"
    payload = {
        "json": '{"listen_port": %d}' % int(new_port)  # Update the listening port
    }
    response = session.post(settings_url, data=payload)
    if response.status_code == 200:
        if verbose:
            print(f"Listening port updated to {new_port}.")
    else:
        print(f"Failed to update the listening port: {response.status_code}, {response.text}")


# Main function to check the log every minute and update qBittorrent if necessary
def main():
    global last_forwarded_port  # Use the global variable to track the last forwarded port

    # Set up argparse for command-line arguments
    parser = argparse.ArgumentParser(description="Monitor ProtonVPN logs and update qBittorrent port.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    with requests.Session() as session:
        # Log in to qBittorrent first
        qb_login(session, args.verbose)

        while True:
            # Get the latest log file in the directory
            latest_log_file = get_latest_log_file(log_dir_path, args.verbose)

            if latest_log_file:
                # Get the forwarded port from the log file (starting from the bottom)
                forwarded_port = get_forwarded_port_from_log(latest_log_file, args.verbose)

                # If a valid port is found and it's different from the last one
                if forwarded_port and forwarded_port != last_forwarded_port:
                    print(f"Updating qBittorrent to new port: {forwarded_port}")
                    update_qbittorrent_port(session, forwarded_port, args.verbose)
                    last_forwarded_port = forwarded_port  # Update the in-memory last port

            # Wait for 60 seconds before checking again
            time.sleep(60)


if __name__ == "__main__":
    main()
