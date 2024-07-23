# Sample code for getting queries

from omegaconf import OmegaConf
from queries import json # example query function
import pandas as pd
import os
import logging


SETTINGS_PATH = 'settings_template.yml'

# retrieve configuration file
settings = OmegaConf.load(SETTINGS_PATH)

if __name__ == "__main__":

    # make folder
    os.makedirs(settings.output_folder, exist_ok=True)

    # set up logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=settings.log_path, encoding='utf-8', level=logging.INFO)

    # load csv
    column_list = [settings.input_column_serial, settings.input_column_testcase, settings.input_column_groundtruth] + settings.input_column_groups
    dataset_df = pd.read_csv(settings.input_file_path)[column_list]

    # limit csv range
    if settings.input_serial_start:
        dataset_df = dataset_df[dataset_df[settings.input_column_serial] >= settings.input_serial_start]

    # split into autosave batches
    df_split_list = [group for _, group in dataset_df.groupby(dataset_df.index // settings.autosave_batch)]

    # loop csv through function to get result
    results_list = []
    for split in df_split_list:
        # get query results
        results_df = json.multi_query(
            text_df=split,
            query_settings=settings.query_settings,
            input_column_serial=settings.input_column_serial,
            input_column_testcase=settings.input_column_testcase
        )
        results_list.append(results_df)
        results_df = pd.concat(results_list)
        results_df.to_csv(settings.output_result_path)
        logging.info(f'Queried {len(results_df)} of {len(dataset_df)}')

    results_df = pd.concat(results_list)
    results_df.to_csv(settings.output_result_path)
    full_df = pd.merge(dataset_df, results_df, how="right", on=[settings.input_column_serial, settings.input_column_serial])
    full_df.to_csv(settings.output_all_path)