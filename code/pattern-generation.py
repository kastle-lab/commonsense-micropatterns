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

    for filename in os.listdir(input_path): # For each Noun
    # for i in range(1): 
        # filename= "Air.tsv"
        name, ext = filename.split(".")
        noun_dir = os.path.join(output_path,name)
        
        fName = f"{name}.out"
        analysisFile = open(os.path.join(analysis_path, fName), "w")
        graph = Graph()
        propertyDict = dict()
        for filename in os.listdir(noun_dir): # For each ttl from single Noun
            with open(os.path.join(noun_dir, filename), "r") as f:
                try:
                    graph.parse(f)
                    for _,p,_ in graph:
                        if("rdf" in p): #Skip RDF properties
                            continue 
                        p = p.split("/")[-1]
                        if("#" in p):
                            p = p.split("#")[-1].strip()
                        if(str(p) in propertyDict):
                            propertyDict[str(p)] += 1
                        else:
                            propertyDict[str(p)] = 1
                except Exception:
                    pass
                    # print("Error: " + filename)

        propertyDict = {k: v for k, v in sorted(propertyDict.items(), key=lambda item: item[1], reverse=True)}
        for key, value in propertyDict.items():
            analysisFile.write(f"{key} \t {value}\n")
        

if __name__ == "__main__":
    parse_results()
    count_properties()