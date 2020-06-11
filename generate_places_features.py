import pandas as pd
import geopandas as gpd

from shapely.geometry import Point, Polygon
from shapely import wkt

COLUMNS = ['safegraph_place_id', 'location_name_x', 'street_address_x', 'city_x',
           'region_x', 'postal_code_x', 'brands_x',  'top_category',
            'sub_category', 'latitude', 'longitude']

logging.basicConfig(level=logging.INFO)


def read_in_data(filepath):
	'''
	Read csv as pandas dataframe
	'''
	return pd.read_csv(filepath)

def merge_places_patterns(coreplaces_filepath, patterns_filepath):
	'''
	Merge safegraph coreplaces and patterns datasets
	'''
	cp_df = pd.read_csv(coreplaces_filepath)
	wp_df = pd.read_csv(patterns_filepath)
	merged = wp_df.merge(cp_df, on ='safegraph_place_id')

	return filter_daterange(merged)

def filter_daterange(merged_df):
	'''
	Filter merged dataframe to stay-at-home order timeframe
	'''
	new = merged_df['date_range_start'] = merged_df['date_range_start'].str.split('T', n=1, expand=True)
	merged_df['week_start_date']= new[0]
 	merged_df['week_start_date'] = pd.to_datetime(merged_df['week_start_date'], format='%Y-%m-%d')

 	return merged[(merged['week_start_date'] > '2020-03-21') & merged['week_start_date'] < '2020-05-01']


def find_top_categories(merged_df, n):
	'''
	Find n most visited categories in merged dataset
	'''
	top_cat = merged_df.groupby('top_category').size()
 	top_cat = top_cat.reset_index()
 	top_cat.columns = ['category','count']
 	top_cat = top_cat.sort_values(by='count', ascending=False)
 	return list(top_cat['top_category'].head(n))


def filter_df_top_categories(merged_df, n):
	'''
	Filter dataframe to include just top n categories
	'''
	cats = find_top_categories(merged_df, n)
	places_df = merged[merged['top_category'].isin(cats)]
 	places_df = places_df[COLUMNS]
  	return places_df.drop_duplicates()


def make_places_gdf(merged_df, n):
	'''
	Create places geopandas dataframe of top n categories 
	'''
	filtered = filter_df_top_categories(merged_df, n)
	geometry = [Point(xy) for xy in zip(filtered.longitude, filtered.latitude)]
	crs = 'epsg:4326'
	return gpd.GeoDataFrame(filtered, crs=crs, geometry=geometry)


def create_chicago_tiger_gdf():
	'''
	Use chicago tiger geopandas dataframe from Chicago Data Portal to get geo_12 identifier
	'''
	tiger_gdf = gpd.read_file("https://data.cityofchicago.org/resource/bt9m-d2mf.geojson?$limit=9999999")
	tiger_gdf["geo_12"] = census_gdf["geoid10"].map(lambda x: str(x)[:12])
	return tiger_gdf


def create_places_features(coreplaces_filepath, patterns_filepath, output_filepath, n):
	'''
	Create places features csv from SafeGraph coreplaces and patterns dataframe,
	merged with Chicago TIGER data to get geo_12 identifier for data
	'''
	places_df = merge_places_patterns(coreplaces_filepath, patterns_filepath)
	places_gdf = make_places_gdf(places_df, n)
	tiger_gdf = create_chicago_tiger_gdf()

	merged = gpd.sjoin(census_gdf, places_gdf, how="left", op='contains')
	counts = merged.groupby([merged['geo_12'],merged['top_category'].fillna('tmp')]).size()
	num_organisations = counts.unstack().fillna(0)
	top_places_df = num_organisations.reset_index()

	top_places_df.to_csv(output_filepath, index=False)


if __name__ == "__main__":
	logging.info("Creating places features csv")

	create_places_features('./data/raw/coreplaces_filtered_chicago.csv',
						   './data/raw/weekly_patterns_fitered.csv',
						   './data/places_features.csv', 10)

