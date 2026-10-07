import ctypes
import time
from ctypes import wintypes

class GUID(ctypes.Structure):
	_fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]

class WLAN_INTERFACE_INFO(ctypes.Structure):
	_fields_ = [
        ("InterfaceGuid", GUID),
        ("strInterfaceDescription", wintypes.WCHAR * 256),
        ("isState", wintypes.DWORD),
    ]


class WLAN_INTERFACE_INFO_LIST(ctypes.Structure):
    _fields_ = [
        ("dwNumberOfItems", wintypes.DWORD),
        ("dwIndex", wintypes.DWORD),
        ("InterfaceInfo", WLAN_INTERFACE_INFO * 1),
    ]

from my_ctypes import my_windll
wlanapi = my_windll.wlanapi


def trigger_scan(wait = 8):

	client_handle = wintypes.HANDLE()
	negotiated_version = wintypes.DWORD()

	result = wlanapi.WlanOpenHandle(2, None, ctypes.byref(negotiated_version), ctypes.byref(client_handle))
	if result != 0:
		print("Не удалось подключиться к службе Wi-FI, код", result)
		return False

	try:
		iface_list = ctypes.POINTER(WLAN_INTERFACE_INFO_LIST) ()
		result = wlanapi.WlanEnumInterfaces(client_handle, None, ctypes.byref(iface_list))
		if result != 0:	
			print("Не удалось получить адаптер код:", result)
			return False
		try:
			if iface_list.contents.dwNumberOfItems == 0:
				print("Wi-FI адаптер не найден")
				return False
			
			first = iface_list.contents.InterfaceInfo[0]
			result = wlanapi.WlanScan(client_handle, ctypes.byref(first.InterfaceGuid), None, None, None)
			if result != 0:
				print("Сканирование не удалось, код:", result)
				return False
		finally:
			wlanapi.WlanFreeMemory(iface_list)
	finally:
		wlanapi.WlanCloseHandle(client_handle, None)

	time.sleep(wait)
	return True

if __name__ == "__main__":
	print("Сканирую...")
	print("Успешно:", trigger_scan)