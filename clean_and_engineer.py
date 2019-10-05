import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
import calendar

#-------Clean the Data--------#
def drop_rows_cols(df):
    df.drop([1233], inplace=True)
    df.drop(['Candidate Native location',
            'Name(Cand ID)',
            'Unnamed: 23',
            'Unnamed: 24',
            'Unnamed: 25',
            'Unnamed: 26',
            'Unnamed: 27'], axis=1, inplace=True)x

def rename_cols(df):
    df.columns = ['date',
              'client',
              'industry',
              'location',
              'position',
              'skillset',
              'interview_type',
              'gender',
              'cand_cur_loc',
              'cand_job_loc',
              'interview_loc',
              'start_perm',
              'unsch_mtgs',
              'precall',
              'alt_num',
              'res_jd',
              'venue_clear',
              'letter_shared',
              'exp_attend',
              'obs_attend',
              'mar_status'] 

# general function to change yes/no answers to 1/0
def convert_yes_no_to_bool(df, col, str_to_match):
    series = pd.Series(np.where(df[col].values == str_to_match, 1, 0))
    df[col] = series
    return df

def clean_yes_no_cols(df):
    df = convert_yes_no_to_bool(df, 'obs_attend', 'Yes')
    df = convert_yes_no_to_bool(df, 'start_perm', 'Yes')
    df = convert_yes_no_to_bool(df, 'unsch_mtgs', 'Yes')
    df = convert_yes_no_to_bool(df, 'precall', 'Yes')
    df = convert_yes_no_to_bool(df, 'alt_num', 'Yes')
    df = convert_yes_no_to_bool(df, 'res_jd', 'Yes')
    df = convert_yes_no_to_bool(df, 'venue_clear', 'Yes')
    df = convert_yes_no_to_bool(df, 'letter_shared', 'Yes')
    df = convert_yes_no_to_bool(df, 'exp_attend', 'Yes')
    df = convert_yes_no_to_bool(df, 'mar_status', 'Married') # 1 for married, 0 for single
    df = convert_yes_no_to_bool(df, 'gender', 'Male') # 1 for male, 0 for female
    return df

# use df['Date of Interview'] as date argument
def clean_date_col(date):
    date = date.str.strip()
    date = date.str.split("&").str[0]
    date = date.str.replace('–', '/')
    date = date.str.replace('.', '/')
    date = date.str.replace('Apr', '04')
    date = date.str.replace('-', '/')
    date = date.str.replace(' ', '/')
    date = date.str.replace('//+', '/')
    return date

# Cleans locations in a pandas series
def clean_locations(series):
    ext = series.str.extract('(\w+)')
    ext[0] = ext[0].replace('Gurgaonr','Gurgaon')
    return ext[0].str.capitalize()

def clean_location_cols(df):
    df['location'] = clean_locations(df['location'])
    df['cand_cur_loc'] = clean_locations(df['cand_cur_loc'])
    df['cand_job_loc'] = clean_locations(df['cand_job_loc'])
    df['interview_loc'] = clean_locations(df['interview_loc'])
    return df

#------Engineer the Data------#

# create new column with day of the week (Monday=0 - Sunday=6)
def make_weekdays_column(df):
    df['date'] = pd.to_datetime(df['date'])
    weekdays = []
    for i in range(0,len(df['date'])):
        weekdays.append(df['date'][i].weekday())
    weekdays = pd.Series(weekdays)
    df['weekdays'] = weekdays
    return df

# calculate distances between locations
def get_distance(series1,series2):
    # Returns the L2 distance (in km) from series1 to series2; 
    # series1 and series2 are pandas series containing locations 
    # From https://distancecalculator.globefeed.com/India_Distance_Calculator.asp   
    loc_list = ['Bangalore', 'Chennai', 'Cochin', 
                'Delhi', 'Gurgaon', 'Hosur', 
                'Hyderabad', 'Noida', 'Visakapatinam']

    distances = np.array(
        [[   0,  290,  354, 1750,  346,  248,   39, 2127,  799],
         [ 290,    0,  692, 1768, 1742,  268,  515, 1748,  602],
         [ 354,  692,    0, 2090, 2062,  356,  863, 2675, 1429],
         [1750, 1768, 2090,    0,   43, 1777, 1266,   46, 1375],
         [ 346, 1742, 2062,   43,    0, 1750, 1240,   51, 1354],
         [ 248,  268,  356, 1777, 1750,    0,  608, 1757,  798],
         [  39,  515,  863, 1266, 1240,  608,    0, 1536,  503],
         [2127, 1748, 2675,   46,   51, 1757, 1536,    0, 1344],
         [ 799,  602, 1429, 1375, 1354,  798,  503, 1344,    0]]
         )

    dist_list = []
    for loc1, loc2 in zip(series1.values, series2.values):
        idx1 = loc_list.index(loc1)
        idx2 = loc_list.index(loc2)
        dist_list.append(distances[idx1,idx2])
    return pd.Series(dist_list, index=series1.index) 

if __name__ == "__main__":
#------Import and Clean Data------#
    df = pd.read_csv('data/Interview.csv')
    drop_rows_cols(df)
    rename_cols(df)
    clean_yes_no_cols(df)
    df['date'] = clean_date_col(df['date'])
    clean_location_cols(df)

#------Feature Engineering------#
    make_weekdays_column(df)
    df['d_loc2job'] = get_distance(df['location'], df['cand_job_loc'])
    df['d_loc2int'] = get_distance(df['location'], df['interview_loc'])

#------Export------#
    df_cleaned = df
    df_cleaned.to_csv('data/df_cleaned.csv')