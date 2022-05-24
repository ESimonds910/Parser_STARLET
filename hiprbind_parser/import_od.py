import pandas as pd
import xlrd
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename


def header_check(columns):
    try:
        eln_headers = pd.read_excel("test_files/ELN_headers.xlsx", header=None)
    except FileNotFoundError:
        print("File not found")
        pass
    else:
        for column in columns:
            if column not in list(eln_headers[0]):
                print(f"'{column}' does not match SSF Database Nomenclature.")


def import_od(proj_data):
    # input_od_path = proj_data["od_file"]
    window = Tk()
    window.withdraw()
    od_data = pd.DataFrame()
    input_od_path = askopenfilename(title="Choose OD file.")
    if input_od_path:
        try:
            od_data = pd.read_excel(input_od_path, sheet_name="Growth Details")
        except FileNotFoundError:
            messagebox.showinfo(title="Uh oh...", message="Something's wrong. The OD file wasn't found.")
            pass
        except KeyError:
            try:
                od_data = pd.read_excel(input_od_path)
            except FileNotFoundError:
                messagebox.showinfo(title="Uh oh...", message="Something's wrong. The OD file wasn't found.")
                pass
        except ValueError:
            try:
                od_data = pd.read_csv(input_od_path)
            except FileNotFoundError:
                messagebox.showinfo(title="Uh oh...", message="Something's wrong. The OD file wasn't found.")
                pass
        except xlrd.XLRDError:
            try:
                od_data = pd.read_excel(input_od_path)
            except xlrd.XLRDError:
                od_data = pd.read_csv(input_od_path)
            except FileNotFoundError:
                messagebox.showinfo(title="Uh oh...", message="Something's wrong. The OD file wasn't found.")
                pass
        if not od_data.empty:
            try:
                for column in od_data.columns[1:]:
                    if " " in column:
                        new_column = column.strip().replace(" ", "_").lower().capitalize()
                    else:
                        new_column = column.strip().lower().capitalize()
                    od_data.rename(columns={column: new_column}, inplace=True)
                od_data.dropna(thresh=3, subset=od_data.columns[:-1], inplace=True)
                od_data.dropna(axis=1, how="all", inplace=True)
                col_header = "Od600"
                od_data[col_header] = od_data[col_header].replace(" ", "0.0")
                col_header = "Harvest_sample_id"
                od_data.set_index(col_header, drop=False, inplace=True)
            except KeyError:
                print(f"Parser was looking for column '{col_header}', but was not found. Check file for missing column.")
                pass
            finally:
                # header_check(od_data.columns)
                window.destroy()
                return od_data
        else:
            messagebox.showinfo(title="Uh oh...", message="Something's wrong, there is no OD data. Check OD File.")
            return "end"
    else:
        return "end"


if __name__ == "__main__":
    from time import time
    start_time = time()
    # ELN file path
    od_file_path = r"L:\Molecular Sciences\Small Scale Runs\SSF00609b Discrete Strain Screening (DSS) v1.5 Repeat of" \
                   r" old SSF00603 DSS reference sequence into 3 hosts 21C 44 hours\SSF00609b Discrete" \
                   r" Strain Screening (DSS) ELN v1.5.xlsm"

    # Old OD file path
    # od_file_path = "L:/Molecular Sciences/Small Scale Runs/SSF00607 Discrete Strain Screening (DSS) akita Compare " \
    #                "Chap hits side-by-side/Assays/OD/Processed/SSF00607 24DW OD.xlsx "

    import_od(od_file_path)
    end_time = time()
    run_time = end_time - start_time
    print(f"Run time: {run_time}")