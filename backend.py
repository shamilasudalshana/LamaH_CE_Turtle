from fastapi import FastAPI
from pydantic import BaseModel
from SPARQLWrapper import SPARQLWrapper, JSON

# Initialize FastAPI app
app = FastAPI()

# Define SPARQL endpoint (Replace with your Virtuoso endpoint URL)
SPARQL_ENDPOINT = "https://sparql.knowledgehub.test.n4e.geo.tu-dresden.de/"

class SPARQLQuery(BaseModel):
    query: str

@app.post("/run_sparql/")
async def run_sparql(sparql_query: SPARQLQuery):
    """
    Execute a SPARQL query and return results.
    """
    try:
        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        sparql.setQuery(sparql_query.query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results
    except Exception as e:
        return {"error": str(e)}
