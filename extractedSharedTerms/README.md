# Extracted Shared Terms
Analysis output results of overlap analysis of cs-modl and enslaved-modl are located in this sub-directory.  The analysis consists of analysing each pattern within the respective MODL for overlap of Classes/Concepts and Relationships/Properties, and an analysis between both MODLs for overlap.

## Directory Structure
* `enslaved-modl` -- copy of the enslaved-modl for ease of use
* `output` -- output files of the overlap analysis
    * `...classTermCounts.tsv` & `...PropTermCounts` -- Analysis of Classes/Concepts or Relationships/Properties represented in either cs-modl (`csmodl`) or enslaved-modl (`enslaved`) or both (`shared`).  Columns represent (a) the Term itself, (b) Count of Apperance from other patterns, (c) The Patterns the Term can be found in.
    * `...ClassTerms.tsv` & `...PropTerms.tsv` -- Analysis of Classes/Concepts or Relationships/Properties represented in either cs-modl (`csmodl`) or enslaved-modl (`enslaved`) or both (`shared`).  Columns represented (a) the Term, (b) the TTL file the Term can be found in, (c) Boolean Flag for the Term's appearance (was used as an auxillary variable within the scripted code)