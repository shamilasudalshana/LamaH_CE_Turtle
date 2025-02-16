from transformers import pipeline

# Load a BERT-based Named Entity Recognition (NER) model
nlp = pipeline("ner", model="dslim/bert-base-NER")

def ask_question(text):
    """Extracts named entities from a given natural language query."""
    entities = nlp(text)
    
    # Format extracted entities
    formatted_entities = [ent['word'] for ent in entities]
    
    return {"entities": formatted_entities}
