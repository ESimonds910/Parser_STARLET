import pandas as pd
import numpy as np
import ipywidgets as ipw
from IPython.display import display
from ipywidgets import Layout
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

STYLE = {"description_width": "initial"}


class DataAnalysis:
    def __init__(self, dict):
        self.parser_data_dict = dict
        self.proj_list = [proj for proj in self.parser_data_dict.keys()]
        self.proj_choice = ipw.Dropdown(options=self.proj_list)
        self.show_data_vis = ipw.Button(description="Show Visuals", button_style="info")
        self.data_vis = ipw.Output()
        self.chart_1_out = ipw.Output(layout={'border': '1px solid black'})
        self.chart_2_out = ipw.Output(layout={'border': '1px solid black'})
        self.chart_3_out = ipw.Output(layout={'border': '1px solid black'})
        self.vbox_data_vis = ipw.VBox([self.proj_choice, self.show_data_vis])
        self.choose_proj()
        self.show_data_vis.on_click(self.build_display)


    # def import_data(self):
    #     with open("parser_data.json") as parserfile:
    #         self.parser_data_dict = json.load(parserfile)

    def choose_proj(self):
        display(self.vbox_data_vis, self.chart_1_out, self.chart_2_out, self.chart_3_out)

    def build_display(self, event):
        # proj chosen from dropdown
        self.chart_1_out.clear_output()
        self.chart_2_out.clear_output()
        self.chart_3_out.clear_output()

        full_calcs_df = pd.DataFrame()
        full_display_df = pd.DataFrame()
        full_calcs_rep_df = pd.DataFrame()
        full_display_rep_df = pd.DataFrame()

        proj_name = self.proj_choice.value
        file_path = self.parser_data_dict[proj_name]["out_path"]
        calcs_df = pd.read_excel(file_path, index_col=0, sheet_name="Calculations")
        display_df = pd.read_excel(file_path, index_col=0, sheet_name="Display_Ready")
        calcs_reps_df = pd.read_excel(file_path, index_col=0, sheet_name="Rep_Calculations")
        display_reps_df = pd.read_excel(file_path, index_col=0, sheet_name="Rep_Display_Ready")

        full_calcs_df = pd.concat([full_calcs_df, calcs_df])
        full_display_df = pd.concat([full_display_df, display_df])

        full_calcs_rep_df = pd.concat([full_calcs_rep_df, calcs_reps_df])
        full_display_rep_df = pd.concat([full_display_rep_df, display_reps_df])

        stacked_calcs_df = pd.concat([full_calcs_df, full_calcs_rep_df])
        stacked_display_df = pd.concat([full_display_df, full_display_rep_df])

        stacked_display_df.dropna(subset=["Sample_type"], how='any', inplace=True)

        column_name = ipw.Dropdown(
            options=list(stacked_display_df.columns),
            description="Choose column to indicate color",
            style=STYLE,
            value='Plate'
        )

        plate_list = list(stacked_display_df["Plate"].unique())
        plate = ipw.Dropdown(
            options=plate_list,
            description="Choose a plate",
            style=STYLE,
            value=plate_list[0])

        corr_plate_list = list(stacked_display_df["Plate"].apply(lambda x: x.split('-')[0]).unique())
        corr_plate = ipw.Dropdown(
            options=corr_plate_list,
            description="Choose a plate",
            style=STYLE,
            value=corr_plate_list[0])

        def create_traces(column_name):
            try:
                rep_lines = px.line(stacked_display_df, x="Volumes", y="Alpha", facet_col="Col", facet_row="Row",
                                    color=column_name, line_group="Plate", log_x=True,
                                    height=800, width=1000, title=proj_name)
                rep_lines.update_xaxes(tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                rep_lines.update_yaxes(tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                rep_lines.update_traces(line=dict(width=0.8))

                rep_lines.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                rep_lines.show()
            except KeyError:
                print("\nChoose a different column! This one doesn't work.")
            except ValueError:
                print("\nChoose a different columns! These values don't look right.")

        with self.chart_1_out:
            display(ipw.HTML("<b>Please be patient while I load!</b>"))
            trace_plot = ipw.interactive(create_traces, column_name=column_name)
            display(trace_plot)

        def create_byplate_traces(plate):
            by_plate_df = stacked_display_df[stacked_display_df["Plate"] == plate]

            try:
                all_lines = px.line(by_plate_df, x="Volumes", y="Alpha", color='Sample_type', line_group="Well_Id",
                                    log_x=True,
                                    height=800, width=1000, title=f"{proj_name}: {plate}")
                all_lines.update_xaxes(tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                all_lines.update_yaxes(tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                all_lines.update_traces(line=dict(width=0.8))

                all_lines.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                all_lines.show()
            except KeyError:
                print("\nThis one doesn't work.")
            except ValueError:
                print("\nThese values don't look right.")

        with self.chart_2_out:
            trace_byplate_plot = ipw.interactive(create_byplate_traces, plate=plate)
            display(trace_byplate_plot)

        def check_replicates(corr_plate):
            corr_plate_df = stacked_display_df[stacked_display_df["Plate"].str.startswith(corr_plate)]
            sample_type = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)][
                "Sample_type"].values
            well_id = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)]["Well_Id"].values
            main_alpha = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)]["Alpha"].values
            rep_alpha = corr_plate_df[corr_plate_df["Plate"].str.contains("-2", case=False)]["Alpha"].values
            try:
                corr_plot = px.scatter(x=main_alpha, y=rep_alpha, color=sample_type)
                corr_plot.update_xaxes(title='Main', tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                corr_plot.update_yaxes(title='Replicate', tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                corr_plot.show()
                pcorr, pvalue = stats.pearsonr(main_alpha, rep_alpha)
                corr_coef_disp = ipw.HTML(f"<b>Correlation Coefficient:</b> {pcorr}, <b>p-value:</b> {pvalue}")
            except KeyError:
                print("\nThis one doesn't work.")
            except ValueError:
                print("\nThese values don't look right.")
            else:
                display(corr_coef_disp)

        with self.chart_3_out:
            corr_plate_plot = ipw.interactive(check_replicates, corr_plate=corr_plate)
            display(corr_plate_plot)
