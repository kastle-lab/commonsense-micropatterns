# Validation
## Template
Sparql Query
```sql
Select *
Where {
    
}
```
Bridged MODLs:

## Summary
41 Questions asked  
11 Answers

## Proto-OKN Projects
## Biology-Health
### SPOKE
1. What conditions can be inferred from the gene activity pattern of blood cells in space?
2. What drugs can counteract or minimize the effect of radiation in lower orbit and in outer space?
3. What are the most physiologically accurate Earth analogs of spaceflight?
4. What conditions on Earth most closely resemble long spaceflight missions?
5. How are food deserts associated with diabetes?
6. Where is air pollution most closely associated with lung cancer in non-smokers?

### BioBricks
1. Chemical identifier lookup: Look up the names of chemical entities and optionally their CAS RNand DSSTOXSID if available. Indicate which graph the data come from.
2. Assays by source: Look up assays from InvitroDB that are found in both ICE and ToxCast by graph (where the graph IRI corresponds to which dataset it is from).
3. Endpoint responses: Retrieves endpoint responses chemicals and assays. An endpoint response provides information about observed experimental outcomes when chemicals are tested in assays. Endpoint responses include the (often numeric) value itself and entities like units (eg. mg/kg).

### Bio-Health
"Predicate represents the relationship between two nodes in the knowledge graph. Subject node and object node is the start and the end node of a pair of relationships between two concepts we extracted from the datasets listed above. Predicate, subject node, and object node are pre-defined by Unified Medical Language System."
1. Find the concepts that cause 'Homelessness'

Sparql Query
```sql
Select *
Where {
    ?s ?p ?o .
    ?s a kastle:HomelessPerson .
}
```
Bridged MODLs: Proto-OKN KNs

2. Find the concepts that ‘occurs in’ 'Homeless Youth'
3. Find the concepts that affect the 'Homeless family'
4. Retrieve nodes connected by a 'METHOD_OF' relationship to nodes named 'Suicide prevention' - identify various methods of interventions that are aimed at preventing suicide
5. Find nodes that coexist with 'Suicide prevention' - look for other interventions, conditions, or factors that are typically associated with suicide prevention efforts.
6. Retrieve nodes that have an 'AFFECTS' relationship with 'Homeless persons'. This aims to discover factors that have a positive or negative impact on the existence or wellbeing of homeless individuals.
7. Identify what prevents 'Post-Traumatic’ conditions. It is focused on interventions or factors that could help in preventing post-traumatic events.
8. Finds nodes that have a 'COEXISTS_WITH' relationship with 'Housing problem'. This could help in identifying other issues or conditions that often occur alongside housing problems.
9. Identify nodes that have a 'CAUSES' relationship with 'Unemployment'. The goal is to explore different factors or conditions that may lead to or cause unemployment.

## Technology Manufacturing
### SUDOKN
1. Which suppliers in southern California can provide precision machining services for aerospace grade material?
2. What are the gaps in this area [selected on the map] in terms of Additive Manufacturing capabilities?

Sparql Query
```sql
Select *
Where {
    ?s kastle:hasCapability ?o .
    ?s a kastle:AdditiveManufacturing
}
```
Bridged MODLs: Proto-OKN KNs

3. What are the gaps in this area [selected on the map] in terms of skilled TIG (Tungsten Inert Gas) welders?

Sparql Query
```sql
Select *
Where {
    ?s ?p ?o .
    ?s a kastle:TigWelder .
    ?p a kastle:requiresSkill .
}
```
Bridged MODLs: Proto-OKN KNs

4. What are the existing supply chains for this particular product (with this UPC/GTIN)?

### Software Supply Chain
1. Does the Apache Struts framework have any known vulnerabilities?
2. What software libraries and packages are Apache Struts built upon?
3. Does Apache Struts depend on any software library or package, directly or transitively, that has a known vulnerability?
4. Which version of Apache Struts no longer has the Remote Code Execution vulnerability?

### CollabNext
1. As a principal investigator (or industry partner), I want to identify and contact colleagues (either at HBCUs/MSIs/emerging research institutions or at well-resourced institutions) with interest and expertise in specific research areas, so that I can build a stronger research team.

Sparql Query
```sql
Select ?person ?expertise
Where {
    ?person kastle:hasExpertise ?expertise .
    ?expertise a kastle:Expertise .
}
```
Bridged MODLs: Proto-OKN KNs

2. As a sponsoring agency program officer (or journal editor), I want to identify researchers who specialize in certain areas to serve as reviewers so I can expose more researchers to what successful submissions look like.

Sparql Query
```sql
Select *
Where {
    ?s kastle:hasSpeciality kastle:Specialty .
}
```
Bridged MODLs: Proto-OKN KNs

3. As a program or conference organizer, I want to curate a diverse panel of knowledgeable experts so that my event will engage a broader audience and have wider representation.

Sparql Query
```sql
Select ?person ?expertise
Where {
    ?person kastle:hasExpertise ?expertise .
    ?expertise a kastle:Expertise .
}
```
Bridged MODLs: Proto-OKN KNs

4. As a student applying to a grad program, I want to identify researchers with whom my interests and values align, so that I can find potential advisors at an institution.

Sparql Query
```sql
Select *
Where {
    ?person kastle:hasInterest ?interest .
}
UNION
Select *
Where {
    ?researcher kastle:hasResearchInterest ?res_interest .
}
```
Bridged MODLs: Enslaved-MODL, Proto-OKN KNs

5. As a graduate student or postdoc, I want to look for potential research collaborators within and outside my institution, so that I can strengthen my research network beyond my advisor.

Sparql Query
```sql
Select *
Where {
    ?person kastle:hasInterest ?interest .
}
UNION
Select *
Where {
    ?researcher kastle:hasResearchInterest ?interest .
}
```
Bridged MODLs: Enslaved-MODL, Proto-OKN KNs

6. As an administrator, I want to understand the current research capabilities and focus areas of faculty in my unit, so that I can visualize existing research networks, and see potential new collaborations, so that I can facilitate partnerships and advocate for additional resources.

## Justice
### Warehouse
"Queries can be made by incident type (e.g., fatal, non-fatal, location, time of dispatch, associated crime), victim characteristics (race/ethnicity, age, wound location), and census tract characteristics (poverty, racial composition, unemployment)."

### IJP
1. Querying all distinct judges

Sparql Query
```sql
Select *
Where {
    ?person a kastle:Judge .
}
```
Bridged MODLs: Enslaved-MODL

2. Querying all ontology event labels

Sparql Query
```sql
Select *
Where {
    ?s a kastle:EventClass .
    ?s kastle:eventName ?name
}
```
Bridged MODLs: Proto-OKN KNs, Enslaved KNs

3. Counting number of cases by type

Sparql Query
```sql
Select *
Where {
    ?s a kastle:Case .
}
```
Bridged MODLs: CS-MODL, Enslaved-MODL

### DreamKG
1. Target homeless service providers which provide multiple services
2. Hours available for the target homeless service providers
3. Multiple languages instead of just English
4. Hours available in the weekend
5. Cost free or not
