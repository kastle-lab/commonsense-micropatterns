import os
from rdflib import URIRef, Graph, Namespace, Literal
from rdflib import OWL, RDF, RDFS, XSD, TIME
from rdflib.plugins.parsers.notation3 import ParserError

import re

import numpy as np

#  Directories
input_path = "../data/prompt-results"
output_path = "../data/extracted-patterns"
analysis_path = "../data/pattern-analysis"
pattern_path = "../csmodl/patterns"

#  Voting parameters
voting_limit = 1.03 # mean * 103%; only include values that are mean + x

#  Graph parameters (prefix)
pfs = {
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "owl": OWL,
    "time": TIME,
    "kastle": Namespace("https://kastle.cs.wright.edu/csmodl")
}
# predicate shortcut
a = pfs["rdf"]["type"]

# Property Types
prop_types = [
    pfs["rdf"]["Property"],
    pfs["owl"]["ObjectProperty"],
    pfs["owl"]["DatatypeProperty"]
]

def init_kg(prefixes=pfs):
    kg = Graph()
    for prefix in pfs:
        kg.bind(prefix, pfs[prefix])
    return kg

def serialization(noun, graph:Graph):
    output_file = f"{noun}.ttl"
    dest = os.path.join(pattern_path, output_file)
    graph.serialize(format="turtle", encoding="utf-8", destination=dest)

def markdown_cleanup(ontology):
    '''
        Helper cleanup function specifically for markdown codeblock tags
    '''
    #  Strip any leading findable ```
    ontology = ontology.replace("```turtle","\n")
    ontology = ontology.replace("```ttl","\n")
    ontology = ontology.replace("```@","\n@")
    ontology = ontology.replace(".```",".\n```")
    ontology = ontology.replace(". ```",".\n```")
    ontology = ontology.replace(". ```",".\n```")

    if "```" in ontology:
        onto_clean = ontology.split("\n")
        ontology = ""
        for i in range(1, len(onto_clean)-1): # Skip first set of "```"
            if "```" in onto_clean[i]: # If second set found, don't append.
                break
            ontology += f"{onto_clean[i]}\n"
        ontology = ontology.replace(" .", " .\n")
        ontology = ontology.replace("\".", "\".\n")
        ontology = ontology.replace(";", ";\n")
    return ontology

def strip_uri(uri):
    tokens = re.split("[#/]", uri)
    name = tokens[-1]
    return name

def parse_results(verbose=False):
    '''
        Generates noun-specific directories with resultant TTL files
        provided the list of TSV in `resources`.
    '''
    result_files = os.listdir(input_path)
    result_files.sort()
    for result_file in result_files:
        name, ext = result_file.split(".")
        # Only process the tsv files
        if ext != "tsv":
            # Historically there were some other file exts
            continue
        else:
            # print(f"Parsing {name}.")
            pass

        noun_dir = os.path.join(output_path,name)
        # Organize turtle output per LLM generated noun ontologies to individual directory
        if(not os.path.exists(noun_dir)): 
            os.mkdir(noun_dir)
            print(f"\tCreating firectory: {noun_dir}")

        with open(os.path.join(input_path, result_file), "r") as inp:
            lines = [ line.strip() for line in inp.readlines() ]

            for count, line in enumerate(lines):
                # Simple naming convention for unique noun ontology
                out_name = f"{name}_{count}.ttl" 
                split = line.split("\t")
                
                index = 0
                for s in split:
                    if("@" in s):
                        break
                    index+=1
                try:
                    ontology = split[index]
                except IndexError:
                    if verbose:
                        print(f"No valid ontology found for: {out_name} ")
                    continue

                out = open(os.path.join(noun_dir, out_name), "w")
                # Clean up ttl lines
                ## These were determined while running the script a few times
                ## And seeing how RDFlib was failing to parse the graphs
                ontology = ontology.replace(" .", " .\n")
                ontology = ontology.replace("\".", "\".\n")
                ontology = ontology.replace(";", ";\n")
                ontology = ontology.replace("@@", "@")
                ontology = ontology.replace("resourceex", "resource\nex")
                ontology = ontology.replace("propertyex", "property\nex")
                ontology = ontology.replace("classex", "class\nex")
                ontology = ontology.replace("# Classes", "# Classes\n")
                ontology = ontology.replace("# Properties", "# Properties\n")
                ontology = ontology.replace("# Individuals", "# Individuals\n")
                ontology = ontology.replace("\"ex:", "\"\nex:")

                ## Sometimes class names were wrapped in curly braces
                ## These are removed when encountered
                pattern = r'[a-zA-Z]*:{' # weird { } syntax
                ontology = re.sub(pattern, '', ontology)
                ontology = ontology.replace("}", "")

                if("[" in ontology):
                    try:
                        ontology += split[index+1]
                    except IndexError:
                        pass

                if("```" in ontology):
                    ontology = markdown_cleanup(ontology)
                ontology = ontology.replace('\n\n', '\n')
                ontology = ontology.replace('>@', '>\n@')
                ontology = ontology.replace('>ex', '>\nex')

                #  Write to individual file
                out.write(ontology)

def voting_helper(propDict, key):
    values = []
    for _, value in propDict.items():
        if(len(value) > 1):
            for v in value:
                values.append(v)
        else:       
            values.append(value)

    # Mean and Std Dev stats    
    mean = np.mean(values)
    std_dev = np.std(values)

    # Z-Scores for outlier detection
    z_scores = [(x - mean) / std_dev for x in values]
    filtered_data = [x for x, z_score in zip(values, z_scores) if abs(z_score) <= 1.5]

    mean = np.mean(filtered_data)
    threshold = float(mean*voting_limit)
    if(propDict[key] >= threshold): 
        return True
    return False

def vote_properties(verbose=False):
    '''
        Attempts to parse through generated TTL files from LLM generation

        Uses rdflib Graph to generate s,p,o per TTL file
    '''
    #  Stats File Setup
    analysis_filename = "noun-valid-ttl-parsing-analysis.out"
    analysis_filepath = os.path.join(analysis_path, analysis_filename)
    with open(analysis_filepath, "w") as stats_file: 
        ## Stats File Formatting
        stats_file.write(f"noun: \t countOfValidFiles \t countOfTotalFiles \t Ratio Parsed (%) \n")
        stats_valid = { filename.split(".")[0]: 0 for filename in os.listdir(input_path) }
        stats_total = { filename.split(".")[0]: 0 for filename in os.listdir(input_path) }
        
        noun_filepaths = os.listdir(input_path)
        noun_filepaths.sort()
        for noun_filepath in noun_filepaths: # For each Noun
            noun, ext = noun_filepath.split(".")
            noun_dir = os.path.join(output_path, noun)

            analysis_noun_filename = f"{noun}.out"
            analysis_noun_filepath = os.path.join(analysis_path, analysis_noun_filename)
            with open(analysis_filepath, "w") as analysis_noun_file:
                # All occurences from all nouns
                noun_properties = dict()
                noun_files = os.listdir(noun_dir)
                noun_files.sort()
                for filename in noun_files: # For each ttl from single Noun
                    stats_total[noun] += 1 # Total available files
                    unique_props = set() # Individual file occurrences per noun
                    curr_graph = init_kg()
                    with open(os.path.join(noun_dir, filename), "r") as f:
                        try:
                            if verbose:
                                print(f"Parsing: {filename}")
                            # Try to parse the graph
                            curr_graph.parse(f)
                        except Exception as e:
                            if verbose:
                                print(f"\tCould not parse. Skipping")
                            continue

                        #  Identifying Type Properties in Noun Ontology
                        for prop_type in prop_types:
                            for s,p,o in (curr_graph.triples( (None, pfs["rdf"]["type"], prop_type) )):
                                predicate = s
                                prop_name = strip_uri(predicate)
                            
                                try:
                                    _,_,prop_range = list(curr_graph.triples((predicate, RDFS.range,  None)))[0]
                                    _,_,prop_domain = list(curr_graph.triples((predicate, RDFS.domain,  None)))[0]
                                except IndexError as e:
                                    # Consider missing domain/range to be malformed property
                                    # This will accidentally remove all inverses
                                    if verbose:
                                        print(f"{prop_name} is malformed.")
                                    continue

                                try:
                                    domain_name = strip_uri(prop_domain)
                                    range_name = strip_uri(prop_range)
                                except:
                                    if verbose:
                                        print(prop_domain)
                                        print(prop_range)
                                unique_props.add((prop_name, domain_name, range_name))

                        for unique_prop in unique_props:
                            try: 
                                noun_properties[unique_prop] += 1
                            except KeyError as e:
                                noun_properties[unique_prop] = 1    
                    
                    # Stats File
                    stats_valid[noun] += 1

                # The graph that will hold the final combined turtle file
                noun_graph = init_kg()

                threshold = 0
                for k, v in noun_properties.items():
                    p, d, r = k

                    if v > threshold:
                        noun_graph.add( (pfs["kastle"][p], a, RDF.Property) )
                        noun_graph.add( (pfs["kastle"][p], RDFS.domain, pfs["kastle"][d]))
                        noun_graph.add( (pfs["kastle"][p], RDFS.range, pfs["kastle"][r]))

                # Serialize!
                try:
                    serialization(noun, noun_graph)
                except Exception as ex:
                    print(noun)

                #  Sort in descending value order for output
                noun_properties = {k: v for k, v in sorted(noun_properties.items(), key=lambda item: item[1], reverse=True)}
                for key, value in noun_properties.items():
                    analysis_noun_file.write(f"{key} \t {value}\n")

            #  Sort in ascending key order for output
            stats_valid = dict(sorted(stats_valid.items()))
            for key,value in stats_valid.items():
                try:
                    ratioUsed = round(float(value/stats_total[key]),2) * 100 # represent as percentage
                    stats_file.write(f"{key}: \t {value}  \t {stats_total[key]} \t {ratioUsed}\n")
                except Exception as ex:
                    pass

if __name__ == "__main__":
    parse_results()
    vote_properties()
