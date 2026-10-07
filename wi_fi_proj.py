import platform
from run_modul import my_run
import re 
import argparse 
import time 
from wlan_scan import trigger_scan

def scan_wifi():
	system_platform =platform.system().lower()

	if system_platform == "windows":
		return scan_wifi_windows()
	else:
		print("Не соответствует не одной из платфом из перечня =windows=")
		return []

def scan_wifi_windows():
	trigger_scan()
	try:
		result = my_run(
			["netsh", "wlan", "show", "networks", "mode=Bssid"],
			capture_output=True, encoding = "cp866"
		)
		if result.returncode != 0:
			print("Error: Unable to scan networks. Make sure Wi-Fi is enabled.")
			return []

		output = result.stdout
		if not output.strip():
			print("No Wi-Fi networks found")
			return[]
		return parser_networks_windows(output)
	except Exception as e:
		print(f"Error {e}")
		return[]

def parser_networks_windows(output):
	ssid_pattern = re.compile(r"^SSID \d+\s*:\s*(.*)$")
	signal_pattern = re.compile(r"^Сигнал\s*:\s*(\d+)%")
	auth_pattern = re.compile(r"^Проверка подлинности\s*:\s*(.+)")
	encryption_pattern = re.compile(r"^Шифрование\s*:\s*(.+)")
	channel_pattern = re.compile(r"^Канал\s*:\s*(\d+)")
	radio_pattern = re.compile(r"^Тип радио\s*:\s*(.+)")

	networks = []
	current_network = {}

	for line in output.splitlines():
		line = line.strip()

		if ssid_match := ssid_pattern.search(line):
			if current_network:
				networks.append(current_network)
			current_network = {"SSID": ssid_match.group(1)}

		if signal_match := signal_pattern.search(line):
			current_network["Signal"] = int(signal_match.group(1))

		if auth_match := auth_pattern.search(line):
			current_network["Authentication"] = auth_match.group(1)

		if encryption_match := encryption_pattern.search(line):
			current_network["Encryption"] = encryption_match.group(1)

		if channel_match := channel_pattern.search(line):
			channel = int(channel_match.group(1))
			current_network["Channel"] = channel
			current_network["Band"] = "2.4 ГГц" if channel <= 14 else "5 ГГц"

		if radio_match := radio_pattern.search(line):
			current_network["Radio"] = radio_match.group(1)



	if current_network:
		networks.append(current_network)
	return networks

def parse_arguments():
	parser = argparse.ArgumentParser(description="Wi-Fi Network Scanner Tool")
	parser.add_argument('-t', '--timeout', type=int, default=10, help='Timeout duration between scans in seconds')
	parser.add_argument('-r', '--retries', type=int, default=5, help='Number of retries for scanning')
	return parser.parse_args()

def print_networks(networks):
	networks = sorted(networks, key=lambda n: n.get("Signal", 0), reverse=True)

	print(f"{'SSID':<20} {'Сигнал':>7} {'dBm':>5} {'Канал':>6} {'Диапазон':>9}")
	print("-" * 52)
	for net in networks:
		ssid = net.get("SSID") or "<скрытая>"
		signal = net.get("Signal", 0)
		dbm = signal // 2 - 100
		print(f"{ssid:<20} {signal:>6}% {dbm:>5} {net.get('Channel', '?'):>6} {net.get('Band', '?'):>9}")

def main():
	args = parse_arguments()

	for attempt in range(args.retries):
		print(f"\nСканнирование {attempt + 1}/{args.retries}")
		networks = scan_wifi()
		if networks:
			print_networks(networks)
		else:
			print("Сетей не найдено")
		if attempt < args.retries - 1:
			time.sleep(args.timeout)

	print("\nГотово")

if __name__ == "__main__":
	main()