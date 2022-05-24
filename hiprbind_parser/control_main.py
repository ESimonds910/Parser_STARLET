import pandas as pd
import json
import ipywidgets as ipw
import numpy as np
from time import time
from tkinter import Tk, messagebox
from IPython.display import display
from tkinter.filedialog import askopenfilename, askdirectory
from string import ascii_uppercase as upstr
from hiprbind_analysis import data_analysis
from hiprbind_dashboard import main
import hiprbind_parser.file_split as fs
from hiprbind_parser.import_csv import FileFinder
import hiprbind_parser.data_formatter as formatter
import hiprbind_parser.enspire_od_join as enspire_od_join

# This is the original file for calcs
# import hiprbind_parser.pt_calculations as pt_calculations

# This is the new file for calcs
from hiprbind_parser.calculations import Calculations as pt_calculations

from hiprbind_parser.import_od import import_od


class RunParser:
    def __init__(self):
        self.window = Tk()
        self.window.withdraw()
        self.ended = False
        self.proj_data_dict = {}
        self.run_parser_btn = ipw.Button(description='Run parser', button_style='info')
        self.run_parser_btn.on_click(self.run_main)
        display(self.run_parser_btn)

    def concat_projs(self, df):
        all_projs_df = pd.DataFrame()
        pass

    def run_main(self, event):
        proj_concat = False
        self.window = Tk()
        self.window.withdraw()
        try:
            with open(r"parser_data.json", "r") as parser_file:
                self.proj_data_dict = json.load(parser_file)
            # with open(r"C:\Users\esimonds\GitHub\Input-Parser-Form\parser_data.json", "r") as parser_file:
            #     self.proj_data_dict = json.load(parser_file)
        except FileNotFoundError:
            self.window.withdraw()
            messagebox.showinfo(title="Warning!", message="There's no file, did you complete the parser form?")
            self.ended = True
            self.window.destroy()
        else:
            if self.proj_data_dict == {}:
                self.window.withdraw()
                messagebox.showinfo(title="Warning!", message="The file appears to be empty. Complete the input form.")
                self.ended = True
                self.window.destroy()
            else:
                file_finder = FileFinder()

                self.proj_data_dict = fs.split_projects(self.proj_data_dict)
                if self.proj_data_dict != "end":
                    for proj, inner_dict in self.proj_data_dict.items():
                        project_title = proj
                        if "-" in proj:
                            inner_dict["proj_name"] = proj.split("-")[0]
                            inner_dict["ab_name"] = proj.split("-")[-1]
                        else:
                            inner_dict["ab_name"] = ""
                            inner_dict["proj_name"] = proj

                        proj_data = self.proj_data_dict[proj]

                        source_df = file_finder.data_finder(proj_data)

                        df_list = formatter.data_format(source_df, proj_data)

                        if proj_data["od_file"]:
                            raw_od = import_od(proj_data)
                            if isinstance(raw_od, pd.DataFrame):
                                joined_df_list = enspire_od_join.join_dfs(df_list, raw_od, proj_data)
                                main_join_dfs = joined_df_list[:2]
                                final_display_df = joined_df_list[2]
                                final_display_rep_df = joined_df_list[3]

                                # old code for original calcs
                                # completed_main_dfs = pt_calculations.make_calculations(main_join_dfs, proj_data)

                                # new code for calcs
                                completed_main_dfs = pt_calculations(main_join_dfs, proj_data).make_calculations()
                            else:
                                self.ended = True
                                break
                        else:
                            main_dfs = df_list[:2]
                            final_display_df = df_list[2]
                            final_display_rep_df = df_list[3]
                            # old code for original calcs
                            # completed_main_dfs = pt_calculations.make_calculations(main_dfs, proj_data)

                            # new code for calcs
                            completed_main_dfs = pt_calculations(main_dfs, proj_data).make_calculations()

                        final_main_df = completed_main_dfs[0]
                        final_main_rep_df = completed_main_dfs[1]

                        self.window.withdraw()
                        output_path = askdirectory(
                            title="Choose folder to place output file for " + project_title,
                            initialdir='L:/High Throughput Screening/HiPrBind/SSF HPB runs'
                        )

                        if output_path:
                            final_out_path = f"{output_path}/{project_title}_output.xlsx"
                            inner_dict["out_path"] = final_out_path
                            with pd.ExcelWriter(final_out_path) as writer:
                                final_main_df.to_excel(writer, sheet_name="Calculations")
                                final_display_df.to_excel(writer, sheet_name="Display_Ready")
                                final_main_rep_df.to_excel(writer, sheet_name="Rep_Calculations")
                                final_display_rep_df.to_excel(writer, sheet_name="Rep_Display_Ready")

                            self.window = Tk()
                            self.window.withdraw()
                            messagebox.showinfo(title="Congratulations!", message=f"Project {project_title} has been output.")

                    self.window.destroy()
                else:
                    self.ended = True
        
        if not self.ended:
            with open("parser_data.json", "w") as update_parser_file:
                json.dump(self.proj_data_dict, update_parser_file, indent=4)
            # data_analysis.DataAnalysis(self.proj_data_dict)
            main.BuildDashboard(self.proj_data_dict)


        # Also return these four dataframes into list?
        # clean_df, main_df, clean_rep_df, main_rep_df = test_formatter.data_format(source_df, proj_data)
        # df_list = [clean_df, main_df, clean_rep_df, main_rep_df]
        # dfs_return = join_dfs(df_list, raw_od, proj_data)
        #
        # clean_join_df = dfs_return[0]
        # main_join_df = dfs_return[1]
        # clean_rep_join_df = dfs_return[2]
        # main_rep_join_df = dfs_return[3]
        #
        # complete_df = eight_pt_calculations.make_calculations(main_join_df, proj_data)
        # complete_rep_df = eight_pt_calculations.make_calculations(main_rep_join_df, proj_data)
        #


if __name__ == "__main__":
    start_time = time()

    # Test 1 data
    proj_dict = {
        "SSF00Test": {
            "plates": [
                "P1-1",
                "P1-2"
                ],
            "points": 4,
            "volumes": [
                0.071428571,
                0.003401361,
                0.00016197,
                7.71284e-06
            ],
            "od_file": True,
            "std_conc": {
                "A11": 100.0,
                "B11": 50.0,
                "C11": 16.7,
                "D11": 5.6,
                "E11": 1.9,
                "F11": 0.6,
                "A12": 100.0,
                "B12": 50.0,
                "C12": 16.7,
                "D12": 5.6,
                "E12": 1.9,
                "F12": 0.6
            }
        }
    }
    try:
        with open(r"C:\Users\esimonds\GitHub\Input-Parser-Form\parser_data.json", "w") as parser_file:
            json.dump(proj_dict, parser_file, indent=4)
    except FileNotFoundError:
        messagebox.showinfo(title="Warning!", message="There's no file, did you complete the parser form?")

    RunParser()

    end_time = time()
    split = round(end_time - start_time, 2)
    print(f"Program runtime: {split}s")
