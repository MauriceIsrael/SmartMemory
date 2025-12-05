"""
Prompts for document processing and rule extraction.
"""

EXTRACT_RULES_PROMPT = """
Analyze this document excerpt and extract business rules in the form:
IF <condition> THEN <consequence>

For each rule identified:
1. Provide a clear description in French.
2. Convert to SPARQL CONSTRUCT query.
3. Assign confidence (0.0-1.0) based on clarity and formality.
4. Cite the source section/page.
5. Give it a unique snake_case ID.

Document: {document_title}
Section: Page {page_number} or Context

Content:
{document_content}

Return ONLY a JSON array of rules with this format (no other text):
[
  {{
    "rule_id": "unique_snake_case_id",
    "description": "Description claire en français",
    "sparql_pattern": "CONSTRUCT {{ ?s ?p ?o }} WHERE {{ ?s ?p2 ?o2 }}",
    "confidence": 0.85,
    "source_page": 42
  }}
]
"""
