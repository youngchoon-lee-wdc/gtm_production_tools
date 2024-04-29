import sys
import time
import requests
import subprocess

GTM_WEBCLICKER_SERVER='10.163.203.16'

def check_host_status(host):
    host = host.strip()+'.sdcorp.global.sandisk.com'
    result = subprocess.run(['ping', '-c', '1', host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def send_webclicker_command(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

if __name__ == "__main__":
    # Parse arguments
    if len(sys.argv) != 3:
        print("Usage: python GTM_cold_boot.py [GTM hostname] [Web Clicker command]")
        sys.exit(1)

    gtm_hostname = sys.argv[1].strip()
    command = sys.argv[2].strip()
    print(f"hostname : {gtm_hostname}, command : {command}")

    webclicker_url = f"http://{GTM_WEBCLICKER_SERVER}:5000/{gtm_hostname}__{command}"
    send_command = send_webclicker_command(webclicker_url)
    print(f'{gtm_hostname} is issued by {command} command')
    if send_command is None:
        sys.exit(1)

    if command == 'Power': 
        # Sleep for 10 seconds
        time.sleep(10)
        if check_host_status(gtm_hostname) == False:
            print(f"{gtm_hostname} is down, so it should be turned on")
            # If command is 'Power', retry the same URL to turn on the machine for cold boot
            power_on = send_webclicker_command(webclicker_url)
            print(f'{gtm_hostname} is issued by {command} command again')
            if power_on is None:
                sys.exit(1)
