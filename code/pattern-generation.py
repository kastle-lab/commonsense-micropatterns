import os
from rdflib import URIRef, Graph, Namespace, Literal
from rdflib import OWL, RDF, RDFS, XSD, TIME
import re
output_path = "./code/output/"
input_path = "./code/resources/"
analysis_path = "./code/analysis/"

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

def count_properties():
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
    
    for filename in os.listdir(input_path): # For each Noun
    # for i in range(1): # For testing 
    #     filename= "Air.tsv"
        noun, ext = filename.split(".")
        noun_dir = os.path.join(output_path,noun)
        
        fName = f"{noun}.out"
        analysisFile = open(os.path.join(analysis_path, fName), "w")
        graph = Graph()
        propertyDict = dict() # All occurences from all nouns

        for filename in os.listdir(noun_dir): # For each ttl from single Noun
            statsTotalDict[noun] += 1 # Total available files

            nounPropDict = dict() # Individual file occurrences per noun
            with open(os.path.join(noun_dir, filename), "r") as f:
                try:
                    graph.parse(f)
                    for _,p,_ in graph:
                        if("rdf" in p): #Skip RDF properties
                            continue 
                        if("owl" in p): #Skip OWL properties
                            continue 
                        p = p.split("/")[-1]
                        # if("#" in p): # can include RDF properties, if necessary
                        #     p = p.split("#")[-1].strip()

                        if(f"{noun}# in p"):
                            p = p.split("#")[-1]

                        # Skip or Increment Count of Found Properties
                        if(str(p) in nounPropDict): # Skip over found property
                            continue
                        else:
                            nounPropDict[str(p)] = 1
                except Exception:
                    continue
                    # print("Error: " + filename)

                for k,v in nounPropDict.items(): # Add each noun-file to overall property tracker
                    if(k in propertyDict): # Increment past observed properties
                        propertyDict[k] += v
                    else: # Set {k,v} for identifying properties in noun
                        propertyDict[k] = 1    
            statsValidDict[noun] += 1


        #  Sort in descending value order for output
        propertyDict = {k: v for k, v in sorted(propertyDict.items(), key=lambda item: item[1], reverse=True)}
        for key, value in propertyDict.items():
            analysisFile.write(f"{key} \t {value}\n")

    #  Sort in ascending key order for output
    statsValidDict = dict(sorted(statsValidDict.items()))
    for key,value in statsValidDict.items():
        ratioUsed = round(float(value/statsTotalDict[key]),2) * 100 # represent as percentage
        statsFile.write(f"{key}: \t {value}  \t {statsTotalDict[key]} \t {ratioUsed}\n")


if __name__ == "__main__":
    parse_results()
    count_properties()