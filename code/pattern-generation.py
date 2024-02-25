import os
from rdflib import URIRef, Graph, Namespace, Literal
from rdflib import OWL, RDF, RDFS, XSD, TIME
from rdflib.plugins.parsers.notation3 import ParserError

import re

import numpy as np

#  Directory set up
output_path = "./code/output/"
input_path = "./code/resources/"
analysis_path = "./code/analysis/"
pattern_path = "./code/commonsense-patterns"

#  Graph parameters (prefix)
pfs = {
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "owl": OWL,
    "time": TIME
}

#  Hyperparameters
'''
    Properties to be added to the common-sense pattern of a noun
    is voted with respect to the mean/average count of occurrences
    in all properties and a manually set offset value, votingLimit.
'''
votingLimit = 1.03 # mean * 103%; only include values that are mean + x

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
    ''''
        Helper cleanup function specifically for markdown codeblock tags
    '''
    #  Strip any leading findable ```
    ontology = ontology.replace("```turtle","\n")
    ontology = ontology.replace("```ttl","\n")
    ontology = ontology.replace("```@","\n@")
    ontology = ontology.replace(".```",".\n```")
    ontology = ontology.replace(". ```",".\n```")
    ontology = ontology.replace(". ```",".\n```")

    if("```" in ontology):
        onto_clean = ontology.split("\n")
        ontology = ""
        for i in range(1, len(onto_clean)-1): # Skip first set of "```"
            if("```" in onto_clean[i]): # If second set found, don't append.
                break
            ontology += f"{onto_clean[i]}\n"
        ontology = ontology.replace(" .", " .\n")
        ontology = ontology.replace("\".", "\".\n")
        ontology = ontology.replace(";", ";\n")
    return ontology

def parse_results():
    '''
        Generates noun-specific directories with resultant TTL files
        provided the list of TSV in `resources`.
    '''
    for filename in os.listdir(input_path):
        name, ext = filename.split(".")
        noun_dir = os.path.join(output_path,name)
        # Organize turtle output per LLM generated noun ontologies to individual directory
        if(not os.path.exists(noun_dir)): 
            os.mkdir(noun_dir)

        with open(os.path.join(input_path, filename), "r") as inp:
            lines = [ line.strip() for line in inp.readlines() ]

        count = 0
        for line in lines:
            out_name = f"{name}{count}.ttl" # simple naming convention for unique noun ontology
            split = line.split("\t")
            index = 0
            for s in split:
                if("@" in s):
                    break
                index+=1
            try:
                ontology = split[index]
            except IndexError:
                continue
            out = open(os.path.join(noun_dir, out_name), "w")
            # Clean up ttl lines
            ontology = ontology.replace(" .", " .\n")
            ontology = ontology.replace("\".", "\".\n")
            ontology = ontology.replace(";", ";\n")
            ontology = ontology.replace("@@", "@")
            ontology = ontology.replace("resourceex", "resource\nex")
            ontology = ontology.replace("propertyex", "property\nex")
            ontology = ontology.replace("classex", "class\nex")
            ontology = ontology.replace("# Classes", "# Class\n")
            ontology = ontology.replace("# Properties", "# Properties\n")
            ontology = ontology.replace("# Individuals", "# Individuals\n")
            ontology = ontology.replace("\"ex:", "\"\nex:")

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
            # print(f"Writing to {out_name}")
            out.write(ontology)
            count+=1

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
    threshold = float(mean*votingLimit)
    if(propDict[key] >= threshold): 
        return True
    return False

def vote_properties():
    '''
        Attempts to parse through generated TTL files from LLM generation

        Uses rdflib Graph to generate s,p,o per TTL file
    '''
    #  Stats File Setup
    statsFile = open(os.path.join("./code/", "noun-valid-ttl-parsing-analysis.out"), "w")
    ## Stats File Formatting
    statsFile.write(f"noun: \t countOfValidFiles \t countOfTotalFiles \t Ratio Parsed (%) \n")
    statsValidDict = { filename.split(".")[0]: 0 for filename in os.listdir(input_path) }
    statsTotalDict = { filename.split(".")[0]: 0 for filename in os.listdir(input_path) }
    
    # predicate shortcut
    a = pfs["rdf"]["type"]

    # Property Types
    properties = [
        pfs["rdf"]["Property"],
        pfs["owl"]["ObjectProperty"],
        pfs["owl"]["DatatypeProperty"]
    ]
    
    for filename in os.listdir(input_path): # For each Noun
    # for i in range(1): # For testing 
    #     filename= "Month.tsv"
        noun, ext = filename.split(".")
        noun_dir = os.path.join(output_path,noun)
        
        fName = f"{noun}.out"
        analysisFile = open(os.path.join(analysis_path, fName), "w")
        graph = init_kg()

        # All occurences from all nouns
        nounPropertyDict = dict() 
        dictSPO = set()
        for filename in os.listdir(noun_dir): # For each ttl from single Noun
            statsTotalDict[noun] += 1 # Total available files

            ttlPropDict = dict() # Individual file occurrences per noun
            curr_graph = init_kg()
            with open(os.path.join(noun_dir, filename), "r") as f:
                try:
                    curr_graph.parse(f)
                    # print(filename)
                    #  Counting Individual File Occurrences
                    for sub,p,obj in curr_graph:
                        if("rdf" in p): #Skip RDF properties
                            continue 
                        if("owl" in p): #Skip OWL properties
                            continue 
                        if(isinstance(obj, Literal)):
                            continue                        
                        temp = p.split("/")[-1]
                        # if("#" in p): # can include RDF properties, if necessary
                        #     p = p.split("#")[-1].strip()

                        if(f"{noun}#" in p):
                            temp = temp.split("#")[-1]

                        # Skip or Increment Count of Found Properties
                        if(str(temp) in ttlPropDict): # Skip over found property
                            continue
                        else:
                            ttlPropDict[str(temp)] = 1
                            dictSPO[p] = [sub, obj]

                    #  Identifying Type Properties in Noun Ontology
                    for property in properties:
                        for s,p,o in (curr_graph.triples( (None, pfs["rdf"]["type"], property) )):
                            ##  Adding range of properties
                            for _,_,propRange in curr_graph.triples((s, RDFS.range, None)):
                                # print(str(s), str(p), str(o))
                                ##  Skip datatypes
                                if("xsd" in propRange or 
                                    "XML" in propRange or
                                    "Literal" in propRange):
                                    continue
                                ## Skip already added
                                graph.add( (propRange, a, pfs["rdfs"]["Class"]) )
                                graph.add( (s, RDFS.range, propRange) )

                            ##  Adding domain of properties
                            for _, _, propDomain in curr_graph.triples( (s, RDFS.domain, None) ):
                                # print(str(s), str(p), str(o))
                                ##  Skip datatypes
                                if("xsd" in propDomain or 
                                    "XML" in propDomain or
                                    "Literal" in propRange):
                                    continue
                                ## Skip already added
                                graph.add( (propDomain, a, pfs["rdfs"]["Class"]) )
                                graph.add( (s, RDFS.range, propDomain) )

                except ParserError:
                    continue # Error parsing file
                    # print("Error: " + filename)
                except Exception as ex:
                    continue 

                for k,v in ttlPropDict.items(): # Add each noun-file to overall property tracker
                    if(k in nounPropertyDict): # Increment past observed properties
                        nounPropertyDict[k] += v
                    else: # Set {k,v} for identifying properties in noun
                        nounPropertyDict[k] = 1    
            
            # Stats File
            statsValidDict[noun] += 1

        # Voting to add to noun

        for key, value in nounPropertyDict.items():
            sub = value[0]
            pred = key
            obj = value[1]
            # print(f"{sub} \t {pred} \t {obj}")
            property = pred.split("/")[-1].split("#")[-1]
            if(voting_helper(nounPropertyDict, property)):
                graph.add( (sub, pred, obj) )
        try:
            serialization(noun, graph)
        except Exception as ex:
            print(noun)
        #  Sort in descending value order for output
        nounPropertyDict = {k: v for k, v in sorted(nounPropertyDict.items(), key=lambda item: item[1], reverse=True)}
        for key, value in nounPropertyDict.items():
            analysisFile.write(f"{key} \t {value}\n")

    #  Sort in ascending key order for output
    statsValidDict = dict(sorted(statsValidDict.items()))
    for key,value in statsValidDict.items():
        try:
            ratioUsed = round(float(value/statsTotalDict[key]),2) * 100 # represent as percentage
            statsFile.write(f"{key}: \t {value}  \t {statsTotalDict[key]} \t {ratioUsed}\n")
        except Exception as ex:
            pass


if __name__ == "__main__":
    parse_results()
    vote_properties()
