import ipywidgets as ipw
from IPython.display import display
from ipywidgets import Layout
import plotly.express as px
from string import ascii_uppercase as upstr
import json

STYLE = {'description_width': 'initial'}


class DisplayImage:
    img_path = open('AbSciImg.jfif', 'rb')
    img = img_path.read()
    display(ipw.Image(value=img, format='jfif', height='200px', width='200px'))


class InputForm:

    def __init__(self):
        self.proj_dict = {}
        self.std_dict_all = {}
        with open('parser_data.json', 'w') as parser_file:
            json.dump(self.proj_dict, parser_file, indent=4)
        self.proj_name = ipw.Text(placeholder="e.g. SSFXXXXX or SOMXXXXX")
        self.point_choice = ipw.Dropdown(options=[('Four', 4), ('Eight', 8)])
        self.plates = ipw.Text(placeholder="e.g. P1, P2 or P1-1, P1-2, P2")
        self.d_vols = ipw.Text(placeholder="e.g. 2, 1, 0.5, 0.25 or 2 1 0.5 0.25")
        self.check = ipw.Checkbox(indent=False)

        self.loc = ipw.Dropdown(options=["Column", "Row"])
        self.well_loc = ipw.Text(placeholder="e.g. A11 or G01")
        self.std_conc = ipw.Text(placeholder="e.g. 100, 50, 25 or 100 50 25")
        self.add_stc_button = ipw.Button(description='Add Standard', button_style='info')
        self.stc_out = ipw.Output(layout={'border': '1px solid black'})
        # self.display_standard()
        self.add_stc_button.on_click(self.add_standard)
        self.vbox_stc_result = ipw.VBox([self.add_stc_button, self.stc_out])

        self.button_update = ipw.Button(
            description='Add Project',
            button_style='info'
        )
        self.output = ipw.Output(layout={'border': '1px solid black'})
        self.button_update.on_click(self.on_button_click)
        self.vbox_result = ipw.VBox([self.button_update, self.output])

        self.display_inputs()

    def display_inputs(self):
        display(
            ipw.Label("Enter project name:"),
            self.proj_name,
            ipw.Label("Enter plate ids for project:"),
            self.plates,
            ipw.Label("Choose four or eight point dilution scheme:"),
            self.point_choice,
            ipw.Label("Enter dilution volumes:"),
            self.d_vols,
            ipw.Label("Check box to indicate if OD file is required:"),
            self.check,

            ipw.Label(f"{'-' * 100}"),
            ipw.HTML(value="<h4><b>*** Add Standard information here: enter replicates separately ***</b></h4>"),
            ipw.Label("Is the standard curve in a row or a column:"),
            self.loc,
            ipw.Label("Enter the location of first well used:"),
            self.well_loc,
            ipw.Label("Enter the standard curve concentrations- match first listed concentration with indicated well"),
            self.std_conc,
            self.vbox_stc_result,
            ipw.HTML(value="<h5><b>Check inputs for accuracy and add."
                           " Enter new details for multiple projects or run parser.</b></h5>"),
            self.vbox_result
        )

    def on_button_click(self, event):
        self.stc_out.clear_output()
        self.output.clear_output()
        all_valid = True
        with open('parser_data.json', 'r') as parser_file:
            proj_dict_all = json.load(parser_file)

        proj = self.proj_name.value
        if proj == "":
            fix_proj = "This field cannot be blank."
            all_valid = False
        else:
            fix_proj = "No issues"
        point = self.point_choice.value

        if ',' in self.plates.value:
            plate_ids = list(map(str.strip, self.plates.value.upper().split(',')))
        else:
            plate_ids = list(map(str.strip, self.plates.value.upper().split()))

        if self.plates.value == "":
            fix_plate = "This field cannot be blank."
            all_valid = False
        else:
            fix_plate = "No issues"
            for plate in plate_ids:
                valid_list = [False for char in plate if char not in 'p P 1 2 3 4 5 6 7 8 9 0 -'.split()]
                if False in valid_list:
                    fix_plate = f"Something doesn't match in plate {plate}"
                    all_valid = False
                    break
                else:
                    if plate[:1].upper() == "P":
                        if plate[-1] == '-':
                            fix_plate = "Add replicate number."
                            all_valid = False
                            break
                        elif "P" in plate[1:] or len(plate) < 2 or not isinstance(int(plate[1]), int) or not isinstance(int(plate[-1]), int):
                            fix_plate = f"Second or last character in {plate} is not an integer"
                            all_valid = False
                            break
                        elif len(plate) > 3:
                            if "-" in plate:
                                fix_plate = "No issues"
                            else:
                                fix_plate = "Specify replicate plate with '-'," \
                                            " e.g. P1 for non-replicate, or P1-1, P1-2 for replicates."
                                all_valid = False
                                break
                        else:
                            fix_plate = 'No issues'
                    else:
                        fix_plate = "Please write in following format: P1, P2 for plates, or P1-1, P1-2 for replicate plates."
                        all_valid = False
                        break

        if ',' in self.d_vols.value:
            dvs = self.d_vols.value.split(',')
        else:
            dvs = self.d_vols.value.split()

        try:
            d_volumes = [float(x) for x in dvs]
        except ValueError:
            fix_vols = "Please use a valid number for dilution volumes"
            all_valid = False
        else:
            if len(d_volumes) != self.point_choice.value:
                fix_vols = "Please use the same number of volumes as points indicated - 4 or 8 points."
                all_valid = False
            else:
                fix_vols = "No issues"

        if all_valid:
            self.proj_dict = {proj: {
                'plates': plate_ids,
                'points': point,
                'volumes': d_volumes,
                'od_file': self.check.value,
                'std_conc': self.std_dict_all
            }
            }
            proj_dict_all.update(self.proj_dict)

            with open('parser_data.json', 'w') as parser_file:
                json.dump(proj_dict_all, parser_file, indent=4)

            self.std_dict_all = {}

            with self.output:
                display(ipw.HTML("<h4><b>*** Project Updated ***</b></h4>"))
                # print('***  Project Updated  ***')
                for proj, inner in proj_dict_all.items():
                    p_name_text = ipw.HTML(f"<span style='color: #7EAA31';><b>Project name entered:</b></span> {proj}")
                    p_id_text = ipw.HTML(f"<span style='color: #7EAA31';><b>Plate Ids:</b></span> {', '.join(inner['plates'])}")
                    points_text = ipw.HTML(f"<span style='color: #7EAA31';><b>Point Scheme:</b></span> {inner['points']}")
                    dv_text = ipw.HTML(f"<span style='color: #7EAA31';><b>Dilution Volumes:</b></span> {', '.join([str(x) for x in inner['volumes']])}")
                    od_text = ipw.HTML(f"<span style='color: #7EAA31';><b>Add OD data:</b></span> {inner['od_file']}")
                    std_text = ipw.HTML("<span style='color: #7EAA31';><b>Standards:</b></span>")
                    display_box = ipw.VBox([p_name_text, p_id_text, points_text, dv_text, od_text, std_text])
                    display(display_box)
                    for key, value in inner['std_conc'].items():
                        labels = ipw.HTML(f"<ul><li style='line-height:1px';><span style='color: #7EAA31';><b>Well ID:</b></span>"
                                          f" {key}, <span style='color: #7EAA31';><b>Standard Concentration:</b></span>"
                                          f" {value}</li></ul>")
                        display(labels)
            #             for key, value in inner.items():
            #                 print(f'{key} entered: {value}\n')
            return self.std_dict_all
        else:
            with self.output:
                display(ipw.HTML("<h4><u><b>Please resolve the issues listed below!</b></u></h4>"))
                if fix_proj == "No issues":
                    display(ipw.HTML(f"<b>Project name: <font color='green'>{fix_proj}</b>"))
                else:
                    display(ipw.HTML(f"<b>Project name: <font color='red'>{fix_proj}</b>"))
                if fix_plate == "No issues":
                    display(ipw.HTML(f"<b>Plate IDs: <font color='green'>{fix_plate}</b>"))
                else:
                    display(ipw.HTML(f"<b>Plate IDs: <font color='red'>{fix_plate}</b>"))
                if fix_vols == "No issues":
                    display(ipw.HTML(f"<b>Dilution Volumes: <font color='green'>{fix_vols}</b>"))
                else:
                    display(ipw.HTML(f"<b>Dilution Volumes: <font color='red'>{fix_vols}</b>"))

    def add_standard(self, event):
        self.stc_out.clear_output()
        all_valid = True

        if self.well_loc.value[:1].upper() not in "ABCDEFGH":
            fix_well = f"{self.well_loc.value[:1].upper()} is invalid. Please fix."
            all_valid = False
        elif len(self.well_loc.value[1:]) != 2:
            fix_well = f"Please enter valid column number between 01 and 12."
            all_valid = False
        elif self.well_loc.value[1:] not in [f"{y}".zfill(2) for y in range(1, 13)]:
            fix_well = f"Please enter valid column number between 01 and 12. Remember, for numbers < 10, use 01 format."
            all_valid = False
        else:
            fix_well = "No issues"

        if ',' in self.std_conc.value:
            stc_list = self.std_conc.value.split(',')
        else:
            stc_list = self.std_conc.value.split()

        try:
            std_conc_list = [float(x) for x in stc_list]
            fix_conc = "No issues"
        except ValueError:
            fix_conc = "Valid number was not added. Check input values."
            all_valid = False

        if all_valid:
            std_conc_list_len = len(std_conc_list)
            if self.loc.value == 'Column':
                col_letter = self.well_loc.value[:1]
                letter_idx = upstr.index(col_letter)
                col_num = self.well_loc.value[1:]
                std_ids = [f"{upstr[letter]}{str(col_num).zfill(2)}" for letter in range(letter_idx, std_conc_list_len)]
                std_dict = (dict(zip(std_ids, std_conc_list)))

            elif self.loc.value == 'Row':
                row_letter = self.well_loc.value[:1]
                row_num = int(self.well_loc.value[1:])
                std_ids = [f"{row_letter}{str(num).zfill(2)}" for num in range(row_num, row_num + std_conc_list_len)]
                std_dict = dict(zip(std_ids, std_conc_list))
            try:
                self.std_dict_all.update(std_dict)
            except AttributeError:
                std_dict_all = {}
                std_dict_all.update(std_dict)
            else:
                with self.stc_out:
                    display(ipw.HTML("<h4><b>*** Standard Updated ***</b></h4>"))
                    for key, value in self.std_dict_all.items():
                        labels = ipw.HTML(
                            f"<ul><li style='line-height:1px';><span style='color: #7EAA31';><b>Well ID:</b></span>"
                            f" {key}, <span style='color: #7EAA31';><b>Standard Concentration:</b></span>"
                            f" {value}</li></ul>")
                        display(labels)
                    display(ipw.HTML("<b>To add replicate, change well id, or 'column/row' to indicate new standard curve position.</b>"))
                return self.std_dict_all
        else:
            with self.stc_out:
                title = ipw.HTML("<h4><u><b>Please resolve the issues listed below!</b></u></h4>")
                display(title)
                if fix_well == "No issues":
                    display(ipw.HTML(f"<b>Well ID: <font color='green'>{fix_well}</b>"))
                else:
                    display(ipw.HTML(f"<b>Well ID: <font color='red'>{fix_well}</b>"))
                if fix_conc == "No issues":
                    display(ipw.HTML(f"<b>Standard concentrations: <font color='green'>{fix_conc}</b>"))
                else:
                    display(ipw.HTML(f"<b>Standard concentrations: <font color='red'>{fix_conc}</b>"))
