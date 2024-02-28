import sys
import os
from rdflib import URIRef, Graph, Namespace, Literal
from rdflib import OWL, RDF, RDFS, XSD, TIME

#  Directories
input_path = "../data/prompt-results"
output_path = "../data/extracted-patterns"
analysis_path = "../data/pattern-analysis"
pattern_path = "../csmodl/patterns"

# Prefix Configurations
name_space = "https://kastle-lab.org/"
opla_namespace = "https://archive.org/services/purl/purl/modular_ontology_design_library#"

pfs = {
"": Namespace(f"{opla_namespace}"),
"kl-res": Namespace(f"{name_space}lod/resource/"),
"kl-ont": Namespace(f"{name_space}lod/ontology/"),
"rdf": RDF,
"rdfs": RDFS,
"xsd": XSD,
"owl": OWL,
"time": TIME,
"dc": Namespace("http://purl.org/dc/elements/1.1/"),
"opla": Namespace("http://ontologydesignpatterns.org/opla#"),
"opla-core": Namespace("http://ontologydesignpatterns.org/opla-core#"),
"opla-sd": Namespace("http://ontologydesignpatterns.org/opla-sd#"),
"opla-cp": Namespace("http://ontologydesignpatterns.org/opla-cp#")
}

# Property Shortcuts
a = pfs["rdf"]["type"]


def init_kg(prefixes=pfs):
    kg = Graph()
    for prefix in pfs:
        kg.bind(prefix, pfs[prefix])
    return kg

def generate_index():
    graph = init_kg()
    result_files = os.listdir(pattern_path)
    result_files.sort()

    # Noun CSMODL Ontology 
    ## Minting URIs
    noun_ontology = f"{opla_namespace}"
    noun_onto_uri = Namespace(noun_ontology)[""]
    pattern_uri = Namespace(noun_ontology)["Pattern"]
    ## Bind
    graph.add( (noun_onto_uri, a, OWL.Ontology) )
    graph.add( (noun_onto_uri, pfs["opla-core"]["hasPatternName"], Literal("Commonsense Modular Ontology Design Library")) )

    
    for filename in result_files: # For each Noun
        if(os.path.isdir(os.path.join(pattern_path, filename))):
            continue
        noun, ext = filename.split(".")
        # Mint a Noun Pattern
        noun_pattern_uri = Namespace(noun_ontology)[f"{noun}"]
        # Bind
        graph.add( (noun_pattern_uri, a, OWL.NamedIndividual) )
        graph.add( (noun_pattern_uri, a, pattern_uri) )

    output_name = "csmodl.owl"
    output_path = os.path.join("../csmodl", output_name)
    graph.serialize(format="turtle", encoding="utf-8", destination=output_path)

if __name__ == "__main__":
    generate_index()