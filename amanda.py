import pandas as pd
import geopandas as gpd
import json

def drop_rows(df):
    pass


def get_frac_devices_home(df):
    df['fraction_of_devices_home'] = (
        df['completely_home_device_count']/df['device_count'])


def get_frac_devices_work(df):
    df['fraction_of_devices_work'] = (
        (df['part_time_work_behavior_devices'] + df['full_time_work_behavior_devices'])/df['device_count'])


def get_frac_time_away(df):
    time_buckets = {"<20":10, "21-45":33, "46-60":53, "61-120":90, "121-180":150, "181-240":210, "241-300":270,
                    "301-360":330, "361-420":390, "421-480":460, "481-540":510, "541-600":570, "601-660":630,
                    "661-720":690, "721-840":780, "841-960":900, "961-1080":1020, "1081-1200":1140, "1201-1320":1260,
                    "1321-1440":1380, ">1440":1440}

    frac_time_away = []

    for row in df.iterrows():
        _frac = 0
        for key, val in json.loads(row[1]['bucketed_away_from_home_time']).items():
            _frac += val*time_buckets[key]
        frac_time_away.append(_frac)

    return frac_time_away


def process_targets(df):
    df = df.loc[df['date_range_start'] >= '2020-03-23'].copy()
    df = df.loc[df['date_range_start'] <= '2020-05-03'].copy()
    get_frac_devices_home(df)
    get_frac_devices_work(df)
    frac_time_away = get_frac_time_away(df)
    df['fraction_time_away_all'] = frac_time_away/(1440*df['device_count'])
    df['fraction_time_away_leave'] = frac_time_away/(1440*(df['device_count'] - df['completely_home_device_count']))
    df['Week'] = pd.to_datetime(df['date_range_start'], utc=True).dt.week
    df_weekly = df.groupby(['origin_census_block_group', 'Week'])[
                            ['device_count',
                             'fraction_of_devices_home',
                             'fraction_of_devices_work',
                             'fraction_time_away_all',
                             'fraction_time_away_leave']].mean().reset_index()
    df_weekly.rename(columns={"origin_census_block_group": "geo_12"}, inplace=True)

    return (df, df_weekly)
