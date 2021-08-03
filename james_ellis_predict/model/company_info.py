'''
Creates the following features:

country_code (need to change this to some form of one hot)
business_sector (1 hot)
age_years: age of the company in years. Arroyo et al. use months but quantisation not right for the trust code
has_email
has_phone
has_facebook_url
has_twitter_url
has_linkedin_url

Optional to add:

description_sentiment
'''

# Module imports
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from tabloo import show

from utils import splitDataFrameList


# NOTE need to add 1 hot encoding for the country variable
# NOTE could add in the description sentiment 

def company_info(tc, ts, stats=False):
    # Note, total_funding_usd not included here because it could include funding that has taken place during the simulation window.
    # Hence, we calculate total_funding_usd in funding_info where it can be calculated for a specific warmup window
    org_cols = ['uuid', 'country_code', 'founded_on','facebook_url', 'linkedin_url', 'twitter_url',
    'email', 'phone',  'primary_role', 'category_groups_list']

    org = pd.read_csv('../../../data/raw/organizations.csv', usecols=org_cols)
    
    # Only interested in primary roll of company
    org = org[org['primary_role'] == 'company']
    org = org.drop(columns='primary_role')
    
    # Removing certain rows with no values
    org = org[org['country_code'].notna()]
    org = org[org['founded_on'].notna()] 
    org = org[org['category_groups_list'].notna()] 
    
    country_codes = ['USA', 'CHN', 'IND', 'GBR', 'SGP', 'SWE', 'DEU', 'CAN', 'KOR']

    for country in country_codes:
        org[country] = org['country_code'].str.fullmatch(country).astype(int)
    org = org.drop(columns='country_code')

    org['other_country'] = np.where(org[country_codes].sum(axis=1)==0, 1, 0)
    
    # Only want companies founded between t_c (start of warmup) and t_s (start of simulation)
    org = org[
        (org['founded_on'] >= tc) &
        (org['founded_on'] < ts)
        ]
    
    if stats:
        # Shows significant spikes at the start of each year i.e trust code 4
        org['founded_on'].value_counts(normalize=True).sort_index().plot()
        plt.show()
    
    # Age of the company at the start of the simulation window 
    # Not sure whether to round up or not

    def age_years(x):
        fmt = "%Y-%m-%d"
        tdelta = datetime.strptime(ts, fmt) - datetime.strptime(x, fmt)
        return round(tdelta.days/365.2425)

    org['age_years'] = org['founded_on'].transform(age_years)
    org = org.drop(columns='founded_on')

    # 1 hot encoding for social media and contact info presence
    cols = ['email', 'phone', 'facebook_url', 'twitter_url', 'linkedin_url']
    for col in cols:
        org['has_{}'.format(col)] = org[col].transform(lambda x: 1 if pd.notna(x) else 0)
    org = org.drop(columns=cols)

    # 1 hot encoding for the category group list

    # Obtains unique categories
    _df = splitDataFrameList(org, 'category_groups_list', ',')
    categories = _df['category_groups_list'].unique()

    for cat in categories:
        org[cat] = org['category_groups_list'].transform(lambda x: 1 if cat in x.split(',') else 0)
    org = org.drop(columns='category_groups_list')

    return org

if __name__=="__main__":
    company_info('2013-12-01','2017-12-01', stats=False)
