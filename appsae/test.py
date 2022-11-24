import requests
import json

# Define a business ID
category_alias = 'hotdogs'

# Define API Key, Search Type, and header
MY_API_KEY = 'yrzAjuWxX9PQzxXL1om7yRlmDV2wb45YoBNbLim5Vd2dBvknXfxVoj-ISRFmhi76RQWqAfybNV3N6vG5u_CjUI63A' \
             '-gev2jmG5bMEyWW7GoxPfd6YFKsHdL3tphSY3Yx '
BUSINESS_PATH = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'Bearer ' + MY_API_KEY}

# Define the Parameters of the search
PARAMETERS = {'location':'San Diego',
              'limit':10,
              'offset': 0}

# Make a Request to the API, and return results
response = requests.get(url=BUSINESS_PATH,
                        params=PARAMETERS,
                        headers=HEADERS)

# Convert response to a JSON String
business_data = response.json()

f = open('.\\result.txt','w')
f.write(json.dumps(business_data, indent=3))
f.close()