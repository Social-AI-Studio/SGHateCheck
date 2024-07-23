""" 
Example function to read json file from experiment
Very inefficient but it is meant as an example when querying outputs that give results one by one

"""

import json
import pandas as pd
import random
import logging
from pprint import pprint

logger = logging.getLogger(__name__)

def single_query(
            text:str,
            file_path:str,
            annotation_path:str,
            minwait:int = 0, 
            maxwait:int = 0, 
            ):
    
    """ 
    text:str text to be tested
    file_path: file to read from
    minwait:int min wait between actions, in seconds, used when analysing wait times for online queries. 
    maxwait:int max wait between actions, in seconds, used when analysing wait times for online queries. 

    reads json files from experiments
    """

    # dummy function
    wait_time = random.uniform(minwait, maxwait)

    # get c_id
    annotations_df = pd.read_csv(annotation_path)
    c_id = annotations_df[annotations_df['c_testcase'] == text]['c_id'].values[0]

    # get classification
    classification_df = pd.read_json(file_path)
    try:
        hate_score = classification_df[classification_df['case_id'] == c_id]['classified'].values[0]
        if hate_score == 'non-hateful':
            return {'Hateful Score': 0.0}, wait_time
        else:
            return {'Hateful Score': 1.0}, wait_time
    except:
        return {'Hateful Score': -1}, wait_time

def multi_query(text_df:pd.DataFrame, query_settings:dict, input_column_serial:str, input_column_testcase:str)-> pd.DataFrame: 
    """ 
    text_iterable:pd.DataFrame df containing information, 
    query_settings:dict query settings for single_query, 
    input_column_groundtruth:str , 
    input_column_serial:str,
    input_column_testcase:str
    """

    output = []
    for index, row in text_df.iterrows():
        # query
        metrics_dict, wait_elapsed = single_query(text=row[input_column_testcase], **query_settings)
        output.append(
            {
                input_column_serial:row[input_column_serial],
                input_column_testcase:row[input_column_testcase],
                'wait_elapsed': wait_elapsed,
                **metrics_dict,
            }
        )

    return pd.DataFrame(output)