import sys
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
    "kastle": Namespace("https://kastle.cs.wright.edu/csmodl#")
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
    if tokens[-1]=="":
        name = tokens[len(tokens)-2]

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
            analysis_filepath = os.path.join(analysis_path, analysis_noun_filename)
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
                                    
                                    # Convert URIs to Pascal Case
                                    if domain_name[0].islower():
                                        domain_name = domain_name.capitalize()
                                    if range_name[0].islower():
                                        range_name = range_name.capitalize()
                                    
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
                if verbose:
                    print(noun_properties)

            # The graph that will hold the final combined turtle file
            noun_graph = init_kg()

            threshold = 0
            for k, v in noun_properties.items():
                p, d, r = k

                if v > threshold:
                    # Use correct prefix where applicable
                    xsd_pfx = ["boolean", 
                               "float", "int", "decimal", 
                               "string", "date"]
                    rdfs_pfx = ["Literal"]
                    d_pfx = "kastle"
                    r_pfx = "kastle"

                    #  Convert predicate to camelcase
                    p = p[0].lower() + p[1:]

                    noun_graph.add( (pfs["kastle"][p], a, RDF.Property) )

                    if str(r).lower() in xsd_pfx:
                        r_pfx = "xsd"
                        r = r.lower()
                    if r in rdfs_pfx:
                        r_pfx = "rdfs"
                    
                    noun_graph.add( (pfs["kastle"][p], RDFS.domain, pfs[f"{d_pfx}"][d]))
                    noun_graph.add( (pfs["kastle"][p], RDFS.range, pfs[f"{r_pfx}"][r]))

            # Serialize!
            try:
                serialization(noun, noun_graph)
            except Exception as ex:
                print(noun)

def generate_opla_annotations():
    # Predicate shortcut
    a = pfs["rdf"]["type"]

    opla_pfs = {
        "dc": Namespace("http://purl.org/dc/elements/1.1/"),
        "opla": Namespace("http://ontologydesignpatterns.org/opla#"),
        "opla-core": Namespace("http://ontologydesignpatterns.org/opla-core#"),
        "opla-sd": Namespace("http://ontologydesignpatterns.org/opla-sd#"),
        "opla-cp": Namespace("http://ontologydesignpatterns.org/opla-cp#")
    }

    opla_noun_namespace = "https://archive.org/services/purl/domain/modular_ontology_design_library/"

    for filename in os.listdir(pattern_path): # For each Noun
        noun, ext = filename.split(".")
        noun = noun.replace(" ", "")
        noun_ontology = f"{opla_noun_namespace}{noun}"

        graph = init_kg()
        for opla_pf in opla_pfs:
            graph.bind(opla_pf, opla_pfs[opla_pf])
        
        graph.parse(os.path.join(pattern_path,filename))

        # Mint URI
        noun_onto_uri = Namespace(noun_ontology)[""]
        
        # Add to graph
        graph.add((noun_onto_uri, a, OWL.Ontology))
        
        # Add OPLA Properties
        graph.add( (noun_onto_uri, opla_pfs["opla-core"]["hasPatternName"], Literal(f"{noun} Pattern", datatype=XSD.string)) )
        graph.add( (noun_onto_uri, opla_pfs["opla-cp"]["addressesScenario"], Literal(f"", datatype=XSD.string)) )
        graph.add( (noun_onto_uri, opla_pfs["opla-cp"]["hasCompentencyQuestion"], Literal(f"", datatype=XSD.string)) )
        graph.add( (noun_onto_uri, opla_pfs["opla-sd"]["hasSchemaDiagramFileName"], Literal(f"{noun}-pattern.pdf", datatype=XSD.string)) )
        graph.add( (noun_onto_uri, opla_pfs["opla-sd"]["hasConnections"], Literal(f"", datatype=XSD.string)) )
        graph.add( (noun_onto_uri, opla_pfs["dc"]["contributor"], Literal(f"", datatype=XSD.string)) )
        graph.add( (noun_onto_uri, opla_pfs["dc"]["creator"], Literal(f"", datatype=XSD.string)) )
        
        # Overwrite original TTL file with new additions
        serialization(noun, graph)

if __name__ == "__main__":
    parse_results()
    vote_properties()
    generate_opla_annotations()