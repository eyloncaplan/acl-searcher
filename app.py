print("Importing Streamlit...")
import streamlit as st
print("Streamlit imported successfully.")

print("Importing RAGPretrainedModel from ragatouille (this might take a while)...")
from ragatouille import RAGPretrainedModel
print("RAGPretrainedModel imported successfully.")

# Other imports (not expected to take long)
import sys
import os
import pandas as pd

print("All necessary imports completed.")

# Initialize the engine
def init_engine():
    print("Initializing the engine...")
    index_name = "paper_abstracts"
    index_path = f"data/.ragatouille/colbert/indexes/{index_name}"

    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')  # Redirect stdout to suppress library output

    engine = None
    for i in range(5):
        try:
            print(f"Attempting to load the index (attempt {i + 1})...")
            engine = RAGPretrainedModel.from_index(index_path)
            engine.search("dummy", k=10)  # Test the index
            print("Engine initialized successfully.")
            break
        except Exception as e:
            sys.stdout = original_stdout
            print(f"Failed to make index on attempt {i + 1}: {e}")
            if i == 4:
                print("Failed to initialize the engine after 5 attempts.")
            else:
                print(f"Retrying initialization... ({5 - i - 1} attempts left)")
    sys.stdout = original_stdout  # Restore stdout
    return engine

engine = init_engine()  # Initialize the engine once and reuse it

# Load data for detailed retrieval
data = pd.read_csv('data/anthology+abstracts.csv')
data = data.dropna(subset=['abstract'])

# Query the engine
def query_engine(engine, query, k=5):
    print(f"Processing query: {query}")
    results = engine.search(query, k=k)
    results = [result['content'] for result in results]
    print("Query processed successfully.")
    return results

def retrieve_paper_details(results):
    print("Retrieving paper details...")
    retrieved_df = data[data['abstract'].apply(lambda x: any(result in x for result in results))]
    return retrieved_df

# Streamlit UI
def streamlit_interface():
    st.title("Research Paper Search Engine")
    st.markdown("Enter your query below to search the database for relevant papers.")

    # Input widgets
    query = st.text_input("Enter your search query:")
    k = st.slider("Number of results to retrieve:", min_value=1, max_value=20, value=5)

    # Process query on button click
    if st.button("Search"):
        if not query:
            st.warning("Please enter a query to search.")
        else:
            with st.spinner("Searching..."):
                results = query_engine(engine, query, k=k)
                retrieved_df = retrieve_paper_details(results)

                if retrieved_df.empty:
                    st.error("No matching papers found.")
                else:
                    st.success(f"Found {len(retrieved_df)} papers.")
                    for i, row in retrieved_df.iterrows():
                        st.markdown(f"### {row['title']}")
                        st.markdown(f"**Year:** {row['year']}  \n**Authors:** {row['author']}  \n**Venue:** {row['booktitle']}  \n**Abstract:** {row['abstract']}  ")
                        st.markdown("---")

if __name__ == "__main__":
    streamlit_interface()

