import streamlit as st
from query_handler import QueryHandler
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize Streamlit page configuration
st.set_page_config(
    page_title="Australian Legal Advisor AI",
    page_icon="⚖️",
    layout="wide"
)

# Define categories and states
CATEGORIES = [
    "Criminal Law",
    "Corporate Law",
    "Divorce Law",
    "Immigration Law",
    "Property Law",
    "Employment Law",
    "Consumer Law",
    "Environmental Law",
    "Tax Law",
    "Healthcare Law"
]

STATES = [
    "Federal",
    "New South Wales",
    "Victoria",
    "Queensland",
    "Western Australia",
    "South Australia",
    "Tasmania",
    "Australian Capital Territory",
    "Northern Territory"
]

def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state.history = []

def create_reference_chart(references):
    """Create a visual representation of references used."""
    categories = list(references.keys())
    counts = [len(refs) for refs in references.values()]
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=counts,
        text=counts,
        textposition='auto',
    )])
    
    fig.update_layout(
        title="References by Category",
        xaxis_title="Reference Type",
        yaxis_title="Count"
    )
    
    return fig

def format_response(response_dict):
    """Format the response for display."""
    st.write("### Analysis")
    st.write(response_dict['answer'])
    
    if response_dict['references']:
        st.write("### References")
        for ref in response_dict['references']:
            st.write(f"- {ref}")

def main():
    initialize_session_state()
    
    st.title("Manish Paneru's Australian Legal Advisor AI")
    st.write("Get expert AI's advice on Australian law with up-to-date information as of 2024.")
    
    # Create tabs for different features
    tab1, tab2, tab3 = st.tabs(["Legal Query", "History Analysis", "About"])
    
    with tab1:
        # Existing query interface with enhancements
        col1, col2 = st.columns([2, 1])
        
        with col1:
            query = st.text_area("Enter your legal question:", height=100)
            
        with col2:
            category = st.selectbox("Choose the area of law:", CATEGORIES)
            state = st.selectbox("Choose jurisdiction:", STATES)
            
        if st.button("Get Legal Advice", type="primary"):
            if not query.strip():
                st.warning("Please enter a question.")
                return
                
            try:
                with st.spinner("Analyzing your query..."):
                    query_handler = QueryHandler()
                    response = query_handler.process_query(query, category, state)
                    
                    # Format and display response
                    format_response(response)
                    
                    # Store in history with metadata - SIMPLIFIED STRUCTURE
                    history_entry = {
                        'query': query,
                        'answer': response['answer'],
                        'category': category,
                        'state': state,
                        'timestamp': datetime.now().isoformat(),
                        'references': response['references']
                    }
                    if 'history' not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append(history_entry)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    with tab2:
        if st.session_state.history:
            try:
                # Create a DataFrame from history
                df = pd.DataFrame(st.session_state.history)
                
                # Show statistics
                st.write("### Query Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Queries", len(df))
                
                with col2:
                    if not df['category'].empty:
                        top_category = df['category'].mode()[0]
                        st.metric("Most Common Category", top_category)
                
                with col3:
                    if not df['state'].empty:
                        top_state = df['state'].mode()[0]
                        st.metric("Most Common Jurisdiction", top_state)
                
                # Show history with filters
                st.write("### Query History")
                if not df['category'].empty:
                    category_filter = st.multiselect(
                        "Filter by Category",
                        options=df['category'].unique()
                    )
                    
                    filtered_df = df if not category_filter else df[df['category'].isin(category_filter)]
                    
                    for idx, row in filtered_df.iterrows():
                        with st.expander(f"Query {idx + 1}: {row['query'][:50]}..."):
                            st.write("**Question:**", row['query'])
                            st.write("**Category:**", row['category'])
                            st.write("**Jurisdiction:**", row['state'])
                            st.write("**Timestamp:**", row['timestamp'])
                            
                            # Create a response dict for format_response
                            response_dict = {
                                'answer': row['answer'],
                                'references': row['references']
                            }
                            format_response(response_dict)
            except Exception as e:
                st.error(f"Error displaying history: {str(e)}")
        else:
            st.info("No query history available yet.")
    
    with tab3:
        st.write("### About This Legal Advisor")
        st.write("""
        This AI-powered legal advisor uses advanced language models to provide 
        information about Australian law. It covers both federal and state jurisdictions 
        across various areas of law.
        
        **Features:**
        - Real-time legal information
        - Federal and state-specific advice
        - Structured responses with references
        - Historical query analysis
        
        **Note:** This tool provides information only and should not be considered 
        as legal advice. Always consult with a qualified legal professional for 
        specific legal matters.
        """)

if __name__ == "__main__":
    main() 