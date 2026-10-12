import time
import threading
import msvcrt
from wi_fi_proj import scan_wifi
from signal_finder import draw_bar, signal_to_freq, signal_to_interval, kernel32

def choose_network():
	print("Сканирую эфир...")
	networks = scan_wifi()
	print(networks[0])
	networks = sorted(networks, key=lambda n: n.get("Signal", 0), reverse=True)
	for i , net in enumerate(networks, start=1):
		ssid = net.get("SSID") or "<скрытая>"
		print(f"{i:2}. {ssid:<20} {net.get('Signal', 0):3}% канал {net.get('Channel', '?')}")
	number = int(input("\nНомер сети: "))
	return networks[number - 1]

state = {"signal":None}

def scanner(bssid):
	while True:
		networks = scan_wifi()
		found = None
		for net in networks:
			if net.get("BSSID") == bssid:
				found = net.get("Signal")
		state["signal"] = found

def main():
	target = choose_network()
	name = target.get("SSID") or "<скрытая>"
	state["signal"] = target.get("Signal")

	thread = threading.Thread(target=scanner, args=(target.get("BSSID"),), daemon=True)
	thread.start()

	print(f"\nИщу {name}. Пробел — звук вкл/выкл, Ctrl+C — выход.\n")
	muted = False
	try:
		while True:
			if msvcrt.kbhit():
				key = msvcrt.getwch()
				if key == " ":
					muted = not muted

			signal = state["signal"]
			if signal is None:
				print(f"\r{name}: не вижу сеть...".ljust(60), end="", flush=True)
				time.sleep(1)
				continue
			label = name + (" [без звука]" if muted else " " * 12)
			draw_bar(label, signal)
			if not muted:
				kernel32.Beep(signal_to_freq(signal), 60)
			time.sleep(signal_to_interval(signal))
	except KeyboardInterrupt:
		print("\nГотово")

if __name__ == "__main__":
	main()

