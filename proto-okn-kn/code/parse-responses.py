import os

import pandas as pd

input_dir = os.path.join("./proto-okn-kn/gpt-responses")
inp_file = "v5_protoOKN_responses_4.tsv"
output_dir = os.path.join("./proto-okn-kn/prompt-results")
def parse_and_write_tsv(data:pd.DataFrame, key_notion, count=0):
    """Parses data and writes it to a TSV file based on the key notion.

    Args:
        data: A list of dictionaries, each representing a row of data.
        key_notion: The specific key notion for the current file.
    """

    filename = f"{key_notion}.tsv"
    columns = ['Key Notion', 'Prompt', 'Response']
    df_filtered = data[columns]
    df_filtered = df_filtered[data['Key Notion'] == key_notion]
    df_filtered.to_csv(os.path.join(output_dir,filename), sep='\t', index=False, header=False)

# Assuming your data is in a CSV file
def main():
    # Read the data from a CSV file
    df = pd.read_csv(os.path.join(input_dir, inp_file), sep="\t")
    # Get unique key notions
    key_notions = df['Key Notion'].unique()

    # Create TSV files for each key notion
    for key_notion in key_notions:
        parse_and_write_tsv(df, key_notion)

if __name__ == '__main__':
    main()