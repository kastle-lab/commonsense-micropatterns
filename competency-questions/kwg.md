# KWG-Lite
1. Places that have been impacted by a Hazard.
2. Retrieve the following properties associated with a Hazard Event  
    1. affectedAreasInAcres (ONLY Fires have affected area) 
    2. numberOfDeaths (ONLY NOAA hazards have this information)
    3. damageToInfrastructureInDollars (ONLY NOAA hazards have this information)
    4. damageToCropsInDollars (ONLY NOAA hazards have this information)
3. Get all hazard events, their name, start date, end date, and KWG entity
    1. NOAA Hazards
    2. MTBS Fires
    3. MTBS Fires
    4. Earthquakes
4. Get all places, their name, and KWG entity
5. Get the following health attributes of places: percentObese, percentBelowPovertyLine, percentDiabetic
6. Get the following demographic attributes associated with a place hasPopulation, hasNumberOfHouseHolds
7. Get the following fire-specific attributes related to a place
    1. The query retrieves the number of fires ONLY from the NIFC datasets right now - numberOfFiresImpactingPlace2021 (this query is altered to extract all data for the last 5 yrs)
    2. Dollar damage is calculated on the kwg-ont:NOAAWildfire, because that is the only dataset that records financial loss/impact
  8. Get the following hurricane-specific attributes relate to a place
    1. numberOfHurricanesImpactingPlace2021
    2. numberOfHurricanesImpactingPlace2021 (NOAAHurricane and NOAAMarinelHurricaneTyphoon)
    3. dollarDamageOfHurricanesImpactingPlace2021
9. Number of earthquakes
10. Get the following tornado-specific attributes related to a a place
    1. numberOfTornadoesImpactingPlace2021 (this query is altered to extract all data for the last 5 yrs)
    2. Dollar damage (this query is altered to extract all data for the last 5 yrs)
11. Get the following storm-specific attributes related to a a place:
    1. Number of storm surges (this query is altered to extract all data for the last 5 yrs)
    2. Dollar damage (this query is altered to extract all data for the last 5 yrs)
12. Get the following flood-specific attributes related to a a place:
    1. numberOfFloodsImpactingPlace2021 (this query is altered to extract all data for the last 5 yrs)
    2. dollarDamageOfFloodsImpactingPlace2021 (this query is altered to extract all data for the last 5 yrs)
13. Get the following landslide-specific attributes related to a a place:
    1. numberOfDebrisFlowEventsImpactingPlace2021 (this query is altered to extract all data for the last 5 yrs)
    2. dollarDamageOfDebrisFlowEventsImpactingPlace2021 (this query is altered to extract all data for the last 5 yrs)
14. Get the following climate-specific attributes related to a a place
    1. averageHeatingDegreeDaysPerMonth
    2. averageCoolingDegreeDaysPerYear
    3. averageMonthlyTemperatureInCelsius
    4. maximumMonthlyTemperatureInCelsius
    5. minimumMonthlyTemperatureInCelsius
15. Get all places and spatial relationships with each other
16. Get all fires and the type of Fire
    1. All
    2. MTBS fire
    3. NIFC Fire
17. Get all hurricanes
18. Get all tornadoes
19. Get all earthquakes
20. Get all place types
    1. US Climate Division
    2. Sub National
    3. US Census District (Metropolitan Micropolitan Statistical Area)
    4. Zip Code Area
    5. Federal Judicial District
    6. National Weather Zone
# KWG
## Direct Relief
### Expertise
1. What Disaster/Hazard Types have identified Experts?
2. What is the Expertise Area of an Expert?
3. Where—Show me all Experts with experience in specific regions?
4. When—Show me all Experts with recent experience with Disaster Type X?
5. What are the Types of Expertise available for querying in the KWG?
6. Can I export Data from the KWG in some useable format like CSV?
7. Can I contribute “value-added” data back into the KWG?
8. How many Experts are documented in the KWG?

### Hurricane
1. What are the sources of Disaster/Hazard Events included in the KWG?
2. Where--what is the geospatial extent of Disaster/Hazard Events in KWG?
3. When-- what is the time-scale of Disaster/Hazard Events included in the KWG?
4. What specific aspects of Disaster/Hazard Events is available in the KWG?
5. Can I export Data from the KWG in some useable format like CSV?
6. Can I contribute “value-added” data back into the KWG?
7. Where do Floods happen most frequently in Louisiana between 1980-2020?
8. Query on “Hurricane” will find Data/Information about “Typhoon”?
9. Use {FEMA | GACS | GLIDE | NOAA} Event Identifier to find information about THE SAME EVENT from  other {FEMA | GACS | GLIDE | NOAA} Data Sources?

## Farm2Table
1. At a given point in time, where are wildfires occurring in California?
2. What regions are being affected by dense smoke and potential ash fall?
    1. In these regions, are there agricultural lands that will be affected?
    2. What types of crops are growing there?
  3. How will the current fires and associated smoke plumes affect the quality and quantity of lettuce produced in the Salinas Valley? (county?)
  4. Who will be affected by these shortages?
 
## FMI
