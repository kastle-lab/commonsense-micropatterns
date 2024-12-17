import spacy
import os

# Function to remove duplicates from list
def remove_duplicates(list_in):
  return list(dict.fromkeys(list_in))

# Initiate spacy
nlp = spacy.load("en_core_web_sm")

# Output file paths
nouns_out_path = r"C:/commonsense-micropatterns/extendedPaper/nouns.out"
verbs_out_path = r"C:/commonsense-micropatterns/extendedPaper/verbs.out"
noun_verb_path = r"C:/commonsense-micropatterns/extendedPaper/noun-verb.out"

# Read CQ md files
enslaved_path = r"C:/commonsense-micropatterns/data/competency-questions/enslaved.md"
kwg_path = r"C:/commonsense-micropatterns/data/competency-questions/kwg.md"
proto_path = r"C:/commonsense-micropatterns/data/competency-questions/proto-okn.md"

with open(enslaved_path, 'r', encoding="utf-8") as enslaved_file, open(kwg_path, 'r', encoding="utf-8") as kwg_file, open(proto_path, 'r', encoding="utf-8") as proto_file:
  enslaved_contents = enslaved_file.read()
  kwg_contents = kwg_file.read()
  prot_contents = proto_file.read()

# Extract nouns and verbs
document = nlp(enslaved_contents + "\n" + kwg_contents + "\n" + prot_contents)
#print(document)

# Store nouns and verbs
noun_list = [token.text for token in document if token.pos_ == "NOUN"]
verb_list = [token.text for token in document if token.pos_ == "VERB"]
# Clean up lists
undesirable_chars = ["#","?", "*", ")", "(", "()", ",", "'","-", "8)", "|", "’m"]

for noun in noun_list:
  for char in undesirable_chars:
    if noun == char:
      noun_list.remove(noun)

for verb in verb_list:
  for char in undesirable_chars:
    if verb == char:
      verb_list.remove(verb)

# Combine lists
nouns_verbs_list = noun_list + verb_list

# Remove duplicates and sort
uni_noun_list = remove_duplicates(noun_list)
uni_noun_list.sort()
uni_verb_list = remove_duplicates(verb_list)
uni_verb_list.sort()
uni_nouns_verbs_list = remove_duplicates(nouns_verbs_list)
uni_nouns_verbs_list.sort()

# Write files
with open(nouns_out_path, 'w', encoding="utf-8") as nout, open(verbs_out_path, 'w', encoding="utf-8") as vout, open(noun_verb_path, 'w', encoding="utf-8") as nvout:
    # Write nouns
    for noun in uni_noun_list:
      nout.write(f'{noun}\n')
    # Write verbs
    for verb in uni_verb_list:
      vout.write(f'{verb}\n')
    # Write nouns and verbs
    for word in uni_nouns_verbs_list:
      nvout.write(f'{word}\n')

# Output file paths
classes_out_path = r"C:/commonsense-micropatterns/extendedPaper/classes.out"
relations_out_path = r"C:/commonsense-micropatterns/extendedPaper/relations.out"

with open(classes_out_path, 'r', encoding="utf-8") as classes_file:
  class_contents = classes_file.read()

with open(relations_out_path, 'r', encoding="utf-8") as relations_file:
  relation_contents = relations_file.read()

