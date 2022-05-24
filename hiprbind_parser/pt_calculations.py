import pandas as pd
import numpy as np

def find_max(main_dfs, proj_data):

    max_found = False
    max_slope = 0
    original_max = 0
    max_cols = [f"alpha_slope_{n}" for n in range(1, 8)]
    alpha_cols = [f"Alpha_{n}" for n in range(1, 9)]
    search_cols = alpha_cols + max_cols
    selected_row = clean_df[clean_df["Alpha_avg_raw"] == row].loc[:, search_cols]
    # new_avg = selected_row.loc[:, ["Alpha_5", "Alpha_6", "Alpha_7", "Alpha_8"]].std(axis=1).item()
    # row_minus_std = row - std
    while not max_found:

        # print(max_cols)
        max_slope = float(selected_row.loc[:, max_cols].max(axis=1))

        # print(f"max_slope: {max_slope}")
        col_idx = selected_row.loc[:, max_cols].idxmax(axis=1).item()
        # print(f"col_idx 1: {col_idx}")
        try:
            col_num = int(col_idx.split("_")[2])
        except IndexError:
            print(f"col_idx 2: {col_idx}")
        alpha_raw_max = int(selected_row[f"Alpha_{col_num}"])
        # print(f"alpha_raw_max: {alpha_raw_max} vs alpha_mean: {row}")
        if alpha_raw_max < row:
            max_cols.remove(col_idx)
            if max_slope > original_max:
                original_max = max_slope
            if max_cols == []:
                return original_max
        else:
            max_found = True
            return max_slope


def make_calculations(dfs, proj_data):
    dv = proj_data["volumes"]
    points = proj_data["points"]
    signals = ["Alpha", "DNA"]
    final_dfs = []

    for df in dfs:

        # df["Alpha_avg_raw"] = df.loc[:, "Alpha_1":"Alpha_8"].mean(axis=1)

        for signal in signals:
            for n in range(1, points):
                df[f"{signal}_slope_{n}"] = round(
                    (df[f"{signal}_{n + 1}"] - df[f"{signal}_{n}"]) / (dv[n] - dv[n - 1]), 2
                )

            # df["Value"] = df["Alpha_avg_raw"].apply(find_max, args=(df, ))
            # df["4pt_selection"] = df.loc[:, "alpha_slope_1":"alpha_slope_4"].max(axis=1)
            if points == 8:
                last_slope = 4
            else:
                last_slope = 3
            df[f"{signal}.Max.Slope"] = df.loc[:, f"{signal}_slope_1": f"{signal}_slope_{last_slope}"].max(axis=1)

        # for n in range(1, 8):
        #     df[f"DNA_slope_{n}"] = round((df[f"DNA_{n + 1}"] - df[f"DNA_{n}"]) / (dv[n] - dv[n - 1]), 2)
        #
        # df["DNA.Max.Slope"] = df.loc[:, "dna_slope_1":"dna_slope_4"].max(axis=1)

        df["HPB_DNA"] = round(df["Alpha.Max.Slope"] / df["DNA.Max.Slope"], 2)

        if proj_data["od_file"]:
            df["Od600"] = df["Od600"].apply(lambda x: round(float(x), 2) if x != "" else "0.0")
            df["HPB_OD"] = round(df["Alpha.Max.Slope"] / df["Od600"], 2)

        final_dfs.append(df)
    return final_dfs


if __name__ == "__main__":
    test_df = pd.read_csv("test_df_precalc.csv")
    volumes = [0.21428571, 0.03061224, 0.00437318, 0.00062474, 0.00008925, 0.00001275, 0.00000182, 0.00000026]
    output_df = make_calculations(test_df, volumes)
    print(output_df.iloc[0])
    output_df.to_csv("Test_output.csv")
