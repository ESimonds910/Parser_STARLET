import csv
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
import tkinter.messagebox as messagebox


def split_projects(proj_dict):
    copy_start_row = 0
    copy_end_row = 0
    window = Tk()
    window.withdraw()

    file_path_raw = askopenfilename(title='Select file to copy', initialdir="L:/Assay Development/Enspire")
    if file_path_raw:
        for proj, inner_dict in proj_dict.items():
            proj_name = proj
            plate_num = len(inner_dict["plates"])
            try:
                folder_path_raw = askdirectory(
                    title="Choose Raw folder from Project folder to place file for " + proj_name,
                    initialdir='L:/High Throughput Screening/HiPrBind/SSF HPB runs'
                )
            except FileNotFoundError:
                pass
            else:
                if folder_path_raw:
                    with open(file_path_raw) as csv_file:
                        reader = csv.reader(csv_file)
                        copy_end_row += int(plate_num) * 48
                        plate_rows = [row for idx, row in enumerate(reader) if idx in range(copy_start_row, copy_end_row)]
                        copy_start_row = copy_end_row

                        raw_output = folder_path_raw + '/' + proj_name + '.csv'
                        with open(raw_output, 'w', newline="") as newFile:
                            csv_writer = csv.writer(newFile)
                            for row in plate_rows:
                                csv_writer.writerow(row)

                    inner_dict["raw_file"] = raw_output

                else:
                    file_path_raw = "end"
                    return file_path_raw

        messagebox.showinfo(title="Congrats!", message="File has been moved!")
        window.destroy()

        return proj_dict
    else:
        file_path_raw = "end"
        return file_path_raw


if __name__ == "__main__":
    print("This is only a test.")

