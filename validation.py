import yaml, os
import pandas as pd
from difflib import SequenceMatcher
from datetime import datetime
from tutorial_without_promt import ask_natural_language_question

# Load the YAML file
yaml_file_path = "questions.yaml"
with open(yaml_file_path, "r", encoding="utf-8") as file:
    yaml_data = yaml.safe_load(file)

# Function to compute Jaccard Similarity
def jaccard_similarity(query1, query2):
    # Tokenize by splitting on whitespace while preserving case
    set1 = set(query1.split())  
    set2 = set(query2.split())

    # Avoid division by zero if both sets are empty
    if not set1 or not set2:
        return 0.0

    # Compute Jaccard similarity
    return len(set1 & set2) / len(set1 | set2)

# Function to compute Levenshtein Similarity (using SequenceMatcher)
def levenshtein_similarity(query1, query2):
    return SequenceMatcher(None, query1, query2).ratio()

# Function to recursively extract NL questions and SPARQL queries from a nested YAML structure
def extract_questions_sparql_recursive(data, results=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):  # If value is a dictionary, recurse
                extract_questions_sparql_recursive(value, results)
            elif isinstance(value, str):  # If value is a string, treat it as SPARQL query
                results.append((key, value.strip()))
    return results

# Extract NL questions and corresponding SPARQL queries
questions_sparql_pairs = extract_questions_sparql_recursive(yaml_data, [])

# Display the first 5 extracted pairs for verification
#print(questions_sparql_pairs[:5])

# Create a DataFrame to store results
results_df = pd.DataFrame(columns=["Question", "Generated SPARQL", "Sample SPARQL", "Jaccard Similarity", "Levenshtein Similarity"])

# Simulate the `ask_natural_language_question` function (replace this with the actual function call)
# def ask_natural_language_question(question, named_graph="http://hydroturtle/LamahCE"):
#     """Mock function: Replace with actual function to get LLM-generated SPARQL query."""
#     # In actual usage, replace this line with: generated_sparql, formatted_answer, verbalized_ans = ask_natural_language_question(question, named_graph)
#     return "MOCKED GENERATED QUERY"

named_graph = "http://hydroturtle/LamahCE"

# Process each question
# Process each question
for question, sample_sparql in questions_sparql_pairs:
    generated_sparql, _, _ = ask_natural_language_question(question, named_graph)  # Extract only SPARQL query, this function has 3 return varibales as tuples, I only need sparql query for the verificaiton 
    jaccard_score = jaccard_similarity(generated_sparql, sample_sparql)
    levenshtein_score = levenshtein_similarity(generated_sparql, sample_sparql)
    
    # Append results correctly using pd.concat()
    results_df = pd.concat([results_df, pd.DataFrame([{
        "Question": question,
        "Generated SPARQL": generated_sparql,
        "Sample SPARQL": sample_sparql,
        "Jaccard Similarity": jaccard_score,
        "Levenshtein Similarity": levenshtein_score
    }])], ignore_index=True)


# Display results
import ace_tools_open as tools
tools.display_dataframe_to_user(name="SPARQL Query Similarity Evaluation", dataframe=results_df)


# export the results to csv

## generate result created time 
time_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file_name = f"validation_{time_stamp}.csv"

output_dir = "C:/Users/sHaMiLa/Nextcloud/Geoinformatics WHK/SPARQL Queries/Validation/SPARQL_Validation_Results"
os.makedirs(output_dir, exist_ok=True) # make the directory if not available 

output_file_path = os.path.join(output_dir, output_file_name)

## save the file to csv 
results_df.to_csv(output_file_path, sep=',', encoding='utf-8', index=False, header=True)

print(f"Finally Validation results saved to: {output_file_path}")