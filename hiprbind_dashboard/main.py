# import required packages to build dashboard
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# import packages required to build graphs
import plotly.graph_objects as go
import plotly.express as px

# import packages to create dataframes for data and statistical analysis
import pandas as pd
from scipy import stats
import json


class BuildDashboard:
    """
    This class is called by /hiprbind_parser/control_main.py, which is run after a button click from the input form.
    This class is used to visual the project(s) data output by the data parser.

    """
    def __init__(self, proj_dict):
        """

        :param proj_dict: This dictionary is passed into the function by the data parser, and contains
        the data input from the input form for each project entered.

        """
        # This line creates the Dash app and uses bootstrap to provide style to the visual layout.
        # external_stylesheets is not necessary for the success of the app, only dash.Dash()
        self.app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

        self.parser_data_dict = proj_dict

        # The following loop will import the outputted project(s) data, and create one dataframe
        # formatted for data visualization - all_stacked_df.
        self.all_stacked_df = pd.DataFrame()
        for proj, inner in self.parser_data_dict.items():
            self.file_path = inner["out_path"]
            self.full_display_df = pd.DataFrame()
            self.full_display_rep_df = pd.DataFrame()
            self.display_df = pd.read_excel(self.file_path, index_col=0, sheet_name="Display_Ready")
            self.display_reps_df = pd.read_excel(self.file_path, index_col=0, sheet_name="Rep_Display_Ready")
            self.full_display_df = pd.concat([self.full_display_df, self.display_df])
            self.full_display_rep_df = pd.concat([self.full_display_rep_df, self.display_reps_df])
            self.stacked_display_df = pd.concat([self.full_display_df, self.full_display_rep_df])

            self.stacked_display_df.dropna(subset=["Sample_type"], how='any', inplace=True)
            self.all_stacked_df = pd.concat([self.stacked_display_df, self.all_stacked_df])

        # This function is called once the dataframe is ready to create the interactive Dashboard
        self.build_display()

    def build_display(self):
        # The following are lists created that are used in the dropdown boxes displayed on the Dashboard.
        proj_options = [{'label': proj, 'value': proj} for proj in self.parser_data_dict]
        plate_options = [{'label': plate, 'value': plate} for plate in self.all_stacked_df["Plate"].unique()]
        column_options = [{'label': column, 'value': column} for column in self.all_stacked_df.columns]
        corr_plate_options = [{'label': corr_plate,
                               'value': corr_plate} for corr_plate in self.all_stacked_df["Plate"].apply(lambda x: x.split('-')[0]).unique()]
        # The following uses core components and html components contained within the dash package
        # This section creates and formats the visual look of the Dashboard.
        self.app.layout = html.Div([
            html.Div([
                dcc.Markdown(id='graph-1-heading', children=f"# Data Analysis for Projects")],
                style={'color': 'black', 'margin': '50px 0px 50px 20px'}),

            # dcc.Store allows storage of dataframe filtered by a project
            dcc.Store(id='proj-output'),
            dcc.Dropdown(id='proj-picker', options=proj_options, value=list(self.parser_data_dict.keys())[0]),

            html.Hr(),

            html.Div([
                dcc.Dropdown(id='plate-picker',
                             options=plate_options,
                             value=self.all_stacked_df["Plate"].unique()[0],
                             style={'margin': '0px 20px', 'width':'50%'}),
                dcc.Graph(id='graph')
            ]),

            html.Hr(),

            html.Div([
                dcc.Dropdown(id='column-picker',
                             options=column_options,
                             value="Plate",
                             style={'margin': '0px 20px', 'width':'50%'}),
                dcc.Graph(id='graph2')
            ]),

            html.Hr(),

            html.Div([
                dcc.Dropdown(id='rep-picker',
                             options=corr_plate_options,
                             value="P1",
                             style={'margin': '0px 20px', 'width':'50%'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Div(dcc.Graph(id='graph3'),
                                     className='graph-corr-box col-lg-6')
                        ]),
                        dbc.Col([
                            html.Div(html.P(id='corr-output',
                                            className='graph-corr-box col-lg-6',
                                            style={'margin': '300px auto 100px 0px',
                                                   'textAlign':'left'}))
                        ])
                    ])
                ], style={'width':'100%'})

            ])

        ], style={'marginLeft': '20px'})

        # The next section allows for the interactivity of the Dashboard. @app.callback will receive dashboard inputs
        # pass the inputs into the function below, and return the desired output information
        @self.app.callback(Output(component_id='proj-output', component_property='data'),
                           [Input(component_id='proj-picker', component_property='value')])
        def picked_proj(selected_proj):
            """

            :param selected_proj: receives user selected project from the dashboard dropdown
            :return: A filtered dataframe based on the chosen project
            """
            filtered_proj_df = self.all_stacked_df[self.all_stacked_df["SSF_exp"] == selected_proj]
            return filtered_proj_df.to_dict('records')

        @self.app.callback(Output(component_id='graph', component_property='figure'),
                           [Input(component_id='proj-output', component_property='data'),
                            Input(component_id='plate-picker', component_property='value')])
        def update_figure(data, selected_plate):
            """

            :param data: receives stored, filtered dataframe from selected project
            :param selected_plate: receives plate selected for analysis on first graph
            :return: a graph based on the selected data
            """
            if data is None:
                raise PreventUpdate

            # dict data is converted to df for plotly graph
            df = pd.DataFrame.from_dict(data)

            # df is filtered by dropdown user selected plate
            by_plate_df = df[df["Plate"] == selected_plate]
            proj_name = df["SSF_exp"].unique()[0]

            # graph is built for display
            traces = px.line(x=by_plate_df["Volumes"],
                    y=by_plate_df["Alpha"],
                    color=by_plate_df['Sample_type'],
                    line_group=by_plate_df["Well_Id"],
                    log_x=True,
                    height=800, width=800, title=f"{proj_name}: {selected_plate}")
            traces.update_xaxes(title='Log Volumes: log(ul)',
                                rangemode='tozero',
                                zeroline=True,
                                zerolinecolor='grey',
                                showline=True,
                                linewidth=1,
                                linecolor='grey')
            traces.update_yaxes(title='Alpha',
                                rangemode='tozero',
                                zeroline=True,
                                zerolinecolor='grey',
                                showline=True,
                                linewidth=1,
                                linecolor='grey')
            traces.update_traces(mode="markers+lines")
            traces.update_layout(legend_title="Sample Type")
            fig = go.Figure(traces)

            return fig

        @self.app.callback(Output(component_id='graph2', component_property='figure'),
                     [Input(component_id='proj-output', component_property='data'),
                      Input(component_id='column-picker', component_property='value')])
        def update_traces(data, selected_column):
            """

            :param data: receives stored, filtered dataframe from selected project
            :param selected_column: receives column selected for analysis on second graph with all traces
            :return: facet grid graph that displays traces based on desired selected dropdown
            """
            if data is None:
                raise PreventUpdate
            df = pd.DataFrame(data)
            try:
                proj_name = df["SSF_exp"].unique()[0]
                # graph is built for display
                traces = px.line(df,
                                 x="Volumes",
                                 y="Alpha",
                                 facet_col="Col",
                                 facet_row="Row",
                                 color=selected_column,
                                 line_group="Plate",
                                 log_x=True,
                                 height=800, width=1200,
                                 title=proj_name)
            # the following is error handling meant catch invalid column selected from dropdown; empty graph will
            # be displayed
            except ValueError:
                fig = go.Figure()
                return fig
            except AttributeError:
                fig = go.Figure()
                return fig
            else:
                # if there are now issues with graph, the following format adjustments are made for aesthetics
                traces.update_xaxes(tickangle=45,
                                    tickfont=dict(size=8),
                                    title_font=dict(size=10),
                                    showline=True,
                                    linecolor='grey')
                traces.update_yaxes(tickangle=45,
                                    tickfont=dict(size=8),
                                    title_font=dict(size=10),
                                    showline=True,
                                    linecolor='grey')
                traces.update_traces(line=dict(width=0.8))
                traces.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                fig = go.Figure(traces)
                return fig

        @self.app.callback([Output(component_id='graph3', component_property='figure'),
                            Output(component_id='corr-output', component_property='children')],
                           [Input(component_id='proj-output', component_property='data'),
                            Input(component_id='rep-picker', component_property='value')])
        def corr_analysis(data, corr_plate):
            """

            :param data: receives stored, filtered dataframe from selected project
            :param corr_plate: receives plate selected for replicate analysis on third graph
            :return: scatter plot graph based on selected source plate; also pearson correlation value and p-value
            for display
            """
            if data is None:
                raise PreventUpdate
            df = pd.DataFrame(data)
            corr_plate_df = df[df["Plate"].str.startswith(corr_plate)]
            # the dataframe here is filtered to create separate df for main data and replicate data
            sample_type = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)][
                "Sample_type"].values
            well_id = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)]["Well_Id"].values
            main_alpha = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)]["Alpha"].values
            rep_alpha = corr_plate_df[corr_plate_df["Plate"].str.contains("-2", case=False)]["Alpha"].values
            proj_name = df["SSF_exp"].unique()[0]
            try:
                # graph is built to analysis main data against replicate data
                corr_plot = px.scatter(x=main_alpha,
                                       y=rep_alpha,
                                       color=sample_type,
                                       width=800,
                                       height=800,
                                       title=f"{proj_name}: {corr_plate}")
            # empty graph and correlation value returned if the selected plate has no replicate data to compare
            except ValueError:
                fig = go.Figure()
                corr_value = "No correlation"
                return fig, corr_value

            else:
                corr_plot.update_xaxes(title='Main',
                                       tickangle=45,
                                       tickfont=dict(size=8),
                                       showline=True,
                                       linecolor='grey')
                corr_plot.update_yaxes(title='Replicate',
                                       tickangle=45,
                                       tickfont=dict(size=8),
                                       showline=True,
                                       linecolor='grey')
                corr_plot.update_layout(legend_title="Sample Type")
                fig = go.Figure(corr_plot)

                pcorr, pvalue = stats.pearsonr(main_alpha, rep_alpha)
                corr_value = f"Correlation: {str(round(pcorr, 4))}  |  p-value: {str(round(pvalue, 4))}"
                return fig, corr_value

        # this code is required to run the app and dashboard - app is run only on local server
        self.app.run_server(
            debug=False,
            use_reloader=False
        )


if __name__ == "__main__":
    with open("../parser_data.json", "r") as update_parser_file:
        proj_data_dict = json.load(update_parser_file)

    BuildDashboard(proj_data_dict)