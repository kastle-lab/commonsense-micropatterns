# pattern-generation
The `prompts/chatGPTPrompts.ipynb` Jupyter Notebook contains the code used to prompt and generate noun ontologies from a LLM, and `prompts/linting.py` is the notebook converted to a Python script.

The `pattern-generation.py` script will parse the generated responses from the `../data/prompt-results` directory to produce `noun` ontologies, stored as `turtle` files in `ttl` format. These `turtle` files are stored in `../data/extracted-patterns/{noun}`, where {noun} is the respective `noun` being described.

The `noun` ontologies are then parsed with the `graph` structure provided by `rdflib` and generates the `/analysis` output files with a count of unique properties for each noun.

The most occurring properties per noun become part of a common-sense `pattern` for a `noun`, thus, stripping the least occurring properties or less likely implemented representation of a `noun` with some relationship/property.

The final result of `pattern-generation.py` with the added OPaL annotation properties are stored `../csmodl/patterns`

## Challenges
The LLM generated responses resulted in variations of ontology representation from plain-text natural language descriptions to abiding a `turtle` format. The output of `pattern-generation` is only concerned with the generated `turtle` format.  As such, cleaning of the respective `column` holding the ontology in string was performed and still resulted in the inability for `rdflib`'s graph structure to be used.

`noun-valid-ttl-parsing-analysis.out` contains the ratio of valid files to total files the `rdflib` graph was able to parse.