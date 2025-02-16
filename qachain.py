from execute_sparql import query_sparql

def format_answer(results):
    """Formats SPARQL query results into readable text."""
    if 'boolean' in results:
        return "Yes" if results['boolean'] else "No"

    answer_list = []
    for item in results['results']['bindings']:
        values = [v['value'] for v in item.values()]
        answer_list.append(" - ".join(values))

    return "\n".join(answer_list)

def get_natural_language_response(query):
    """Executes SPARQL query and returns a formatted natural language response."""
    results = query_sparql(query)
    return format_answer(results)
