# Michael McCain
# 02/6/2025
# This script gathers the appropriate wikidata for the extracted patterns

# Libraries
import requests
import os
from time import sleep

# Functions
## This function will search a directory for subdirectory names. Then it will return a list of those names.
def Find_Dirs( desiredDirectory):
    
    list_dir = [] # List to hold directory names
    try:
        for root, dirs, files in os.walk(desiredDirectory): # Search for directorys
            for i in dirs:
                dir_name = str(i)
                list_dir.append(dir_name)
            return list_dir
        print(f"Directory not found!") # File not found output
    except FileNotFoundError:
        print(f"\nError: Directory not found.")
    except PermissionError:
        print(f"\nError: Permission for '{desiredDirectory} denied.")
    except Exception as e:
        print(f"\nError: An unknown error occured: {e}")

## Fetches wikidata endpoint
def Fetch_Wikidata(params):
    url = 'https://www.wikidata.org/w/api.php'
    try:
        return requests.get(url, params=params)
    except:
        return 'Error'
    

# Main
start_dir = ".\data\extracted-patterns"     # Starting Directory  
extracted_patterns = Find_Dirs(start_dir)   # List of dir names from start_dir 
id_dict = {}    # Dictionary to hold IDs (key) and label (value)

## Get data for each pattern
for pattern in extracted_patterns:
    ### Dictionary to hold parameters for fetching
    pattern_params = {  
        'action': 'wbsearchentities',
        'format': 'json',
        'search': pattern,
        'language': 'en'
    }
    pattern_data = Fetch_Wikidata(pattern_params) 
    sleep(2)
    pattern_data = pattern_data.json()
    
for each in pattern_data:
    ###  Parse JSON and show values for ID of matched pattern
    for i in range(len(pattern_data)):
        if pattern_data['search'][i]['label'] == pattern.lower():
            print("Item ID/Label: ",pattern_data['search'][i]['id'], pattern_data['search'][i]['label'])
            id_dict.update({pattern_data['search'][i]['id']: pattern_data['search'][i]['label']})
    #input("Press a key to continue...")
    
# Save to file
with open ("./extendedPaper"'w') as file:
    id_dict.items()

print(id_dict.items())

## Fetch data from IDs
# for identifier in id_dict.keys():
#     id_params = {
#                     'action': 'wbgetentities',
#                 'ids':identifier, 
#                 'format': 'json',
#                 'languages': 'en'
#     }
    
#     pattern_data = Fetch_Wikidata(id_params)
