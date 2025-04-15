print("Importing Flask...")
from flask import Flask, request, render_template
print("Flask imported successfully.")

print("Importing RAGPretrainedModel from ragatouille (this might take a while)...")
from ragatouille import RAGPretrainedModel
print("RAGPretrainedModel imported successfully.")

# Other imports
import argparse
import logging
import sys
import os
import pandas as pd

print("All necessary imports completed.")

app = Flask(__name__)

# Global variable
K = None
base_dir = os.path.dirname(os.path.abspath(__file__))

def init_engine():
    print("Initializing the engine...")
    # index_name = "paper_abstracts"
    index_name = "paper_abstracts_old"
    index_path = os.path.join(base_dir, "data", ".ragatouille", "colbert", "indexes", index_name)


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
            logging.error(f"Failed to make index on attempt {i + 1}: {e}")
            if i == 4:
                print("Failed to initialize the engine after 5 attempts.")
            else:
                print(f"Retrying initialization... ({5 - i - 1} attempts left)")
    sys.stdout = original_stdout  # Restore stdout
    return engine

engine = init_engine()

# Load data (ensure 'year' column is present in your CSV)
csv_path = os.path.join(base_dir, "data", "anthology+abstracts.csv")
data = pd.read_csv(csv_path)
data = data.dropna(subset=['abstract'])

def query_engine(engine, query, k=5):
    print(f"Processing query: {query}")
    results = engine.search(query, k=k)
    results = [result['content'] for result in results]  # Just the text
    print("Query processed successfully.")
    return results

def get_paper_details(results, min_year=0):
    """
    Return the paper info in the same order as 'results' from the search engine,
    but only for those papers with 'year' >= min_year.
    """
    papers = []
    for abstract in results:
        # Filter for matching abstracts AND year >= min_year
        matching_rows = data[(data['abstract'] == abstract) & (data['year'] >= min_year)]
        if not matching_rows.empty:
            row = matching_rows.iloc[0]  # Take the first match
            papers.append({
                'title': row['title'],
                'year': row['year'],
                'authors': row['author'],
                'venue': row['booktitle'],
                'abstract': row['abstract'],
                'url': row.get('url', '')  # Handle missing or empty URLs
            })
    return papers

@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    k_val = 5          # Default number of results
    min_year_val = 0   # Default min year (filter out papers older than this)
    papers = []

    if request.method == "POST":
        query = request.form.get("query", "")
        k_val = request.form.get("k", type=int, default=5)
        min_year_val = request.form.get("min_year", type=int, default=0)

        print(f"Received query: {query} | k={k_val} | min_year={min_year_val}")

        if query.strip():
            # Query the engine
            results = query_engine(engine, query, k=k_val)
            # Convert results to structured data, filtering out older papers
            papers = get_paper_details(results, min_year=min_year_val)

    return render_template(
        "index.html",
        query=query,
        k_val=k_val,
        min_year_val=min_year_val,
        papers=papers
    )

def console_mode():
    print("\n" * 100)
    print("============================================")
    print(" Welcome to the Interactive Console Mode ")
    print(" Type 'exit' to quit at any time ")
    print("============================================\n")

    while True:
        query = input("Enter your query: ").strip()
        if query.lower() == "exit":
            print("\nExiting console mode. Goodbye!")
            break
        if not query:
            print("Empty query. Please enter a valid query or type 'exit' to quit.\n")
            continue

        print("\nSearching...")
        results = query_engine(engine, query, k=K)
        # Just print results or do something else
        print(results)

def cli_mode():
    parser = argparse.ArgumentParser(description="Run the search engine in console or web mode.")
    parser.add_argument("--console", action="store_true", help="Run the search engine in interactive console mode")
    parser.add_argument("--web", action="store_true", help="Run the web interface")
    parser.add_argument("-k", type=int, default=5, help="Number of results to retrieve (default: 5)")
    args = parser.parse_args()

    global K
    K = args.k

    if args.web:
        print("Starting the web interface...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    elif args.console:
        console_mode()
    else:
        print("Please specify either --console to run in interactive console mode or --web to run the web interface.")

if __name__ == "__main__":
    print("Script starting...")
    cli_mode()