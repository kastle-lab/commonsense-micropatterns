# Commonsense Micropatterns
This repository describes a set of 104 commonsense micropatterns (CSMPs). These are tiny ontology design patterns (ODPs) that are constructed in a rather naïve fashion (generally for ad hoc schema construction) and sourced from a commonsense model. In this case, we prompt ChatGPT 4 to provide an ODP for the top 100 most common words in the English language (as sourced from [here](https://www.espressoenglish.net/100-common-nouns-in-english/)).

## Directory Structure
* `code/` -- the code to extract patterns from the responses, clean extracted turtle files, and create the patterns.
* `data/` -- the direct results of the prompting, as stored in multiple formats.
* `csmodl/` -- the modular ontology design library created from these patterns.
