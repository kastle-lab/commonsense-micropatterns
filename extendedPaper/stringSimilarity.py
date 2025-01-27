# Michael McCain
# 12/19/2024
# This program compares the strings between the noun and verb lists and the class and relation lists. The cosine sim and jaro-winkler sim scores are calculated and saved to csv files. 

import spacy
import os
import numpy as np
import pandas as pd
from numpy.linalg import norm
from strsimpy.jaro_winkler import JaroWinkler

# Function to normalize list using lemmatization with spaCy
def norm_list(list_of_strings):
    normal_list = []
    for string in list_of_strings:
        nlp_string = nlp(string)
        tokens = [token.lemma_.lower().strip() for token in nlp_string if not token.is_punct]
        normal_list.append(" ".join(tokens))
    return normal_list

# Function to compare strings between two lists, calculate their cosine similarity, and save each compared item to a csv file in the desired directory. Threshold disabled by default. Directory must be declared. Returns list of created files. 
def comparison(list1, list2, directory, header1="Item1", header2="Item2", threshold=False, threshold_value=0.79):
    # Initiate Jaro-Winkler
    jw = JaroWinkler()

    # Get current working dir
    prev_dir = os.getcwd()

    # Create path to target dir
    target_dir = directory
    target_path = os.path.join(prev_dir, target_dir)

    # Check if dir exists
    if os.path.exists(target_path):
        os.chdir(target_path)
        print(f"Current directory: {os.getcwd()}")
    else:
        os.makedirs(target_path)
        os.chdir(target_path)
        print("Directory '", target_path, "' created.")

   # List to keep track of created files
    created_files = []

    # Compare items in list 1 and list 2
    for list1_item in list1:
        list1_vector = nlp(list1_item).vector           # Get vector of item1
        list1_item_norm = np.linalg.norm(list1_vector)  # Calculate norm of noun vector

        if list1_item_norm == 0:  # Skip if the noun vector is zero
            continue

        # List to hold tuples for string cosine sim scores
        scores = []

        for list2_item in list2:
            list2_vector = nlp(list2_item).vector       # Get vector of item2
            list2_item_norm = np.linalg.norm(list2_vector)  # Calculate norm of class vector

            if list2_item_norm == 0:  # Skip if the class vector is zero
                continue
            
            # Cosine Similarity Score
            cosine = np.dot(list1_vector, list2_vector) / (list1_item_norm * list2_item_norm)        
            cosine = float(cosine)                      # Convert to python float

            # Jaro-Winkler Score
            jw_score = jw.similarity(list1_item, list2_item)

            if threshold == True:
                if cosine >= threshold_value:
                    scores.append((list1_item, list2_item, jw_score, cosine))
                    print(scores)
            else:
                scores.append((list1_item, list2_item, jw_score, cosine))

        # Put results of list1_item comparisons into a dataframe and save as csv              
        df = pd.DataFrame(scores, columns=[header1, header2, "Jaro-Winkler_Score", "Cosine_Sim_Score"])
        df = df.sort_values(by="Cosine_Sim_Score", ascending=False) # Sort by descending cosine sim scores

        file_path = os.path.join(os.getcwd(), f"{list1_item}.csv") # Save file path
        df.to_csv(file_path, index=False)
        created_files.append(file_path)

    # Return to dir before function call
    os.chdir(prev_dir)
    print("Comparison complete.")

    return created_files


### MAIN ###
# Initiate spacy with large model
nlp = spacy.load("en_core_web_lg")

#input("Press enter to continue...")

# file paths
classes_path = r"C:/commonsense-micropatterns/extendedPaper/classes.out"
relations_path = r"C:/commonsense-micropatterns/extendedPaper/relations.out"
nouns_path = r"C:/commonsense-micropatterns/extendedPaper/nouns.out"
verbs_path = r"C:/commonsense-micropatterns/extendedPaper/verbs.out"
noun_verb_path = r"C:/commonsense-micropatterns/extendedPaper/nounVerb.out"

print("Creating lists from files...")
# Create lists from file contents
with open(classes_path, 'r', encoding="utf-8") as classes_file, open(relations_path, 'r', encoding="utf-8") as relations_file, open(nouns_path, 'r', encoding="utf-8") as noun_file, open(verbs_path, 'r', encoding="utf-8") as verb_file, open(noun_verb_path, 'r', encoding="utf-8") as nv_file:
  class_list = classes_file.read().split("\n")      # Classes
  relation_list = relations_file.read().split("\n") # Relations (predicates)
  noun_list = noun_file.read().split("\n")          # Nouns list
  verb_list = verb_file.read().split("\n")          # Verbs list
  nv_list =  nv_file.read().split("\n")             # Combined nouns/verbs list

print("Normalizing lists...")
# Normalize lists
class_list = norm_list(class_list)
relation_list = norm_list(relation_list)
noun_list = norm_list(noun_list)
verb_list = norm_list(verb_list)
nv_list = norm_list(nv_list)
cr_list = class_list + relation_list  # Combined class/relations list

# Perform string similiarty  comparison
print("Comparing nouns with classes...")

noun_files_created = comparison(noun_list, class_list, "extendedPaper\\evaluations\\perfect\\perfectNounResults", "Noun", "Class", True, 1.0)

# num = 0
# print("Noun files created:")
# for i in noun_files_created:
#     num = num + 1
#     print(num, ") " ,i)

print("Comparing verbs with predicates...")
verb_files_created = comparison(verb_list, class_list, "extendedPaper\\evaluations\\perfect\\perfectVerbResults", "Verb", "Predicate", True, 1.0)

print("Comparing CQ strings against Enslaved strings...")
noun_verb_files_created = comparison(nv_list, cr_list, "extendedPaper\\evaluations\\perfect\\perfectNounVerbResults", "CQ_String", "Enslaved_String", True, 1.0)

print("Program done.")

