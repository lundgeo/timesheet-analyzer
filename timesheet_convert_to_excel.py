import os

from pyexcel_ods3 import get_data
from pyexcel_xlsx import save_data

def main():
    print("check for and convert .ods to .xlsx ")
    for filename in os.listdir('.\input_files'):
        f = os.path.join('.\input_files', filename)
        if os.path.isfile(f) and f.endswith('.ods'):
            dataOds = get_data(f)
            save_data(f"{f[:-4]}.xlsx", dataOds)
            os.remove(f)

if __name__ == "__main__":
  main()