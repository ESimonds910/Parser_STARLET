import pandas as pd


def join_dfs(df_list, raw_od, proj_data):

    ab_name = proj_data["ab_name"]
    join_df_list = []
    for df in df_list:
        df.set_index("Unique_Id", inplace=True)
        raw_od.set_index("Harvest_sample_id", drop=False, inplace=True)
        join_df = raw_od.join(df, how="right")

        try:
            join_df.loc[(join_df["std_conc"].apply(lambda x: x) != ""), "Sample_type"] = "Standard"
        except KeyError:
            pass

        if ab_name != "":
            join_df.insert(loc=1, column="HPB_scheme", value=ab_name)
        join_df_list.append(join_df)
    return join_df_list
