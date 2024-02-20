import os

output_path = "./code/output/"
input_path = "./code/resources/"

def markdown_cleanup(ontology):
    ''''
        Helper cleanup function specifically for markdown codeblock tags
    '''
    ontology = ontology.replace("```turtle","\n")
    ontology = ontology.replace("```@","\n@")
    ontology = ontology.replace(".```",".\n```")
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
        
            if("[" in ontology):
                try:
                    ontology += split[index+1]
                except IndexError:
                    pass

            if("```" in ontology):
                ontology = markdown_cleanup(ontology)
            ontology = ontology.replace('\n\n', '\n')

            #  Write to individual file
            print(f"Writing to {out_name}")
            out.write(ontology)
            count+=1

def count_properties():
    # for filename in os.listdir(input_path):
    for i in range(1):
        filename= "Air.tsv"
        name, ext = filename.split(".")
        noun_dir = os.path.join(output_path,name)



if __name__ == "__main__":
    parse_results()