### Data Processing ###
import pandas as pd
import census_module as cm
import censusdata
import geopandas as gpd
import cenpy
from cenpy import products

features_list = [
"GEO_ID", 
"B19013_001E",
"B01002_001E",
"B05001_001E",
"B05001_006E",
"B06007_001E",
"B06007_008E",
"B06007_005E",

"B06009_001E",
"B06009_002E",
"B06009_003E",
"B06009_004E",
"B06009_005E",
"B06009_006E",


"B08014_001E",
"B08014_002E",
"B08014_003E",
"B08014_004E",

"B22003_001E",
"B22003_002E",
"B22003_005E",

"B17020_001E",
"B17020_002E",
"B17020_010E",

"B23022_001E",
"B23022_002E",
"B23022_003E",
"B23022_004E",
"B23022_025E",
"B23022_026E",
"B23022_027E",
"B23022_028E",
"B23022_049E",

"B28010_001E",
"B28010_002E",
"B28011_001E",
"B28011_002E",
"B28011_007E",
"B28011_008E"
]

conn = products.APIConnection("ACSDT5Y2018")
merged = cm.get_block_tract_data(conn, features_list)

merged[features_list[1:]] = merged[features_list[1:]].apply(pd.to_numeric)

renamed = cm.rename_to_detailed(merged, 2018, features_list)

percents = cm.make_percents(renamed)

filtered = cm.rename_and_filter(percents)

filtered["geo_12"] = filtered["GEO_ID"].map(lambda x: str(x)[-12:])
filtered.loc[filtered['Median_Income'] < 0, 'Median_Income'] = 'NA'
filtered.to_csv('../data/census_processed.csv',index=False)