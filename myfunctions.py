#myfunctions
import pickle
import json
import os
import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPolygon, shape, GeometryCollection
import json
import plotly.express as px
from urllib.request import urlopen


##############
# VARIABLES 
##############

all_offices = ['Associate Justice of the Supreme Court, Place 1',
                'Associate Justice of the Supreme Court, Place 2',
                'Associate Justice of the Supreme Court, Place 3',
                'Associate Justice of the Supreme Court, Place 4',
                'Attorney General', 'Chief Justice of the Supreme Court',
                'Commissioner of Agriculture and Industries', 'Governor',
                'Lieutenant Governor', 'Public Service Commission, Place 1',
                'Public Service Commission, Place 2', 'Secretary of State',
                'State Auditor', 'State Representative', 'State Senator',
                'State Treasurer', 'US Representative',
                'State Board of Education Member', 'Corporation Commissioner',
                'State Mine Inspector', 'Superintendant of Public Instruction',
                'US Senator', 'Auditor of State', 'Commissioner of State Lands',
                'State Senate', 'Board of Equalization Member', 'Controller',
                'Insurance Commissioner', 'State Assembly Member', 'Treasurer',
                'Governor/Lieutenant Governor',
                'Regent of the University of Colorado', 'Comptroller',
                'Governor and Lieutenant Governor', 'Secretary of the State',
                'Auditor of Accounts', 'Chief Financial officer',
                'Commissioner of Agriculture', 'State Attorney',
                'Commissioner of Insurance', 'Commissioner of Labor',
                'Public Service Commission, District 3 - Metro-Atlanta',
                'Public Service Commission, District 5 - Western',
                'State School Superintendent', 'State Controller',
                'State Representative A', 'State Representative B',
                'Superintendent of Public Instruction', 'Treasurer of State',
                'Secretary of Agriculture', 'Governor / Lt. Governor',
                'House of Delegates Member', 'Auditor', "Governor's Council",
                'Secretary of the Commonwealth',
                'Member of the State Board of Education',
                'Regent of the University of Michigan',
                'State Representative (Partial Term Ending 01/01/2019)',
                'State Senator (Partial Term Ending 01/01/2019)',
                'US Representative (Partial Term Ending 01/03/2019)',
                'Governor & Lt Governor', 'Auditor of Public Accounts',
                'Governor and Lt. Governor', 'Public Service Commissioner',
                'Executive Council', 'Commissioner of Public Lands',
                'Justice of the Supreme Court', 'Supreme Court Justice',
                'NC Supreme Court Associate Justice Seat 1',
                'Agriculture Commissioner', 'For Attorney General',
                'For Corporation Commissioner', 'For Insurance Commissioner',
                'State Auditor and Inspector', 'General Treasurer',
                'Comptroller General', 'State Superintendent of Education',
                'Commissioner School Public Lands',
                'Public Utilities Commissioner',
                'Commissioner of the General Land office',
                'Comptroller of Public Accounts',
                'Judge, Court of Criminal Appeals Place 7',
                'Judge, Court of Criminal Appeals Place 8',
                'Justice, Supreme Court, Place 2',
                'Justice, Supreme Court, Place 4',
                'Justice, Supreme Court, Place 6',
                'Presiding Judge, Court of Criminal Appeals',
                'Railroad Commissioner', 
                'Member, State Board of Education',
                'State Representative Pos. 1', 
                'State Representative Pos. 2',
                'State House Delegate', 
                'State Assembly Representative',]

major_offices = ['Governor',
                 'US Representative',
                 'US Senator',
                 'Governor/Lieutenant Governor',
                 'Governor and Lieutenant Governor',
                 'Governor / Lt. Governor',
                 'US Representative (Partial Term Ending 01/03/2019)',
                 'Governor & Lt Governor', 
                 'Governor and Lt. Governor', 
                 'For Attorney General',]

congress =      ['US Representative',
                 'US Senator',
                 'US Representative (Partial Term Ending 01/03/2019)',]

house =         ['US Representative',
                 'US Representative (Partial Term Ending 01/03/2019)',]



###############
# FUNCTIONS
###############

# DATA PREPROCESSING FUNCTIONS
def load_county(f):
    '''
    Get the dataFrame of US county info
    
    Project specific function to load the county df from json containing polygon info for each county
    
    Parameters:
    f (str): file path
    
    Returns:
    us_county (DataFrame): dataframe of US counties
    '''
    
    us_county_path = f

    cur_json = json.load(open(us_county_path, encoding='ISO-8859-1'))
    path,ext = os.path.splitext(us_county_path)
    new_path = path+"_new"+ext

    with open(new_path,"w", encoding='utf-8') as jsonfile:
        json.dump(cur_json,jsonfile,ensure_ascii=False)

    us_county = gpd.read_file(new_path, driver='GeoJSON')

    us_county['fips'] = us_county['STATE'] + us_county['COUNTY']
    us_county = us_county[us_county['STATE'].apply(int) < 57]
    us_county_df = pd.DataFrame(us_county[['STATE', 'COUNTY', 'NAME', 'CENSUSAREA','fips']])
    print(us_county_df.head())
    
    return us_county


def csv_encoding_fix(f):
    '''
    fix an encoding issue on a csv file.
    encoding on many of my files prevented some functionality of the dataframes
    
    Parameters:
    f (str):  file path
    '''
    df = pd.read_csv(f,  encoding='latin')
    df.to_csv(f)
    print('file created:', f)
    
    
def get_pop(fips, pop_df):
    try:
        pop = pop_df[pop_df['fips']==fips]['POPESTIMATE2018'].values[0]
        return pop
    except:
        print(fips)
        return 0

def get_area(fips, us_county_df):
    try:
        area = us_county_df[us_county_df['fips']==fips]['CENSUSAREA'].values[0]
        return float(area)
    except Exception as e:
        print(fips, e)
        return 0
    

# MAPPING FUNCTIONS
def make_choro(df, geojson, col, color_list, range_color):
    fig = px.choropleth(df, 
                        geojson=geojson, 
                        locations='fips', 
                        color=col,
                        #color_discrete_sequence=px.colors.qualitative.Set1,
                        color_continuous_scale=color_list,
                        range_color=range_color,
                        scope="usa",
                        labels={'Party':'party'},
                        hover_name='county',
                        hover_data=[col, 'party'],
                    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


def add_longlat(df):
    df['longlat'] = list(zip(df['long'].astype('float'), df['lat'].astype('float')))
    df['points'] = df['longlat'].apply(make_point)
    return df

def make_point(longlat):
    '''
    Returns a shapely Point object from a latlong location.

            Parameters:
                    latlong (list): iterable of len 2 [lat, long]

            Returns:
                    Point object
    '''
    # note that the point requires (long, lat) or (x, y) format
    return Point(longlat[0], longlat[1])




def get_county(point, us_county):
    for i in range(len(us_county)):
        poly = us_county.iloc[i]['geometry']
        if poly.contains(point):
            return us_county.iloc[i]['fips']
        
def get_stores_by_county(store_df, us_county):
    found = store_df['points'].apply(get_county, args=[us_county])
    return found.value_counts()
