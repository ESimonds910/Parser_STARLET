import pandas as pd
import numpy as np
from string import ascii_uppercase as letters


def find_replicate_data(df):
    df["Replicate"] = np.where(
        df["Plate"].apply(lambda x: '-' in x and int(x[-1:])) > 1,
        "replicate", ""
    )

    rep_df = df[df["Replicate"] == "replicate"]
    main_df = df[df["Replicate"] == ""]

    main_df = main_df.drop("Replicate", axis=1)
    return main_df, rep_df


def add_standard(df, proj_data):
    # std_row = proj_data["std_row"]
    std_conc = proj_data["std_conc"]
    # std_pos = proj_data["std_pos"]

    if type(std_conc) == dict:
        df.insert(
            6,
            "std_conc",
            df["Well_Id"].apply(
                lambda x: std_conc[x] if x in std_conc else ""
            )
        )
    # elif std_row != "" and std_pos == "half":
    #     df.insert(
    #         6,
    #         "std_conc",
    #         df["Well_Id"].apply(
    #             lambda x: std_conc[int(x[1:]) - 1] if x[:1] in std_row and int(x[1:]) > 6 else ""
    #         )
    #     )
    # elif std_row != "":
    #     df.insert(
    #         6,
    #         "std_conc",
    #         df["Well_Id"].apply(
    #             lambda x: std_conc[int(x[1:]) - 1] if x[:1] in std_row else ""
    #         )
    #     )
    return df


def build_columns(df, plate, proj_data, w_idx, df_id="main"):
    proj_name = proj_data["proj_name"]
    volumes = proj_data["volumes"]

    if df.shape[1] == 16 or df.shape[0] == 8:
        row_len = 4
    else:
        row_len = 8
    well_ids = [letter + str(num).zfill(2) for letter in letters[:row_len] for num in range(1, 13)]

    if df_id == "display":
        df.insert(0, "Plate", plate)
        df.insert(1, "Well_Id", well_ids[w_idx])
        df.insert(2, "Row", df["Well_Id"].apply(lambda x: x[:1]))
        df.insert(3, "Col", df["Well_Id"].apply(lambda x: x[1:]))
        df.insert(4, "Volumes", volumes)
        df.insert(0, "Id", plate.split("-")[0] + "-" + df["Well_Id"])
        df.insert(0, "Unique_Id", proj_name + "-" + df["Id"])
        return df

    df.insert(0, "Plate", plate)
    df.insert(1, "Well_Id", well_ids[w_idx])
    df.insert(0, "Id", plate.split("-")[0] + "-" + df["Well_Id"])
    df.insert(0, "Unique_Id", proj_name + "-" + df["Id"])
    return df


def data_format(source, proj_data):
    plates = proj_data["plates"]
    points = proj_data["points"]
    display_formatted_df = pd.DataFrame()
    main_formatted_df = pd.DataFrame()

    start_row = 0
    if points == 8:
        end_row = 8
    else:
        end_row = 16
    for plate in plates:
        well_index = 0
        for row in range(start_row, end_row, 2):
            row_2 = row + 1

            end_col = int(source.shape[1] / 2)
            for col in range(1, end_col, 2):
                col_2 = col + 1
                dna_col = col + 24
                dna_col_2 = dna_col + 1

                alpha_quad = list(source.iloc[row][[col]]) + list(source.iloc[row_2][[col]]) + list(source.iloc[row][[col_2]]) + list(source.iloc[row_2][[col_2]])
                dna_quad = list(source.iloc[row][[dna_col]]) + list(source.iloc[row_2][[dna_col]]) + list(source.iloc[row][[dna_col_2]]) + list(source.iloc[row_2][[dna_col_2]])

                main_df_columns = [f"Alpha_{n}" for n in range(1, 5)] + [f"DNA_{n}" for n in range(1, 5)]
                if points == 8:
                    row_3 = row + 8
                    row_4 = row + 9
                    alpha_quad_2 = list(source.iloc[row_3][[col, col_2]]) + list(source.iloc[row_4][[col, col_2]])
                    alpha_quad += alpha_quad_2
                    dna_quad_2 = list(source.iloc[row_3][[dna_col, dna_col_2]]) + \
                                 list(source.iloc[row_4][[dna_col, dna_col_2]])
                    dna_quad += dna_quad_2
                    main_df_columns = [f"Alpha_{n}" for n in range(1, 9)] + [f"DNA_{n}" for n in range(1, 9)]

                main_df = pd.DataFrame([alpha_quad + dna_quad], columns=main_df_columns)
                display_df = pd.DataFrame([alpha_quad, dna_quad], index=["Alpha", "DNA"]).transpose()

                main_df = build_columns(main_df, plate, proj_data, well_index)
                display_df = build_columns(display_df, plate, proj_data, well_index, df_id="display")

                main_df = add_standard(main_df, proj_data)
                display_df = add_standard(display_df, proj_data)

                main_formatted_df = pd.concat([main_formatted_df, main_df])
                display_formatted_df = pd.concat([display_formatted_df, display_df])
                well_index += 1
        start_row += 16
        end_row += 16

    main_formatted_df, main_formatted_rep_df = find_replicate_data(main_formatted_df)
    display_formatted_df, display_formatted_rep_df = find_replicate_data(display_formatted_df)

    df_list = [main_formatted_df, main_formatted_rep_df, display_formatted_df, display_formatted_rep_df]

    return df_list


if __name__ == "__main__":
    pass
