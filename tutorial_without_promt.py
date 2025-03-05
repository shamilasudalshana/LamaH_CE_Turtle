import os
from langchain_openai import ChatOpenAI
from execute_sparql import query_sparql
from dotenv import load_dotenv

# take open AI API key from the env variables
load_dotenv() # to load all the env variables form the env variables
open_ai_api_key = os.getenv("OPENAI_API_KEY")

open_ai_model = "ft:gpt-4o-2024-08-06:personal::Ay6V9DlJ" #this is the fine tuned model with 10 questions.
#"ft:gpt-4o-2024-08-06:personal::Ay6V9DlJ" - this is the fine tuned model with 10 questions. 
# "ft:gpt-4o-2024-08-06:personal::B7JJuV3V" # fine tune models with 15 quesions on 2025_03_14. 

# Initialize OpenAI model
llm = ChatOpenAI(model=open_ai_model, temperature=0, api_key=open_ai_api_key) #gpt-4o, gpt-3.5-turbo, gpt-4o-mini-2024-07-18


def clean_sparql_query(sparql_query, named_graph):
    """Fixes common LLM errors in SPARQL query generation."""
    
    # 1️. Remove unnecessary SELECT ?s ?p ?o WHERE wrappers
    if "SELECT ?s ?p ?o WHERE" in sparql_query:
        sparql_query = sparql_query.replace("SELECT ?s ?p ?o WHERE {", "").rstrip("}")

    # 2️. Fix incorrect nested COUNT queries
    if "SELECT (COUNT(?sensor) AS ?sensorCount)" in sparql_query:
        sparql_query = sparql_query.replace("SELECT (COUNT(?sensor) AS ?sensorCount)", "SELECT (COUNT(*) AS ?count)")

    # 3️. Ensure PREFIX is correctly included
    if "sosa:Sensor" in sparql_query and "PREFIX sosa: <http://www.w3.org/ns/sosa/>" not in sparql_query:
        sparql_query = f"PREFIX sosa: <http://www.w3.org/ns/sosa/>\n{sparql_query}"

    # 4️. Ensure correct GRAPH placement
    if f"GRAPH <{named_graph}>" not in sparql_query:
        sparql_query = sparql_query.replace("WHERE {", f"WHERE {{ GRAPH <{named_graph}> {{") + " } }"

    # 5. Remove any lingering Markdown formatting
    sparql_query = sparql_query.replace("```sparql", "").replace("```", "").strip()

    # 6. Fix mismatched braces `{}` by checking the counts
    open_braces = sparql_query.count("{")
    close_braces = sparql_query.count("}")

    if open_braces > close_braces:
        sparql_query += "}" * (open_braces - close_braces)  # Add missing `}`
    elif close_braces > open_braces:
        sparql_query = sparql_query.rstrip("}")  # Remove extra closing `}`

    # 7. Fix nested queries: Ensure correct referencing of subquery results
    sparql_query = sparql_query.replace("WHERE { {", "WHERE {").replace("} } }", "} }")

    return sparql_query.strip()


# def generate_sparql(question, named_graph):
#     """Uses OpenAI to generate a structured SPARQL query, ensuring correctness."""

#     prompt = f"""
#     You are an expert in querying RDF datasets using SPARQL. Your task is to convert the following natural language question into a **correct** and **well-structured** SPARQL query.

#     ### **Guidelines**
#     1. **Use Correct Prefixes**
#        - `PREFIX sosa: <http://www.w3.org/ns/sosa/>`
#        - `PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/>`
#        - `PREFIX qudt: <https://qudt.org/schema/qudt/>`
#        - `PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`
#        - `PREFIX unit: <https://qudt.org/vocab/unit/>`
#        - `PREFIX schema: <https://schema.org/>`
#        - `PREFIX locn: <http://www.w3.org/ns/locn#>`
#        - `PREFIX geo: <http://www.opengis.net/ont/geosparql#>`

#     2. **Follow Correct Data Structure**
#        - Observations are modeled using `sosa:Observation`.
#        - The observed property is linked using `sosa:observedProperty`.
#        - The result is linked using `sosa:hasResult` (not `sosa:result`).
#        - The numeric value of the result is stored in `qudt:numericValue`.
#        - The unit of measurement is stored in `qudt:unit`.
#        - Observations result time it associated with property 'sosa:resultTime'

#     3. **Query Formatting Rules**
#        - make sure brackets are balanced. double check whether every open backet is closed and whether is there any additional closed backet before exicute query. 
#        - **For average flow rate values**, use:
#          ```sparql
#          PREFIX sosa: <http://www.w3.org/ns/sosa/>
#          PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/> 
#          PREFIX qudt: <https://qudt.org/schema/qudt/>

#          SELECT (AVG(?flowRate) AS ?averageFlowRate) ?unit 
#          WHERE {{
#            GRAPH <{named_graph}> {{
#              ?obs a sosa:Observation ;
#                   sosa:observedProperty envthes:21242 ;
#                   sosa:hasResult ?result .
#              ?result qudt:numericValue ?flowRate;
#                      qudt:unit ?unit .
#            }}
#          }}
#          ```
#        - Ensure **all opening brackets '{' have a corresponding closing '}' **.
#        - Do **not add extra closing brackets at the end**.
#        - If the question explicitly asks for **a limited number of results**, add a `LIMIT` clause.
#        - If the question requires **counting**, use `COUNT(*)`.
#        - **Ensure the correct namespace for `envthes` is used** (`http://vocabs.lter-europe.net/EnvThes/`).
#        - **Ensure the correct namespace for `qudt:` is used** (`https://qudt.org/schema/qudt/`).
#        - **Do not use unnecessary `FROM` statements**.
#        - Always ensure **proper indentation and readability**.
#        - When generating SPARQL queries, note that sosa:madeBySensor is the inverse of sosa:madeObservation. If the query uses sosa:madeObservation, replace it with ^sosa:madeBySensor.

#     4. Convert the following natural language question into a well-structured SPARQL query.

#         - Use correct ontology classes and properties.
#         - Ensure proper formatting for Virtuoso triple store.
#         - make sure brackets are balanced. double check whether every open backet is closed and whether is there any additional closed backet before exicute query. 

        
#         ### **Input Question**
#         {question}

#         ### **Output:**
#         Generate only the SPARQL query without any additional text. **Ensure correct bracket placement to avoid syntax errors.**
#         """

#     # Generate a SPARQL query using OpenAI
#     response = llm.invoke(prompt)

#     # Extract the generated SPARQL query
#     sparql_query = response.content.strip()

#     # Clean the SPARQL query to remove code block markers
#     if sparql_query.startswith("```"):
#         sparql_query = sparql_query.replace("```sparql", "").replace("```", "").strip()

#     # Apply corrections if the query structure is incorrect
#     sparql_query = clean_sparql_query(sparql_query, named_graph)

#     return sparql_query

def generate_sparql(question, named_graph):
    """Uses OpenAI to generate a structured SPARQL query, ensuring correctness for Virtuoso."""

    prompt = f"""
    You are an expert in querying RDF datasets using SPARQL **for the Virtuoso triple store**.  
    Your task is to convert the following natural language question into a **correct**, **well-structured**, and **Virtuoso-compatible** SPARQL query.

    ### **Guidelines**
    1. **Use Correct Prefixes**  
       ```
       PREFIX sosa: <http://www.w3.org/ns/sosa/>
       PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/>
       PREFIX qudt: <https://qudt.org/schema/qudt/>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       PREFIX unit: <https://qudt.org/vocab/unit/>
       PREFIX schema: <https://schema.org/>
       PREFIX locn: <http://www.w3.org/ns/locn#>
       PREFIX geo: <http://www.opengis.net/ont/geosparql#>
       PREFIX n4e_hyd: <https://nfdi4earth.pages.rwth-aachen.de/knowledgehub/nfdi4earth-ontology/test_hyd#>
       ```

    2. **Follow Correct Data Structure**  
       - Observations are modeled using `sosa:Observation`.  
       - The observed property is linked using `sosa:observedProperty`.  
       - The result is linked using `sosa:hasResult` (not `sosa:result`).  
       - The numeric value of the result is stored in `qudt:numericValue`.  
       - The unit of measurement is stored in `qudt:unit`.  
       - The observation result time is associated with `sosa:resultTime`.  
       - Spatial data is stored using `geo:asWKT`.  

    3. **Query Formatting Rules**  
       - Ensure **balanced brackets**: double-check that every `{" has a corresponding "}`.  
       - **Use LIMIT** when the question asks for a specific number of results.  
       - **Use COUNT(*)** when the question asks for a count.  
       - **Use proper namespaces** (`envthes:`, `qudt:`) without errors.  
       - **For spatial queries, use Virtuoso-specific functions**:
         - `bif:st_x()`, `bif:st_y()`, `bif:st_z()` for extracting coordinates.  
         - `bif:st_distance()` for geodesic distance.  
         - `bif:st_intersects()` for spatial relationships.  

    4. **Examples for Reference (Few-Shot Learning)**  

    **Example 1: Location of a gauging station**  
    **Question:** "Where is the 'Schlehdorf' gauging station located?"  
    **SPARQL Query:**
    ```sparql
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX schema: <https://schema.org/>

    SELECT ?geomObj ?easting ?northing ?elevation
    WHERE {{
      GRAPH <{named_graph}> {{
        ?sensor schema:name "Schlehdorf" ;
                geo:hasGeometry ?geom .
        ?geom geo:asWKT ?geomObj.
        BIND (bif:st_x(?geomObj) AS ?easting)
        BIND (bif:st_y(?geomObj) AS ?northing)
        BIND (bif:st_z(?geomObj) AS ?elevation)
      }}
    }}
    ```

    **Example 2: Highest annual precipitation catchment**  
    **Question:** "Which catchment area recorded the highest annual precipitation in 2015?"  
    **SPARQL Query:**
    ```sparql
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/>
    PREFIX qudt: <https://qudt.org/schema/qudt/>
    PREFIX schema: <https://schema.org/>

    SELECT ?catchment (SUM(?precipitation) AS ?totalAnnualPrecipitation) ?unit
    WHERE {{
      GRAPH <{named_graph}> {{
        ?observation a sosa:Observation ;
                     sosa:observedProperty envthes:30106 ;
                     sosa:madeBySensor ?sensor ;
                     sosa:resultTime ?resultTime ;
                     sosa:hasResult ?result.
        ?result qudt:numericValue ?precipitation;
                qudt:unit ?unit.
        ?sensor n4e_hyd:monitorsCatchment ?catchment.
        FILTER(YEAR(?resultTime) = 2015)
      }}
    }}
    GROUP BY ?catchment ?unit
    ORDER BY DESC(?totalAnnualPrecipitation)
    LIMIT 1
    ```

    **Example 3: Average flow rate calculation**  
    **Question:** "What is the average flow rate at a station?"  
    **SPARQL Query:**
    ```sparql
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX envthes: <http://vocabs.lter-europe.net/EnvThes/> 
    PREFIX qudt: <https://qudt.org/schema/qudt/>

    SELECT (AVG(?flowRate) AS ?averageFlowRate) ?unit 
    WHERE {{
      GRAPH <{named_graph}> {{
        ?obs a sosa:Observation ;
             sosa:observedProperty envthes:21242 ;
             sosa:hasResult ?result .
        ?result qudt:numericValue ?flowRate;
                qudt:unit ?unit .
      }}
    }}
    ```
    
    5. **Convert the following natural language question into a well-structured SPARQL query.**  
       - Use the correct ontology classes and properties.  
       - Ensure proper formatting for Virtuoso.  
       - Check for **bracket balance** and **namespace correctness**.  
       
    ### **Input Question**  
    {question}

    ### **Output:**  
    Generate only the **SPARQL query** without any additional text.  
    **Ensure correct bracket placement to avoid syntax errors.**
    """

    # Generate a SPARQL query using OpenAI
    response = llm.invoke(prompt)

    # Extract the generated SPARQL query
    sparql_query = response.content.strip()

    # Clean the SPARQL query to remove code block markers
    if sparql_query.startswith("```"):
        sparql_query = sparql_query.replace("```sparql", "").replace("```", "").strip()

    # Apply corrections if the query structure is incorrect
    sparql_query = clean_sparql_query(sparql_query, named_graph)

    return sparql_query




def validate_sparql(sparql_query, named_graph):
    """Validates the SPARQL query before execution."""

    # 1️⃣ Check if the query is empty
    if not sparql_query.strip():
        return False, "Error: The generated SPARQL query is empty."

    # 2️⃣ Check for common syntax errors (e.g., missing brackets)
    if sparql_query.count('{') != sparql_query.count('}'):
        return False, "Error: Mismatched braces in the SPARQL query."

    # 3️⃣ Run a dry-run query to check for syntax errors
    try:
        test_results = query_sparql(sparql_query)
        if 'results' not in test_results:
            return False, "Error: Query execution failed. Check the syntax."
    except Exception as e:
        return False, f"Error: Query validation failed - {str(e)}"

    return True, "Valid Query"


def ask_natural_language_question(question, named_graph):
    """Converts NL question to SPARQL, validates, runs query on a specific named graph, and returns a response."""

    # Step 1: Generate SPARQL query for the named graph
    sparql_query = generate_sparql(question, named_graph)
    # print(f"Generated and cleaned SPARQL Query:\n{sparql_query}\n")  # Debugging output

    # Step 2: Validate the query
    is_valid, validation_message = validate_sparql(sparql_query, named_graph)
    if not is_valid:
        return sparql_query, "Error: Invalid SPARQL Query.", validation_message  # Return error if validation fails

    # Step 3: Run the validated query on Virtuoso
    results = query_sparql(sparql_query)

    # print("SPARQL Query Execution Results:", results) # Debugging output

    # Step 4: Format the result for readability
    # return format_results(results)
    formatted_answer = format_results(results)

    # **Handle empty results**:
    if not formatted_answer.strip():
        return sparql_query, "No results found for the query.", "No explanation available because no results were retrieved."

    # Step 5: Generate a natural language explanation of the answer
    verbalized_ans = generate_explanation (question, answer=formatted_answer)

    # step 6 : Retun both direct and NL explaination
    #return f"Answer: {formatted_answer}\n\nExplaination: {explanation}"
    return sparql_query, formatted_answer, verbalized_ans

def format_results(results):
    """Formats SPARQL results into a readable response."""
    if 'boolean' in results:
        return "Yes" if results['boolean'] else "No"

    answer_list = []
    for item in results['results']['bindings']:
        values = [v['value'] for v in item.values()]
        answer_list.append(" - ".join(values))

    return "\n".join(answer_list)

def generate_explanation(question, answer):
    """Uses OpenAI to generate a natural language explanation of the answer."""
    
    prompt = f"""
    You are an expert in SPARQL and semantic web queries.
    Given the following question and its SPARQL-derived answer, explain the answer in simple, natural language.

    Question: {question}
    Answer: {answer}

    Explanation:
    """

    # Use OpenAI to generate an explanation
    response = llm.invoke(prompt)
    
    return response.content.strip()

if __name__ == "__main__":

    # Example Question
    # question = "How many triples in this dataset?"
    # question = "How many sensors in this dataset?"
    #question = "how many observations in this dataset?" 
    question = "What are the coordinates of sensor called 'Bangs'?"

    # question = "What is the average flow rate observation of this dataset? flow rate is measured by envthes:21242"
    #question = "What it the elevation of the gauging station with the lowest observed average river flow?, flow rate is measured by envthes:21242"

    # question  = "Which year has highest total flow rate in the sensor called 'Bangs'? "

    # question  = "Which year has the highest total precipitation in the catchment where the sensor called 'Bangs' is situated? "

    # question = "What is the surface area of the largest catchment in the dataset?"

    # question = "Where is the 'Gattendorf (Schleuse)' gauging station located? [What are the coordinates]"

    # question = "What is the distance (length) between the highest and lowest elevation gauging stations (gauging stations is a sensor) in this dataset?"

    named_graph = "http://hydroturtle/LamahCE"
    print("Question:", question)
    print("Answer:", ask_natural_language_question(question, named_graph))
