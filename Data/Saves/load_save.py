from json_loader import load_json
import os

def load_save(save_slot = 0):
	save_file = f'Save_{save_slot}.json'
	if os.path.exists(save_file):
		return load_json(save_file)
	else:
		print(f"error, there is no file under save slot {save_slot}.")