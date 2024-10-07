import re
import requests
import time
import os

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
def get_latest_log_file(log_dir):
    try:
        # List all files in the directory
        log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]

        # Find the most recently modified file
        latest_log_file = max(log_files, key=os.path.getmtime)
        print(f"Latest log file selected: {latest_log_file}")
        return latest_log_file
    except Exception as e:
        print(f"Error selecting the latest log file: {e}")
        return None


# Function to parse the latest log file and retrieve the forwarded port
def get_forwarded_port_from_log(log_file):
    try:
        with open(log_file, 'r') as log_file:
            log_data = log_file.read()

            # Regular expression to match the port pair in the log format
            match = re.search(r'Port pair (\d+)->\1', log_data)
            if match:
                forwarded_port = match.group(1)
                print(f"Found Forwarded Port: {forwarded_port}")
                return forwarded_port
            else:
                print("Forwarded port not found in the log.")
                return None
    except FileNotFoundError:
        print("Log file not found. Please check the path.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# Function to log in to qBittorrent's WebUI
def qb_login(session):
    login_url = f"{qb_url}/api/v2/auth/login"
    data = {"username": qb_username, "password": qb_password}
    response = session.post(login_url, data=data)
    if response.text == "Ok.":
        print("Logged in successfully.")
    else:
        print(f"Failed to log in: {response.text}")
        exit(1)


# Function to update the qBittorrent listening port
def update_qbittorrent_port(session, new_port):
    settings_url = f"{qb_url}/api/v2/app/setPreferences"
    payload = {
        "json": '{"listen_port": %d}' % int(new_port)  # Update the listening port
    }
    response = session.post(settings_url, data=payload)
    if response.status_code == 200:
        print(f"Listening port updated to {new_port}.")
    else:
        print(f"Failed to update the listening port: {response.status_code}, {response.text}")


# Main function to check the log every minute and update qBittorrent if necessary
def main():
    global last_forwarded_port  # Use the global variable to track the last forwarded port

    with requests.Session() as session:
        # Log in to qBittorrent first
        qb_login(session)

        while True:
            # Get the latest log file in the directory
            latest_log_file = get_latest_log_file(log_dir_path)

            if latest_log_file:
                # Get the forwarded port from the log file
                forwarded_port = get_forwarded_port_from_log(latest_log_file)

                # If a valid port is found and it's different from the last one
                if forwarded_port and forwarded_port != last_forwarded_port:
                    print(f"Updating qBittorrent to new port: {forwarded_port}")
                    update_qbittorrent_port(session, forwarded_port)
                    last_forwarded_port = forwarded_port  # Update the in-memory last port

            # Wait for 60 seconds before checking again
            time.sleep(60)


if __name__ == "__main__":
    main()