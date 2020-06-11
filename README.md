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

### Getting started

Set up a virtual environment and install package requirements from  `requirements.txt`

e.g. with virtualenv:

`virtualenv venv` 

`source venv/bin/activate`

`pip3 install -r requirements.txt`

