from langchain_core.prompts.prompt import PromptTemplate

# SPARQL query generation prompt
SPARQL_GENERATION_SELECT_TEMPLATE = """Task: Generate a SPARQL SELECT query for a Virtuoso triple store.

Instructions:
1. Extract only entities and relations from the provided schema.
2. Verify entity existence before constructing the query.
3. Ensure the query returns readable labels in English.

Schema:
{schema}

The question is:
{prompt}
"""

SPARQL_GENERATION_SELECT_PROMPT = PromptTemplate(
    input_variables=["schema", "prompt"], template=SPARQL_GENERATION_SELECT_TEMPLATE
)
