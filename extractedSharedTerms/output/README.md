# Output
Sub-directory containing output of analysis from scripts found from `./code`

## Directory Structure
* `output` -- output files of the overlap analysis
    * `...classTermCounts.tsv` & `...PropTermCounts` -- Analysis of Classes/Concepts or Relationships/Properties represented in either cs-modl (`csmodl`) or enslaved-modl (`enslaved`) or both (`shared`).  Columns represent (a) the Term itself, (b) Count of Apperance from other patterns, (c) The Patterns the Term can be found in.
    * `...ClassTerms.tsv` & `...PropTerms.tsv` -- Analysis of Classes/Concepts or Relationships/Properties represented in either cs-modl (`csmodl`) or enslaved-modl (`enslaved`) or both (`shared`).  Columns represented (a) the Term, (b) the TTL file the Term can be found in, (c) Boolean Flag for the Term's appearance (was used as an auxillary variable within the scripted code)
    * `connected-concept/`-- A directory containing a file for each Pattern used as a Root node when exploring connected components via Class Term
    * `connected-concept.txt` -- Output file containing a full overview of the Root pattern in use and the count of other micropatterns the Root was able to connect to