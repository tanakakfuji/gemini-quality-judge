from pathlib import Path
import csv

def load_text(path):
  file_path = Path(__file__).parent.parent / path
  with open(file_path, encoding="utf-8") as f:
    return f.read()

def load_csv(path):
  file_path = Path(__file__).parent.parent / path
  with open(file_path, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    return list(reader)
