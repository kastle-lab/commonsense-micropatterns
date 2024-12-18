import spacy
import os
import numpy as np
import pandas as pd
from numpy.linalg import norm

# Function to normalize list using lemmatization with spaCy
def norm_list(list_of_strings):
    normal_list = []
    for string in list_of_strings:
        nlp_string = nlp(string)
        tokens = [token.lemma_.lower().strip() for token in nlp_string if not token.is_punct]
        normal_list.append(" ".join(tokens))
    return normal_list

# Function to compare strings between two lists, calculate their cosine similarity, and return it as a df with custom headers. Threshold disabled by default
def comparison(list1, list2, header1="Item1", header2="Item2", threshold=False, threshold_value=0.79):
    scores = []

    # Compare items in list 1 and list 2
    for list1_item in list1:
        list1_vector = nlp(list1_item).vector           # Get vector of item1
        list1_item_norm = np.linalg.norm(list1_vector)  # Calculate norm of noun vector

        if list1_item_norm == 0:  # Skip if the noun vector is zero
            continue

        for list2_item in list2:
            list2_vector = nlp(list2_item).vector       # Get vector of item2
            list2_item_norm = np.linalg.norm(list2_vector)  # Calculate norm of class vector

            if list2_item_norm == 0:  # Skip if the class vector is zero
                continue
            
            # Cosine Similarity Score
            cosine = np.dot(list1_vector, list2_vector) / (list1_item_norm * list2_item_norm)        
            cosine = float(cosine)                      # Convert to python float

            if threshold == True:
                if cosine > threshold_value:
                    scores.append((list1_item, list2_item, cosine))
            else:
                scores.append((list1_item, list2_item, cosine))

    # Put results into a dataframe and return             
    df = pd.DataFrame(scores, columns=[header1, header2, "Similarity Score"])
    return df

### MAIN ###
# Initiate spacy with large model
nlp = spacy.load("en_core_web_lg")

# file paths
classes_path = r"C:/commonsense-micropatterns/extendedPaper/classes.out"
relations_path = r"C:/commonsense-micropatterns/extendedPaper/relations.out"
nouns_path = r"C:/commonsense-micropatterns/extendedPaper/nouns.out"
verbs_path = r"C:/commonsense-micropatterns/extendedPaper/verbs.out"
noun_verb_path = r"C:/commonsense-micropatterns/extendedPaper/nounVerb.out"

# Create lists from file contents
with open(classes_path, 'r', encoding="utf-8") as classes_file, open(relations_path, 'r', encoding="utf-8") as relations_file, open(nouns_path, 'r', encoding="utf-8") as noun_file, open(verbs_path, 'r', encoding="utf-8") as verb_file, open(noun_verb_path, 'r', encoding="utf-8") as nv_file:
  class_list = classes_file.read().split("\n")      # Classes
  relation_list = relations_file.read().split("\n") # Relations (predicates)
  noun_list = noun_file.read().split("\n")          # Nouns list
  verb_list = verb_file.read().split("\n")          # Verbs list
  nv_list =  nv_file.read().split("\n")             # Combined nouns/verbs list

# Normalize lists
class_list = norm_list(class_list)
relation_list = norm_list(relation_list)
noun_list = norm_list(noun_list)
verb_list = norm_list(verb_list)
nv_list = norm_list(nv_list)
cr_list = class_list + relation_list  # Combined class/relations list

# Perform string similiarty  comparison
print("Comparing...")
df_noun = comparison(noun_list, class_list, "Noun", "Class")
df_verb = comparison(verb_list, class_list, "Verb", "Predicate")
df_combo = comparison(nv_list, cr_list, "CQ String", "Enslaved String")

# Save dfs as csv files
print("Saving as CSV...")
df_noun.to_csv("nounClassComparison.csv", index=False)
df_verb.to_csv("verbPredicateComparison.csv", index=False)
df_combo.to_csv("nounVerbClassPredicateComparison.csv", index=False)

print("Program done.")



