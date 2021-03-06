import censusdata
import pandas as pd
import geopandas as gpd
import cenpy
from cenpy import products

def get_block_tract_data(conn, features_list):
    '''
    Pulls raw census data from API from year 2018 ACS5, requires list of variables to pull.  
    If a variable is not available at the block group
    level, pulls the tract level.
    
    Input:
    features (list): list of census table names to pull from census data

    Output:
    merged (pandas df): dataframe with all the variables

    '''
    data_block = conn.query(features_list, geo_unit = 'block group', geo_filter = {"state": "17","county": "031"}) 

    block_filt = data_block.dropna(axis = 'columns', how='all')

    colnames = list(block_filt.columns)
    features_list2 = [feature for feature in features_list if feature not in colnames] + ['GEO_ID']

    data_tract = conn.query(features_list2, geo_unit = 'tract', geo_filter = {"state": "17","county": "031"})

    merged = block_filt.merge(data_tract, how = "inner", on = ["tract", "state", "county"])
    
    merged = merged.drop(['GEO_ID_y'], axis=1)
    merged = merged.rename(columns={"GEO_ID_x": "GEO_ID"})

    return merged


def rename_to_detailed(acs_data, year, features):
    '''
    This function gets the detailed names of census variables and renames the acs table variables
    accordingly.

    Inputs:
    acs_data (pandas dataframe): ACS data with table name variables as columns
    features (list): list of ACS table names

    Outputs:
    acs_renamed (pandas dataframe): ACS data with column names replaced with 
    detailed variable descriptiosn from Census

    Example: test = rename_to_detailed(primary_data, features_list)
    '''
    features1 = [feature for feature in features if feature != "GEO_ID" and not feature.startswith("C")]
    census_info = censusdata.censusvar('acs5', year, features1)

    rename_dict = {}
    for key, value in census_info.items():
        title = value[0].replace(" ", "_")
        subtype = value[1].replace("!!", "_")
        subtype = subtype.replace(" ", "_")
        rename_dict[key] = title + "__" + subtype
    
    
    acs_renamed = acs_data.rename(columns = rename_dict)

    return acs_renamed

def make_percents(acs_renamed):
    '''
    Makes ACS variables into percentage of total rather than absolute

    Inputs:
    acs_renamed = pandas df

    Outputs:
    acs_renamed = pandas df with additional columns that are percentage
    '''
    acs_renamed['Percent_NonCitizen'] = (acs_renamed['''NATIVITY_AND_CITIZENSHIP_STATUS_IN_THE_UNITED_STATES__Estimate_Total_Not_a_U.S._citizen'''] /
                                        acs_renamed['NATIVITY_AND_CITIZENSHIP_STATUS_IN_THE_UNITED_STATES__Estimate_Total'])

    # Percent speak English Poorly
    acs_renamed['Percent_SpeakEngl_Poorly'] = ((acs_renamed['''PLACE_OF_BIRTH_BY_LANGUAGE_SPOKEN_AT_HOME_AND_ABILITY_TO_SPEAK_ENGLISH_IN_THE_UNITED_STATES__Estimate_Total_Speak_other_languages_Speak_English_less_than_"very_well"'''] + 
                                               acs_renamed['''PLACE_OF_BIRTH_BY_LANGUAGE_SPOKEN_AT_HOME_AND_ABILITY_TO_SPEAK_ENGLISH_IN_THE_UNITED_STATES__Estimate_Total_Speak_Spanish_Speak_English_less_than_"very_well"''']) / 
                                               acs_renamed['''PLACE_OF_BIRTH_BY_LANGUAGE_SPOKEN_AT_HOME_AND_ABILITY_TO_SPEAK_ENGLISH_IN_THE_UNITED_STATES__Estimate_Total'''])

    # Educational attainment
    acs_renamed['Percent_less_than_HS'] = (acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total_Less_than_high_school_graduate'''] / 
                                           acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total'''])

    acs_renamed['Percent_HS'] = (acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total_High_school_graduate_(includes_equivalency)'''] / 
                                 acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total'''])

    acs_renamed['Percent_SomeCollege'] = (acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total_Some_college_or_associate's_degree'''] /
                                          acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total'''])

    acs_renamed['Percent_Bach'] = (acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total_Bachelor's_degree'''] /
                                   acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total'''])

    acs_renamed['Percent_Grad'] = (acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total_Graduate_or_professional_degree'''] /
                                   acs_renamed['''PLACE_OF_BIRTH_BY_EDUCATIONAL_ATTAINMENT_IN_THE_UNITED_STATES__Estimate_Total'''])

    #No vehicals
    acs_renamed['Percent_No_vehicals'] = (acs_renamed['''SEX_OF_WORKERS_BY_VEHICLES_AVAILABLE__Estimate_Total_No_vehicle_available'''] / 
                                         acs_renamed['''SEX_OF_WORKERS_BY_VEHICLES_AVAILABLE__Estimate_Total'''])
  
    #SNAP and Benefits

    acs_renamed['Percent_Received_SNAP'] = (acs_renamed['''RECEIPT_OF_FOOD_STAMPS/SNAP_IN_THE_PAST_12_MONTHS_BY_POVERTY_STATUS_IN_THE_PAST_12_MONTHS_FOR_HOUSEHOLDS__Estimate_Total_Household_received_Food_Stamps/SNAP_in_the_past_12_months'''] /
                                            acs_renamed['''RECEIPT_OF_FOOD_STAMPS/SNAP_IN_THE_PAST_12_MONTHS_BY_POVERTY_STATUS_IN_THE_PAST_12_MONTHS_FOR_HOUSEHOLDS__Estimate_Total'''])

    #Work Status

    acs_renamed['Percent_Men_Usually_Fulltime_Employed'] = (acs_renamed['''SEX_BY_WORK_STATUS_IN_THE_PAST_12_MONTHS_BY_USUAL_HOURS_WORKED_PER_WEEK_IN_THE_PAST_12_MONTHS_BY_WEEKS_WORKED_IN_THE_PAST_12_MONTHS_FOR_THE_POPULATION_16_TO_64_YEARS__Estimate_Total_Male_Worked_in_the_past_12_months_Usually_worked_35_or_more_hours_per_week'''] / 
                                                            acs_renamed['''SEX_BY_WORK_STATUS_IN_THE_PAST_12_MONTHS_BY_USUAL_HOURS_WORKED_PER_WEEK_IN_THE_PAST_12_MONTHS_BY_WEEKS_WORKED_IN_THE_PAST_12_MONTHS_FOR_THE_POPULATION_16_TO_64_YEARS__Estimate_Total_Male'''])

    acs_renamed['Percent_Women_Usually_Fulltime_Employed'] = (acs_renamed['''SEX_BY_WORK_STATUS_IN_THE_PAST_12_MONTHS_BY_USUAL_HOURS_WORKED_PER_WEEK_IN_THE_PAST_12_MONTHS_BY_WEEKS_WORKED_IN_THE_PAST_12_MONTHS_FOR_THE_POPULATION_16_TO_64_YEARS__Estimate_Total_Female_Worked_in_the_past_12_months_Usually_worked_35_or_more_hours_per_week'''] /
                                                              acs_renamed['''SEX_BY_WORK_STATUS_IN_THE_PAST_12_MONTHS_BY_USUAL_HOURS_WORKED_PER_WEEK_IN_THE_PAST_12_MONTHS_BY_WEEKS_WORKED_IN_THE_PAST_12_MONTHS_FOR_THE_POPULATION_16_TO_64_YEARS__Estimate_Total_Female'''])


    # Percent have no internet
    acs_renamed['Percent_No_Internet_Access'] = (acs_renamed['INTERNET_SUBSCRIPTIONS_IN_HOUSEHOLD__Estimate_Total_No_Internet_access'] /
                                                 acs_renamed['INTERNET_SUBSCRIPTIONS_IN_HOUSEHOLD__Estimate_Total'])

    # Percent have computing device (incl cellphone)
    acs_renamed['Percent_Computing_Device'] = (acs_renamed['COMPUTERS_IN_HOUSEHOLD__Estimate_Total_Has_one_or_more_types_of_computing_devices'] /
                                               acs_renamed['COMPUTERS_IN_HOUSEHOLD__Estimate_Total'])

    return acs_renamed

def rename_and_filter(acs_renamed):
    '''
    Renames certain variables and filters to just the percentages and the median

    Inputs:
    acs_renamed (pandas df)

    Outputs:
    acs_filtered (pandas df)
    '''
    acs_renamed = acs_renamed.rename(columns={'''MEDIAN_HOUSEHOLD_INCOME_IN_THE_PAST_12_MONTHS_(IN_2018_INFLATION-ADJUSTED_DOLLARS)__Estimate_Median_household_income_in_the_past_12_months_(in_2018_inflation-adjusted_dollars)''' : "Median_Income",
                                              '''MEDIAN_AGE_BY_SEX__Estimate_Median_age_--_Total''' : "Median_Age"})

    filter_cols = [col for col in acs_renamed.columns if col.startswith('Percent') or \
        col.startswith('GEO') or col.startswith('Median')]

    acs_filtered = acs_renamed[filter_cols]

    return acs_filtered

