import os
##### Graph stuff
import rdflib
from rdflib import URIRef, Graph, Namespace, Literal
from rdflib import OWL, RDF, RDFS, XSD, TIME

summary = []
csmodl_patterns_folder = os.path.join(".", "csmodl", "patterns")
enslaved_patterns_folder = os.path.join(".", "enslaved-modl", "patterns")
keynotions_patterns_folder = os.path.join(".", "construct-patterns")
output_folder = os.path.join(".", "extractedSharedTerms", "output")

# Prefixes
name_space = "https://kastle-lab.org/"
pfs = {
"kl-res": Namespace(f"{name_space}lod/resource/"),
"kl-ont": Namespace(f"{name_space}lod/ontology/"),
"geo": Namespace("http://www.opengis.net/ont/geosparql#"),
"geof": Namespace("http://www.opengis.net/def/function/geosparql/"),
"sf": Namespace("http://www.opengis.net/ont/sf#"),
"wd": Namespace("http://www.wikidata.org/entity/"),
"wdt": Namespace("http://www.wikidata.org/prop/direct/"),
"dbo": Namespace("http://dbpedia.org/ontology/"),
"time": Namespace("http://www.w3.org/2006/time#"),
"ssn": Namespace("http://www.w3.org/ns/ssn/"),
"sosa": Namespace("http://www.w3.org/ns/sosa/"),
"cdt": Namespace("http://w3id.org/lindt/custom_datatypes#"),
"ex": Namespace("https://example.com/"),
"rdf": RDF,
"rdfs": RDFS,
"xsd": XSD,
"owl": OWL,
"time": TIME
}

# URIs of Class Representation
classURIs = [URIRef("http://www.w3.org/2002/07/owl#Class"),
            URIRef('http://www.w3.org/2000/01/rdf-schema#Class')]

# URIs of Relationship/Property Representation
propURIs = [
    pfs["rdf"]["Property"],
    pfs["owl"]["ObjectProperty"],
    pfs["owl"]["DatatypeProperty"]
]

def process_rdf_file(directory):
    '''
        Processes a directory of TTL files with RDFLib Graph
        Returning lists of identified classes and properties 
        being used for the particular directory of TTL files.
    '''
    classTerms = []
    uniqueClassTerms = []
    propTerms = []
    uniquePropTerms = []

    # filename="Issue.ttl"
    # for i in range(1):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
     
        if os.path.isfile(file_path):
            g = Graph()
            g.parse(file_path, format='turtle')  # Adjust format as needed

            for s, p, o in g.triples((None, RDF.type, None)):
                # entered = False #debug
                if o in classURIs: # Class Representation was found
                    # entered = True
                    term = s.split('/')[-1]
                    term = term.split("#")[-1]
                    if term not in uniqueClassTerms:
                        classTerms.append(f"{term}\t{filename}")
                        uniqueClassTerms.append(term)
                    else:
                        for i in range(len(classTerms)):
                            if f"{term}\t{filename}" not in classTerms:
                                classTerms.append(f"{term}\t{filename}")
                                break

                elif o in propURIs: # Relationship/Property Representation was found
                    # entered = True
                    property = s.split('/')[-1]
                    property = property.split("#")[-1]
                    if property not in uniquePropTerms:
                        propTerms.append(f"{property}\t{filename}")
                        uniquePropTerms.append(property)
                    else:
                        for i in range(len(propTerms)):
                            if f"{property}\t{filename}" not in classTerms:
                                propTerms.append(f"{property}\t{filename}")
                                break

            ##  Occasionally, LLM materialization resulted in identifying a SCO
            ##  without initializing the object as a Class first (see: cs-modl/Story.ttl)
            for s, p, o in g.triples((None, URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)):
                    term = o.split('/')[-1]
                    term = term.split("#")[-1]
                    if term not in uniqueClassTerms:
                        # print(f"Object as SCO in {filename}:")
                        # print(f"{s}\t{o}")
                        classTerms.append(f"{term}\t{filename}")
                        uniqueClassTerms.append(term)
                    else:
                        for i in range(len(classTerms)):
                            if f"{term}\t{filename}" not in classTerms:
                            # if term in classTerms[i] and filename not in classTerms[i]:
                                classTerms.append(f"{term}\t{filename}")
                                break
                # Other Types that can be found include:
                # - Instantiation:  some thing is of type ClassA)
                # - Ontology Representation
                # if(not entered):
                #     if(o == URIRef("http://www.w3.org/2002/07/owl#Ontology")):
                #         continue
                #     print(f"{s}\t{p}\t{o}")
    return classTerms, uniqueClassTerms, propTerms, uniquePropTerms

def countClassTerms(classTerms, propTerms):
    '''
        Counts occurrence of unique class and property terms used
        
        Returns a dictionary of 
            - Key: term used for classes and properties
            - Values: Count of term occurrence, and what TTL the term was used in
    '''
    # Create a dictionary to count class terms
    classTerm_counts = {}
    for term in classTerms:
        term_name = term.split("\t")[0]
        filename = term.split("\t")[1].split(".")[0]

        if term_name in classTerm_counts:
            classTerm_counts[term_name][0] += 1
            classTerm_counts[term_name][1].append(filename)
            classTerm_counts[term_name][1].sort()
        else:
            classTerm_counts[term_name] = [1, [filename]]
    
    # Create a dictionary to count property terms
    propTerm_counts = {}
    for term in propTerms:
        term_name = term.split("\t")[0]
        filename = term.split("\t")[1].split(".")[0]
        if term_name in propTerm_counts:
            propTerm_counts[term_name][0] += 1
            propTerm_counts[term_name][1].append(filename)
            propTerm_counts[term_name][1].sort()
        else:
            propTerm_counts[term_name] = [1, [filename]]

    return classTerm_counts, propTerm_counts

def idSharedTerms(classTerm_counts, propTerm_counts):
    '''
        Helper function to return class and property terms
        when used more than once
        Returns list of identified shared terms of classes and properties.
    '''
    sharedClasses = []
    for term in classTerm_counts:
        if classTerm_counts[term][0] > 1:
            sharedClasses.append(term)

    sharedProps = []
    for term in propTerm_counts:
        if propTerm_counts[term][0] > 1:
            sharedProps.append(term)

    return sharedClasses, sharedProps

def writeTermFiles(pattern_name, classTerms, classTerm_counts, propTerms, propTerms_counts):
    '''
        Helper function to write progress of program into files
        {Class or Prop}Terms consists of all terms used in any particular TTL file
        {class or prop}TermCounts consists of all terms and the count of occurrence, along with which TTL file
    '''
    with open(f"{output_folder}/{pattern_name}/{pattern_name}_ClassTerms.tsv", "w") as file:
        for term in classTerms:
            file.write(f"{term}\n")
        file.close()

    with open(f"{output_folder}/{pattern_name}/{pattern_name}_classTermCounts.tsv", "w") as file:
        classTerm_counts = dict(sorted(classTerm_counts.items(), key=lambda item: item[1][0], reverse=True))
        for term in classTerm_counts:
          if classTerm_counts[term][0] > 1:
               file.write(f"{term}\t{classTerm_counts[term]}\n")
    file.close()    

    with open(f"{output_folder}/{pattern_name}/{pattern_name}_PropTerms.tsv", "w") as file:
        for term in propTerms:
            file.write(f"{term}\n")
    file.close()

    with open(f"{output_folder}/{pattern_name}/{pattern_name}_PropTermCounts.tsv", "w") as file:
     propTerms_counts = dict(sorted(propTerms_counts.items(), key=lambda item: item[1][0], reverse=True))
     for term in propTerms_counts:
          if propTerms_counts[term][0] > 1:
               file.write(f"{term}\t{propTerms_counts[term]}\n")
    file.close()

##  CS MODL Analysis
csmodl_ClassTerms, csmodl_uniqueClassTerms, csmodl_PropTerms, csmodl_uniquePropTerms = process_rdf_file(csmodl_patterns_folder)
csmodl_classTerms_counts, csmodl_propTerms_counts = countClassTerms(csmodl_ClassTerms, csmodl_PropTerms)
csmodl_sharedClass, csmodl_sharedProps = idSharedTerms(csmodl_classTerms_counts, csmodl_propTerms_counts)

writeTermFiles("csmodl", csmodl_ClassTerms, csmodl_classTerms_counts, csmodl_PropTerms, csmodl_propTerms_counts)
print("CSMODL:")
print(f"shared classTermCounts: {len(csmodl_sharedClass)}")
print(f"uniqueClassTerms: {len(csmodl_uniqueClassTerms)}")
print(f"shared propTermCounts: {len(csmodl_sharedProps)}")
print(f"uniquePropTerms: {len(csmodl_uniquePropTerms)}")
print("")

##  Enslaved MODL Analysis
enslaved_ClassTerms, enslaved_uniqueClassTerms, enslaved_PropTerms, enslaved_uniquePropTerms = process_rdf_file(enslaved_patterns_folder)
enslaved_classTerms_counts, enslaved_propTerms_counts = countClassTerms(enslaved_ClassTerms, enslaved_PropTerms)
enslaved_sharedClasses, enslaved_sharedProps = idSharedTerms(enslaved_classTerms_counts, enslaved_propTerms_counts)

writeTermFiles("enslaved", enslaved_ClassTerms, enslaved_classTerms_counts, enslaved_PropTerms, enslaved_propTerms_counts)
print("Enslaved:")
print(f"shared classTermCounts: {len(enslaved_sharedClasses)}")
print(f"uniqueClassTerms: {len(enslaved_uniqueClassTerms)}")
print(f"shared propTermCounts: {len(enslaved_sharedProps)}")
print(f"uniquePropTerms: {len(enslaved_uniquePropTerms)}")
print("")

##  Key-Notions from CQs Analysis
keynotions_ClassTerms, keynotions_uniqueClassTerms, keynotions_PropTerms, keynotions_uniquePropTerms = process_rdf_file(keynotions_patterns_folder)
keynotions_classTerms_counts, keynotions_propTerms_counts = countClassTerms(keynotions_ClassTerms, keynotions_PropTerms)
keynotions_sharedClasses, keynotionsd_sharedProps = idSharedTerms(keynotions_classTerms_counts, keynotions_propTerms_counts)

writeTermFiles("keynotions", keynotions_ClassTerms, keynotions_classTerms_counts, keynotions_PropTerms, keynotions_propTerms_counts)
print("Key-Notions:")
print(f"shared classTermCounts: {len(keynotions_sharedClasses)}")
print(f"uniqueClassTerms: {len(keynotions_uniqueClassTerms)}")
print(f"shared propTermCounts: {len(keynotionsd_sharedProps)}")
print(f"uniquePropTerms: {len(keynotions_uniquePropTerms)}")
print("")

##### End of MODL file parsing #####
# csmodl union enslavedmodl
# Initialize lists to store shared terms
shared_classTerms = []
shared_propTerms = []
unique_classTerms = set(csmodl_uniqueClassTerms) | set(enslaved_uniqueClassTerms)
unique_propTerms = set(csmodl_uniquePropTerms) | set(enslaved_uniquePropTerms)

# Find shared class terms and calculate total counts
for term in csmodl_classTerms_counts:    
    if term in enslaved_classTerms_counts:
        enslavedCount = enslaved_classTerms_counts[term][0]
        enslavedTerms = enslaved_classTerms_counts[term][1]
        csmodlCount = csmodl_classTerms_counts[term][0]
        csmodlTerms = csmodl_classTerms_counts[term][1]
        totalCount = csmodlCount + enslavedCount

        shared_classTerms.append(f"{term}\t{csmodlCount}\t{csmodlTerms}\t{enslavedCount}\t{enslavedTerms}\t{totalCount}")

# Find shared property terms and calculate total counts
for term in csmodl_propTerms_counts:
    if term in enslaved_propTerms_counts:
        enslavedCount = enslaved_propTerms_counts[term][0]
        enslavedTerms = enslaved_propTerms_counts[term][1]
        csmodlCount = csmodl_propTerms_counts[term][0]
        csmodlTerms = csmodl_propTerms_counts[term][1]
        totalCount = csmodlCount + enslavedCount
        shared_propTerms.append(f"{term}\t{csmodlCount}\t{csmodlTerms}\t{enslavedCount}\t{enslavedTerms}\t{totalCount}")


# Write shared class terms to a file
with open(f"{output_folder}/across-modls/shared_classTerms.tsv", "w") as file:
    file.write("Term\tCS-MODL Count\tCS-MODL Files\tEnslaved-MODL Count\tEnslaved-MODL Files\tTotal Count\n")
    for term in shared_classTerms:
        file.write(f"{term}\n")

# Write shared property terms to a file
with open(f"{output_folder}/across-modls/shared_propTerms.tsv", "w") as file:
    file.write("Term\tCS-MODL Count\tCS-MODL Files\tEnslaved-MODL Count\tEnslaved-MODL Files\tTotal Count\n")
    for term in shared_propTerms:
        file.write(f"{term}\n")
print("Across MODLs:")
print(f"shared classTermCounts: {len(shared_classTerms)}")
print(f"uniqueClassTerms: {len(unique_classTerms)}")
print(f"shared propTermCounts: {len(shared_propTerms)}")
print(f"uniquePropTerms: {len(unique_propTerms)}")
print("")


#  MODLs Intersection with LLM(KN(CQs))
modl_classTerms = set(unique_classTerms)
keynotions_ClassTerms = set(keynotions_uniqueClassTerms)
class_intersect = sorted(modl_classTerms.intersection(keynotions_uniqueClassTerms))

print(f"MODLs Classes: {len(modl_classTerms)}")
print(f"KN Classes: {len(keynotions_uniqueClassTerms)}")
print(f"Intersection: {len(class_intersect)}")
# for i in intersect:
#     print(i)

modl_propTerms = set(unique_propTerms)
keynotions_PropTerms = set(keynotions_uniquePropTerms)
prop_intersect = sorted(modl_propTerms.intersection(keynotions_PropTerms))

print(f"MODLs Props: {len(modl_propTerms)}")
print(f"KN Props: {len(keynotions_PropTerms)}")
print(f"Intersection: {len(prop_intersect)}")

# Write intersection between MODL and Key Notions into file
with(open(os.path.join(f"{output_folder}/modls-with-kn", "modl-kn-intersect-classes.out"), "w")) as out:
    for i in class_intersect:
        out.write(f"{i}\n")
    
with(open(os.path.join(f"{output_folder}/modls-with-kn", "modl-kn-intersect-prop.out"), "w")) as out:
    for i in prop_intersect:
        out.write(f"{i}\n")
