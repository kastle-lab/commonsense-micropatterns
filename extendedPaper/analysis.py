# Michael McCain
# 12/20/2024
# This program reads in csv files from a directory and processes them to find matches that exceed a threshold. It then writes the results to a text file in a specified output directory.
# Some code borrowed from https://github.com/Data-Semantics-Laboratory/LLMDrivenOntologyDev
import os
import pandas as pd

# Function to count unique words that had matches
def count_unique_words(match_list):
    unique_words = set()
    for match in match_list:
        unique_words.add(match[0])
    return len(unique_words)

# Function to process directory
def process_directory(directory, threshold, output_directory, pos_type1, pos_type2):
    # Get current working dir
    prev_dir = os.getcwd()
    
    # Create paths
    directory = os.path.join(prev_dir, directory)
    output_directory = os.path.join(prev_dir, output_directory)
    target_path = os.path.join(prev_dir, directory)

    # Check if dir exists
    if os.path.exists(target_path):
        os.chdir(target_path)
        print(f"Current directory: {os.getcwd()}")
    else:
        print("Directory does not exist.")
        return 0
        # os.makedirs(target_path)
        # os.chdir(target_path)
        # print("Directory '", target_path, "' created.")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f'Output directory {output_directory} created.')

    total_matches = 0   # Variable to hold total matches that exceed threshold
    match_list = []     # List to hold words that exceed threshold
    
    # Create file to write summary results
    for filename in os.listdir(target_path):
        matches = 0          # Variable to hold matches that exceed threshold
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)

            # Create output file name
            output_file_name = f'evaluation-summary-{os.path.splitext(filename)[0]}.txt'  # Prefix with "evaluation-summary"
            output_file_path = os.path.join(output_directory, output_file_name)

            # Read in csv file
            df = pd.read_csv(file_path, delimiter=',')

            for row in df.itertuples(index=False):
                if row[2] > threshold or row[3] > threshold:
                    matches += 1
                    total_matches += 1
                    match_item1 = row[0]
                    match_item2 = row[1]
                    matched_items = (match_item1, match_item2)
                    match_list.append(matched_items)

            if len(df) != 0:
                percentage = matches / len(df) * 100  # Calculate percentage of good matches compared to the total number of compared words in the csv
            else:
                percentage = 0

            # Write to outputfile
            with open(output_file_path, 'w') as f:
                f.write(f'File: {filename}\n')
                f.write(f'Good Matches: {matches}\n')
                f.write(f'Percentage of Matches: {percentage:.2f}%\n\n')

    sum_output_file_name = f'_summary-{pos_type1}.txt'  
    sum_output_file_path = os.path.join(output_directory, sum_output_file_name)

    if not os.path.exists(output_directory):
      os.makedirs(output_directory)
      print(f'Output directory {sum_output_file_path} created.')

    # Count unique words that had matches
    unique_matches = count_unique_words(match_list)
    
    # Get total unique words from all CSVs
    total_unique_words = set()
    for filename in os.listdir(target_path):
        if filename.endswith('.csv'):
            df = pd.read_csv(os.path.join(directory, filename))
            total_unique_words.update(df.iloc[:, 0])  # First column contains the words
    
    match_percentage = (unique_matches / len(total_unique_words)) * 100 if total_unique_words else 0

    with open(sum_output_file_path, 'w') as f:
        f.write(f'Threshold value: {threshold}\n')
        f.write(f'Total word matches: {total_matches}\n')
        f.write(f'Unique words with matches: {unique_matches}\n')
        f.write(f'Total unique words: {len(total_unique_words)}\n')
        f.write(f'Percentage of words with matches: {match_percentage:.2f}%\n')
        f.write(f'\n{pos_type1} <--> {pos_type2} \nMatch List:\n####################\n')
        for match in match_list:
            f.write(', '.join(map(str, match)) + '\n')

    # Return to dir before function call
    os.chdir(prev_dir)
    print("Analysis complete.")

    return 

# Threshold
threshold = 1.0

# Directories to analyze and output analysis to
output_dir_noun = "extendedPaper\\summaries\\perfect\\perfectNounSummary"  # Output directory
an_dir_noun = "extendedPaper\\evaluations\\perfect\\perfectNounResults"                 # Directory to analyze
type_n = "Nouns"

output_dir_verb = "extendedPaper\\summaries\\perfect\\perfectVerbSummary"
an_dir_verb = "extendedPaper\\evaluations\\perfect\\perfectVerbResults"
type_v = "Verbs"

output_dir_nv = "extendedPaper\\summaries\\perfect\\perfectNounVerbSummary"
an_dir_nv = "extendedPaper\\evaluations\\perfect\\perfectNounVerbResults"
type_nv = "Nouns and Verbs"

process_directory(an_dir_noun, threshold, output_dir_noun, type_n, "Classes")
process_directory(an_dir_verb, threshold, output_dir_verb, type_v, "Predicates")
process_directory(an_dir_nv, threshold, output_dir_nv, type_nv, "Classes and Predicates")

