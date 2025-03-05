import requests
from SPARQLWrapper import SPARQLWrapper, JSON

# Configure Virtuoso SPARQL endpoint and authentication
VIRTUOSO_ENDPOINT = "https://sparql.knowledgehub.test.n4e.geo.tu-dresden.de/"
USER = "dba"
PASSWORD = "fsCy#@xh4hNM2E"

def query_sparql(sparql_query):
    """Executes a SPARQL query on Virtuoso and returns JSON results."""
    sparql = SPARQLWrapper(VIRTUOSO_ENDPOINT)
    
    # Set authentication manually (Virtuoso typically supports basic authentication)
    sparql.setCredentials(USER, PASSWORD)
    
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        return results
    except Exception as e:
        return {"error": str(e)}

# Test the connection
if __name__ == "__main__":
    test_query = "SELECT ?s ?p ?o WHERE {GRAPH <http://hydroturtle/LamahCE> {?s ?p ?q}} LIMIT 10"

    response = query_sparql(test_query)
    print(response)
