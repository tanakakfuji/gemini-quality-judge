from pathlib import Path
import csv
import json
import os

def load_text(path):
  file_path = Path(__file__).parent.parent / path
  with open(file_path, encoding="utf-8") as f:
    return f.read()

def load_csv(path):
  file_path = Path(__file__).parent.parent / path
  with open(file_path, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    return list(reader)
  
def save_csv(data, dir_path, filename):
  os.makedirs(dir_path, exist_ok=True)
  file_path = Path(__file__).parent.parent / dir_path / filename
  with open(file_path, mode='w', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=',', doublequote=True, lineterminator="\r\n", quotechar='"')
    writer.writeheader()
    writer.writerows(data)

def save_json(data, dir_path, filename):
  os.makedirs(dir_path, exist_ok=True)
  file_path = Path(__file__).parent.parent / dir_path / filename
  with open(file_path, mode='w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
