Simple script to monitor ProtonVPN log files and update qbittorrent via it's web API.
Checks the ProtonVPN logs every minute and updates qBittorrent if a port change is found.

- Clone the repo to your system `git clone https://github.com/Audionut/protonvpn-forward-qbit` - or download a zip of the source
- Install necessary python modules `pip3 install --user -U -r requirements.txt`
- Edit the user variables at the top of the python file:
    - `log_dir_path = r'C:\Users\USERNAME\AppData\Local\ProtonVPN\Logs'`
    - `qb_url = "http://url:port"`
    - `qb_username = "username"`
    - `qb_password = "password"`
- Run `py portForward.py` from an elevated command prompt.
- Setup a task schedule `https://chatgpt.com/share/67039a6a-7ec0-8004-a25a-9623324550d6`