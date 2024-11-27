from typing import Dict, List
import groq
import os
from datetime import datetime
import re

class QueryHandler:
    def __init__(self):
        self.groq_client = groq.Client(api_key=os.getenv('GROQ_API_KEY'))
    
    def process_query(self, query: str, category: str, state: str = "Federal") -> Dict:
        """Process user query using enhanced prompt engineering."""
        
        # Build the context and prompt
        context = self.build_context(category, state)
        full_prompt = self.build_prompt(query, context)
        
        # Generate response
        response = self.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an Australian legal expert assistant. Provide detailed, well-structured legal analysis with proper citations."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3
        )
        
        return {
            'answer': response.choices[0].message.content,
            'references': self.extract_references(response.choices[0].message.content)
        }
    
    def build_context(self, category: str, state: str) -> str:
        """Build legal context based on category and jurisdiction."""
        return f"""You are an expert in {category} within Australian Law, particularly knowledgeable about relevant legislation and its recent amendments up to 2024.

        Jurisdiction: {state}

        When providing your analysis:
        1. Start with a clear summary of the legal position
        2. Cite specific sections of relevant Acts and regulations
        3. Reference recent case law (2020-2024) if applicable
        4. Explain any state-specific variations or requirements
        5. Highlight recent legal changes or upcoming reforms
        6. Provide practical next steps or implications
        
        Format your response with clear sections:
        - Summary
        - Legal Analysis
        - Practical Implications
        - References"""
    
    def build_prompt(self, query: str, context: str) -> str:
        """Build a structured prompt for the query."""
        return f"""
        {context}
        
        User Query: {query}
        
        Please provide a comprehensive legal analysis that:
        1. Directly addresses the specific query
        2. Includes relevant legislative provisions
        3. Cites applicable case law
        4. Explains practical implications
        5. Notes any recent changes or updates
        
        Ensure all citations are accurate and specific."""
    
    def extract_references(self, text: str) -> List[str]:
        """Extract legal references from the response."""
        references = []
        
        # Extract legislation references
        legislation_refs = re.findall(r'(?:Section|Sec\.|s\.) \d+[A-Za-z]* of the [\w\s]+Act \d{4}', text)
        references.extend(legislation_refs)
        
        # Extract case law references
        case_refs = re.findall(r'\[\d{4}\] [A-Z]+[A-Za-z\s]+\d+', text)
        references.extend(case_refs)
        
        return list(set(references))