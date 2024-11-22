import os
import re
import queue

##### Graph stuff
import rdflib
from rdflib import URIRef, Graph, Namespace, Literal
from rdflib import OWL, RDF, RDFS, XSD, TIME

###  Directory Organization
modl = "enslaved"
folders = {
    "csmodl":os.path.join(".", "csmodl", "patterns"),
    "enslaved":os.path.join(".", "enslaved-modl", "patterns"),
    "keynotions":os.path.join(".", "construct-patterns"),
    "all-keynotions": os.path.join(".", "all-key-notions", "patterns")
}
folder = folders[modl]

output_folder = os.path.join(".", "extractedSharedTerms", "output")
if not os.path.exists(os.path.join(output_folder, modl, "connected-concept")):
    os.mkdir(os.path.join(output_folder, modl, "connected-concept"))
output_folder = os.path.join(output_folder, modl, "connected-concept")


a = RDF.type

def extract_concepts(g:Graph):
    '''
        Helper method to modularize concept extraction
        Returns a set of concepts collected from a particular pattern/graph
    '''
    concept_collection = set()

    for s, p, o in g.triples( (None, a, RDFS["Class"]) ):
        name = str(s).split("/")[-1].split("#")[-1]
        concept_collection.add(name)

    for s, p, o in g.triples( (None, a, OWL["Class"]) ):
        name = str(s).split("/")[-1].split("#")[-1]
        concept_collection.add(name)

    for s, p, o in g.triples( (None, RDFS["subClassOf"], None) ):
        name = str(o).split("/")[-1].split("#")[-1]
        concept_collection.add(name)
    
    return concept_collection

collected_connections = {}
patterns = sorted(os.listdir(folder))
root_pattern = queue.Queue()
traversal = queue.Queue()

for p in patterns:
    root_pattern.put(p)

while(not root_pattern.empty()):
    #  Initialize loop variables
    component_patterns = set()
    component_concepts = set()

    #  Set up traversal queue per root
    for p in patterns:
        traversal.put(p)

    #  Initialize root pattern to search
    root = root_pattern.get()
    root_name = root.split(".")[0]
    root_path = os.path.join(folder, root)
    if not os.path.isfile(root_path):
        continue
    g = Graph().parse(root_path)

    #  Extract initial root concepts
    concept_collection = set()
    concept_collection = extract_concepts(g)

    #  Initial start to allow for comparison
    component_patterns.add(root_path)
    component_concepts.update(concept_collection)
    collected_connections[root] = 1

    #  Stopping condition variables
    previous = -1
    traversal.put(root)

    #  Retrieve next pattern
    while not traversal.empty():
        pattern = traversal.get()
        if root == pattern: # Skip over the seeded root concept
            if previous == len(component_patterns):
                # If a full rotation has occured 
                # and no new concepts have been added, break
                break
            previous = len(component_patterns)
            traversal.put(root)
            continue
    
        pattern_path = os.path.join(folder, pattern)
        if not os.path.isfile(pattern_path):
            continue

        #  Compare previously gathered concepts with new concepts
        g = Graph().parse(pattern_path)
        concept_collection = extract_concepts(g)

        if len(component_concepts.intersection(concept_collection)) > 0:
        #  If there is an intersection of classes between previous iteration and current pattern
            component_concepts.update(concept_collection)
            component_patterns.add(pattern_path) # A pattern can connect
        else: # Pattern did not change outcome, look again later
            traversal.put(pattern) 
            continue
        
        #  Only care about path with largest connections
        if len(collected_connections) == 0 or collected_connections[root] < len(component_patterns):
            collected_connections[root] = len(component_patterns)

    print(f"{root}\t{len(component_concepts)}")
    with open(os.path.join(output_folder, f"{root_name}_component_concepts.out"), "w") as out:
        for concept in component_concepts:
            out.write(f"{concept}\n")

    with open(os.path.join(output_folder, f"{root_name}_component_patterns.out"), "w") as out:
        for pattern in component_patterns:
            out.write(f"{pattern}\n")

output_folder = os.path.join(".", "extractedSharedTerms", "output", modl)
collected_connections = dict(sorted(collected_connections.items(), key=lambda item: item[1], reverse=True))
with open(os.path.join(output_folder, "connected-concept.txt"), "w") as out:
    for connection in collected_connections:
        out.write(f"{connection}\t{collected_connections[connection]}\n")

