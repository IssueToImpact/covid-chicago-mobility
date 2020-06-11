import os
import csv
import gzip
import pandas as pd
import logging

WEEKLY_PATTERNS_MAIN_COLS = ['safegraph_place_id', 'location_name', 'street_address', 'city',
                            'region', 'postal_code', 'brands', 'naics_code', 'date_range_start',
                            'date_range_end', 'raw_visit_counts', 'raw_visitor_counts',
                            'visits_by_day', 'visits_by_each_hour', 'visitor_home_cbgs',
                            'visitor_country_of_origin', 'distance_from_home', 'median_dwell',
                            'bucketed_dwell_times', 'related_same_day_brand'
                            'related_same_week_brand', 'device_type', 'iso_country_code']

COREPLACES_COLUMNS = ['safegraph_place_id', 'parent_safegraph_place_id', 'location_name',
                    'safegraph_brand_ids', 'brands', 'top_category', 'sub_category',
                    'naics_code', 'latitude', 'longitude', 'street_address', 'city',
                    'region', 'postal_code', 'iso_country_code', 'phone_number',
                    'open_hours', 'category_tags']

SOCIAL_DISTANCE_COLUMNS = ['origin_census_block_group', 'date_range_start', 'date_range_end',
       'device_count', 'distance_traveled_from_home',
       'bucketed_distance_traveled',
       'median_dwell_at_bucketed_distance_traveled',
       'completely_home_device_count', 'median_home_dwell_time',
       'bucketed_home_dwell_time', 'at_home_by_each_hour',
       'part_time_work_behavior_devices', 'full_time_work_behavior_devices',
       'destination_cbgs', 'delivery_behavior_devices',
       'median_non_home_dwell_time', 'candidate_device_count',
       'bucketed_away_from_home_time', 'median_percentage_time_home',
       'bucketed_percentage_time_home']

logging.basicConfig(level=logging.INFO)


def filter_social_distancing(root_dir_path, output_file_path):
    '''
    Filter safegraph social distancing data to just Cook county
    '''
    with open(output_file_path, 'wt') as of:
        c = csv.writer(of)
        c.writerow(SOCIAL_DISTANCE_COLUMNS)

        for dirpath, subdirs, files in os.walk(root_dir_path):
            for file in files:
                filename = os.path.join(dirpath, file)
                with gzip.open(filename, 'rt') as f:
                    reader = csv.reader(f)
                    filtered = filter(lambda p: p[0].startswith('17031'), reader)
                    c.writerows(filtered)


def filter_places(dir_path, output_file_path):
    '''
    Filter safegraph coreplaces and patterns data to just Chicago
    '''
    with open(output_file_path, 'wt') as of:
        c = csv.writer(of)
        c.writerow(COREPLACES_COLUMNS)

        for dirpath, subdirs, files in os.walk(dir_path):
            for file in files:
                filename = os.path.join(dirpath, file)
                with gzip.open(filename, 'rt') as f:
                    for row in csv.reader(f):
                        if row[11] == 'Chicago':
                            c.writerow(row)


def remove_cols(in_file, out_file, max_col_num):
    '''
    Handle some versions of the data having different numbers of columns 
    '''
    with open(out_file, 'wt') as of:
        c = csv.writer(of)
        with open(in_file, 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                c.writerow(row[:max_col_num])


if __name__ == '__main__':

    logging.info("Filtering social distancing data")
    filter_social_distancing('../data/raw/social_distancing_data/',
                            '../data/raw/filtered_social_distancing.csv')

    logging.info("Filtering coreplaces data")
    filter_places('../data/raw/coreplaces/coreplaces_data/',
                  '../data/raw/filtered_coreplaces.csv')

    logging.info("Filtering weekly patterns data")
    filter_places('../data/raw/weekly_patterns/v1/main-file',
                  '../data/raw/filtered_patterns.csv')







