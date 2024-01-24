# neo4j-arrows
Converts neo4j schema to arrows.app

This script extracts the schema of a neo4j graph and converts it to a json file that is directly importable to an [Arrows.app](https://arrows.app) graph

# Requirements
- neo4j BOLT url (user/password)
- apoc plugin in your neo4j dbms
- Python dependencies
  - neomodel
  - numpy
  - json
