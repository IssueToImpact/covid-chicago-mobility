# covid-chicago-mobility

A UChicago class project aiming to predict reduction in mobility at the census block level as a result of the COVID-19 stay-at-home order in Chicago. Across Chicago there have been stark differences in the impact of COVID-19 in different neighborhoods (see [Illinois Department of Public Health COVID-19 Statistics](https://www.dph.illinois.gov/covid19/covid19-statistics)).
Predicting reductions in mobility at the block-group level would allow for more specific neighborhood level policies to put in place, in order to effectively mitigate the impact of COVID-19. 

Here we use a random forest model to predict reduction in movement at the neighborhood level in Chicago as a result of the first part of the stay-at-home order in Chicago (21st March - 1st May). 

### Data

This project uses cellphone mobility data from [Safegraph](https://docs.safegraph.com) combined with [ACS](https://www.census.gov/programs-surveys/acs) census data at the census block group level in Chicago.

The mobility targets are created using [Safegraph social distancing metrics data](https://docs.safegraph.com/docs/social-distancing-metrics)

The features for the model are in two parts:

1. ACS demographic data

2. [SafeGraph Places Data](https://docs.safegraph.com/docs/places-schema): we created a count of each of the top 10 categories of places in the SafeGraph data (e.g. Grocery stores) still being visited in Chicago since the stay-at-home order for each census block group.

### Running instructions

#### 1. Set up
Set up a virtual environment (e.g. with `virtualenv`)and install package requirements from  `requirements.txt`

#### 2. Creating datasets
* All files for creating the target and features datasets are in the `create_datasets` directory
* All created files are saved within `data` directory
* All raw safegraph data (used by the modules in `create_datasets` is saved within `data/raw` 

##### Step 1: filtering SafeGraph data to Cook County/Chicago, Illinois
`create_datasets/safegraph_data_etl.py` : for each of safegraph social_distancing, coreplaces and weekly_patterns data, takes raw data folders and filters all to Cook County/Chicago data into one filtered file 

**N.B.** in order to run this, you first need to access to the SafeGraph data, and to follow their instructions to download the raw data for each of the three datasets.

##### Step 2: create targets from SafeGraph social distancing data
run jupyter notebook: `create_datasets/safegraph_targets/safegraph_targets.ipynb`

This notebook reads in safegraph social distancing data, aggregates/computes targets, and plots histogram distributions of the targets.

##### Step 2: create features from ACS data
run `create_datasets/census_features/generate_census_features.py`

##### Step 3: create features from safegraph places data
run `create_datasets/places_features/generate_places_features.py`

#### 3. Data exploration
`data-analysis.ipynb` - notebook to explore the features and targets. Creates choropleth maps of target and feature distribution across census block groups in Chicago. Map images are saved in './figure_outputs'

#### 4. Running the models
`COVID_model.ipynb` - notebook runs a regularised regression model and a random forest model for each of our two targets. 














