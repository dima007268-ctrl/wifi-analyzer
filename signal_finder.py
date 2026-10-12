import re 
import time 
from run_modul import my_run
from my_ctypes import my_windll

kernel32 = my_windll.kernel32	

ssid_pattern = re.compile(r"^SSID\s*:\s*(.*)$")
signal_pattern = re.compile(r"^Сигнал\s*:\s*(\d+)%")


def get_current_signal():
	result = my_run(["netsh", "wlan", "show", "interfaces"], capture_output=True, encoding="cp866")
	ssid = None
	signal = None
	for line in result.stdout.splitlines():
		line = line.strip()
		if m := ssid_pattern.search(line):
			ssid = m.group(1)
		if m := signal_pattern.search(line):
			signal = int(m.group(1))
	return ssid, signal

def signal_to_interval(signal):
	return 1.5 - signal / 100 * 1.4

def signal_to_freq(signal):
	return 400 + signal * 10

#сигнал   0% ─────────────── 100%
#пауза  1.5 с ────────────── 0.1 с
#звук   400 Гц ───────────── 1400 Гц


def draw_bar(ssid,signal):
	filled = signal // 5 
	bar = "█" * filled + "░" * (20 - filled)
	dbm = signal // 2 - 100
	print(f"\r{ssid} {bar} {signal:3}% {dbm} dBm", end="", flush= True)

def main():
	print("Поиск лучшего места. Ходи с ноутбуком. Ctrl + C выход. \n")
	try:
		while True:
			ssid, signal = get_current_signal()
			if signal is None:
				print("\r Не подключен к Wi-Fi....".ljust(60), end="", flush= True)
				time.sleep(1)
				continue
			draw_bar(ssid, signal)
			kernel32.Beep(signal_to_freq(signal), 60)
			time.sleep(signal_to_interval(signal))
	except KeyboardInterrupt:
		print("\nГотово")

if __name__ == "__main__":
	main()
