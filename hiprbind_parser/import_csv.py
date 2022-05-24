import pandas as pd
import pandas.errors as pderrors
import numpy as np
import json
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename

PLATE_IDX = [x for x in range(25)]
DNA_PLATE_IDX = [x for x in range(24, 49)]


def file_import(input_raw_path, section, count):
    if section == "alpha":
        row_skip = 7
        index = PLATE_IDX
    else:
        row_skip = 31
        index = DNA_PLATE_IDX
    try:
        df = pd.read_csv(
            input_raw_path,
            header=None,
            index_col=0,
            names=index,
            usecols=np.arange(0, 25),
            skiprows=row_skip + count * 48,
            nrows=16,
            encoding='unicode_escape'
        )
    except pderrors.ParserError:
        messagebox.showinfo(title="Hang on...", message="Raw file is not in typical format. Please check.")
    else:
        return df


class FileFinder:

    def __init__(self):
        self.window = Tk()
        self.window.withdraw()
        self.window.destroy()
        self.all_data = pd.DataFrame()

    def data_finder(self, proj_data):
        plates = proj_data["plates"]
        input_raw_path = proj_data["raw_file"]

        all_alpha_data = pd.DataFrame()
        all_dna_data = pd.DataFrame()

        for plate in plates:
            plate_idx = plates.index(plate)
            new_alpha_data = file_import(input_raw_path, "alpha", plate_idx)
            new_dna_data = file_import(input_raw_path, "dna", plate_idx)
            if new_alpha_data.empty or new_dna_data.empty:
                messagebox.showinfo(
                    title="Hang on...",
                    message="The raw file may be empty, or raw path was not indicated."
                )
                break
            else:
                # new_alpha_data.insert(0, "Plate", plate)
                # new_alpha_data.insert(1, "Source", plate[:2])
                all_alpha_data = pd.concat([all_alpha_data, new_alpha_data])
                all_dna_data = pd.concat([all_dna_data, new_dna_data])

        return self.concat_alpha_dna(all_alpha_data, all_dna_data)

    def concat_alpha_dna(self, all_alpha_data, all_dna_data):
        self.all_data = pd.concat([all_alpha_data, all_dna_data], axis=1)

        return self.all_data


if __name__ == "__main__":
    try:
        with open("../modules/archive_json_test.json") as test_file:
            test_data = json.load(test_file)["SSF00616"]
    except Exception as e:
        print(f"{e.__class__} occurred. Pick new project.")
    else:
        plate_ids = test_data["Plate IDs"]
        raw_path = test_data["raw_file_path"]
        FileFinder().data_finder(plate_ids, raw_path)
