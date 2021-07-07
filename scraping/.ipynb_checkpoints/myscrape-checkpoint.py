import requests
from bs4 import BeautifulSoup
import pandas as pd
import json



def get_cb_hrefs(n=-1):
    '''
    Get Cracker Barrel locations
    
    Returns the locations of every Cracker Barrel location in United States.  
    Works on current website as of 09/28/2020
    
    Parameters:
    n (int): if -1, returns all stores, otherwise returns n stores (for troubleshooting)
    
    Returns:
    all_stores_hrefs (list): list of every url for Cracker Barrel stores
    '''
    
    #THis gets me the links to each of the state pages
    URL = 'https://locations.crackerbarrel.com/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')


    # Start by getting all of the state URLs
    hrefs = soup.findAll('a')

    hrefs = [x['href'].strip() for x in hrefs if 'locations' in x['href']]
    state_hrefs = hrefs[1:-1]
    state_hrefs[:5]

    # THis bit of code gets me the url for every city that hosts a Cracker Barrel
    all_city_hrefs = []

    for URL in state_hrefs:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        hrefs = soup.findAll('a')
        hrefs = [x['href'].strip() for x in hrefs if 'locations' in x['href']]
        city_hrefs = hrefs[2:-1]
        all_city_hrefs.extend(city_hrefs)

    all_city_hrefs[:5]

    # Now we will use city URLs to grab the stores
    all_store_hrefs = []
    
    if n == -1:
        n = len(all_city_hrefs)
    
    for URL in all_city_hrefs[:n]:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        hrefs = soup.findAll('a')
        hrefs = [x['href'].strip() for x in hrefs if 'locations' in x['href']]
        store_hrefs = [x for x in hrefs if URL in x]
        all_store_hrefs.extend(store_hrefs)
    
    return all_store_hrefs






def get_cb_locs(urls):
    '''
    Get long/lat of every store in urls
    
    Parameters:
    urls(list): list of every Cracker Barrel URL
    
    Returns:
    long_lats
    '''
    # Now I just need to grab the lat long.  It looks like this on the store page
    # <meta property="place:location:latitude" content="34.781393" />


    long_lats = []

    for url in urls:

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        lat = soup.find('meta', {'property':"place:location:latitude"})
        lat = float(lat.get('content'))

        long = soup.find('meta', {'property':"place:location:longitude"})
        long = float(long.get('content'))

        long_lats.append([long, lat])

    return long_lats




def get_district_urls(n=None):
    '''
    Function goes through all of the shape files at theunitedstates.io and grabs the congressional districts
    '''
    
    # Get the shape files
    shape_url = 'https://theunitedstates.io/districts/cds/2016/'

    ## ex: NY-30/shape.geojson

    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    if n == None:
        pass
    else:
        states = states[:n]

    all_shape_urls = []

    for state in states:
        flag = 0
        for i in range(0, 54):  # 54 is max number of dists in any state
            url = shape_url + state + '-' + str(i) + '/shape.geojson'
            r = requests.get(url)
            if r.status_code > 200 and flag > 0:
                # if nothing is there, we are done
                break
            elif r.status_code > 200:
                # if there is a bad page, skip
                continue
            else:
                # if it is a good page, append
                all_shape_urls.append(url)

    return all_shape_urls



def get_district_geo(urls):
    '''
    Takes in a list of urls and returns a list of geojson data for congressional dists
    '''

    all_geojsons = []


    for url in urls:
        resp = requests.get(url=url)
        data = resp.json() # Check the JSON Response Content documentation below
        all_geojsons.append(data)

    return all_geojsons



if __name__ == '__main__':
    stores = get_cb_hrefs(5)
    print(stores)

