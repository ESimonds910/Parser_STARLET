import pandas as pd
import numpy as np

class Calculations:
    def __init__(self, df_package, proj_data):
        self.df_package = df_package
        self.proj_data = proj_data
        self.dv = proj_data["volumes"]
        self.points = proj_data["points"]
        self.signals = ["Alpha", "DNA"]

    def add_qc_flag(self, data):
        data["QC_Flag"] = np.where(data["Alpha.Max.Slope"] == 0, "Less than LOQ", "Pass")
        return data
    
    def data_clean_up(self, data):
        data.drop(['Fold_1', 'QC_Flag_1', 'Fold_2', 'QC_Flag_2', 'Fold_3', 'QC_Flag_3'], axis=1, inplace=True)
        return data
    
    def get_max_slope(self, data):
        # last_slope = 3
        # max_slope = data.loc[:, f"Alpha_slope_1": f"Alpha_slope_{last_slope}"].max(axis=1)
        # conditions = [
        #     ,
        #     (data[["QC_Flag_1", "QC_Flag_2", "QC_Flag_3"]].any() == "Pass")
        # ]
        # values = [0, data[[f"Alpha_slope_1", "Alpha_slope_2", f"Alpha_slope_3"]].max(axis=1)]
        data[f"Alpha.Max.Slope"] = data[[f"QC_Flag_1", "QC_Flag_2", f"QC_Flag_3"]].max(axis=1)
        data[f"DNA.Max.Slope"] = data.loc[:, f"DNA_slope_1": f"DNA_slope_3"].max(axis=1)
        return data

    def make_calculations(self):
        # for df, data in self.df_package.items():
            # if (df == "main_df" or df == "main_df_rep") and not data.empty:
        updated_dfs = []
        for data in self.df_package:
            for signal in self.signals:
                for n in range(1, int(self.points)):
                    numerator = (data[f"{signal}_{n + 1}"] - data[f"{signal}_{n}"])
                    denominator = (self.dv[n] - self.dv[n - 1])
                    fold = (data[f"{signal}_{n}"]/ data[f"{signal}_{n + 1}"])
                    # print(fold)
                    calced_slope = f"{signal}_slope_{n}"
                    
                    data[calced_slope] = round(numerator / denominator, 2)
                    if signal == "Alpha":
                        data[f"Fold_{n}"] = fold
                        data[f"QC_Flag_{n}"] = np.where(fold >= 2, round(numerator / denominator, 2), 0)
                    # data[calced_slope] = np.where(abs((data[f"{signal}_{n + 1}"] / data[f"{signal}_{n}"])).astype(int) >= 2, round(numerator / denominator, 2), 0)
                    # data[calced_slope] = 0

                # if self.points == 8:
                #     last_slope = 4
                # else:
                #     last_slope = 3

                # data[f"{signal}.Max.Slope"] = data.loc[:, f"{signal}_slope_1": f"{signal}_slope_{last_slope}"].max(axis=1)

            calced_data = self.get_max_slope(data)
            cleaned_data = self.data_clean_up(calced_data)
            final_data = self.add_qc_flag(cleaned_data)

            # data["HPB_DNA"] = round(data["Alpha.Max.Slope"] / data["DNA.Max.Slope"], 2)

            # if self.proj_data["od_file"]:
            #     data["OD 600 (AU)"] = data["OD 600 (AU)"].apply(lambda x: round(float(x), 2) if x != "" else "0.0")
            #     data["HPB_OD"] = round(data["Alpha.Max.Slope"] / data["OD 600 (AU)"], 2)

            # self.df_package[df] = final_data
            updated_dfs.append(final_data)
        return updated_dfs


if __name__ == "__main__":
    from raw_import import FileFinder
    from od_import import ODImport
    from raw_restructure import RawRestructure
    from raw_od_stitch import StitchRawOD

    test_data = dict(
        proj_name="SSF007-LS",
        plates=["38", "39"],
        ab_name="test_name",
        points=4,
        std_conc={
            "A1": 60,
            "B1": 30,
            "C1": 10,
            "D1": 3.33,
            "E1": 1.11,
            "F1": 0.33
        },
        od_file="test",
        test_file=r"L:\High Throughput Screening\HiPrBind\Benchling_Parser_Test\hpb_parser-main\test\single_project_test\SSF00test_OD.csv",
        volumes=[0.214285714, 0.011278195, 0.000593589, 3.12415E-05],
        raw_file=r"L:\High Throughput Screening\HiPrBind\Benchling_Parser_Test\hpb_parser-main\test\single_project_test\SSF805-RecRec.csv"
    )
    test_data_rep = dict(
        proj_name="SSF007-LS",
        plates=["38-1", "38-2"],
        ab_name="test_name",
        points=4,
        std_conc={
            "A1": 60,
            "B1": 30,
            "C1": 10,
            "D1": 3.33,
            "E1": 1.11,
            "F1": 0.33
        },
        od_file="test",
        test_file=r"L:\High Throughput Screening\HiPrBind\Benchling_Parser_Test\hpb_parser-main\test\single_project_test\SSF00test_OD.csv",
        volumes=[0.214285714, 0.011278195, 0.000593589, 3.12415E-05],
        raw_file=r"L:\High Throughput Screening\HiPrBind\Benchling_Parser_Test\hpb_parser-main\test\single_project_test\SSF805-RecRec.csv"
    )
    source_data = FileFinder(test_data).data_finder()
    restructured_data = RawRestructure(test_data['proj_name'], test_data, source_data).data_format()
    od_data = ODImport(test_data).format_od()
    stitched_data = StitchRawOD(restructured_data, od_data, test_data).stitch_dfs()
    calced_data = Calculations(stitched_data, test_data).make_calculations()

    with pd.ExcelWriter(r"L:\High Throughput Screening\HiPrBind\Benchling_Parser_Test\hpb_parser-main\test\single_project_test\test_calced_data2.xlsx") as writer:
        calced_data["main_df"].to_excel(writer, sheet_name="Calculations")
        calced_data["display_df"].to_excel(writer, sheet_name="Display_Ready")
        calced_data["main_df_rep"].to_excel(writer, sheet_name="Rep_Calculations")
        calced_data["display_df_rep"].to_excel(writer, sheet_name="Rep_Display_Ready")

    source_data = FileFinder(test_data_rep).data_finder()
    restructured_data = RawRestructure(test_data['proj_name'], test_data_rep, source_data).data_format()
    od_data = ODImport(test_data_rep).format_od()
    stitched_data = StitchRawOD(restructured_data, od_data, test_data_rep).stitch_dfs()
    calced_data = Calculations(stitched_data, test_data_rep).make_calculations()


    with pd.ExcelWriter(r"L:\High Throughput Screening\HiPrBind\Benchling_Parser_Test\hpb_parser-main\test\single_project_test\test_calced_data_reps2.xlsx") as writer:
        calced_data["main_df"].to_excel(writer, sheet_name="Calculations")
        calced_data["display_df"].to_excel(writer, sheet_name="Display_Ready")
        calced_data["main_df_rep"].to_excel(writer, sheet_name="Rep_Calculations")
        calced_data["display_df_rep"].to_excel(writer, sheet_name="Rep_Display_Ready")