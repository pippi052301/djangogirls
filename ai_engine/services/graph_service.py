import json
from .ai_config import get_client, types

def generate_knowledge_graph(text_content):
    """Extract knowledge into Nodes and Edges for Obsidian."""
    prompt = f"""
    You are an expert in data analysis and knowledge extraction (Knowledge Graph).
    Read the following text and extract key terms/concepts as "nodes", 
    while identifying the relationships between them as "edges".
    
    MANDATORY REQUIREMENTS:
    1. Nodes: Must be important nouns, terms, events, or proper names.
       - 'id': Unique identifier (no spaces, no accents).
       - 'label': Brief display name.
    2. Edges: Represent one-way relationships.
       - 'from': ID of the source Node.
       - 'to': ID of the target Node.
       - 'label': A short verb phrase describing the relationship.
    
    RETURN 100% JSON FORMAT WITH THE FOLLOWING STRUCTURE:
    {{
        "nodes": [
            {{"id": "node_1", "label": "Concept A"}},
            {{"id": "node_2", "label": "Concept B"}}
        ],
        "edges": [
            {{"from": "node_1", "to": "node_2", "label": "includes"}}
        ]
    }}

    Source text:
    \"\"\"{text_content}\"\"\"
    """
    
    try:
        response = get_client().models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error when calling API draw Graph: {e}")
        return None