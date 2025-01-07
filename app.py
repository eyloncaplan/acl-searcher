print("Importing Flask...")
from flask import Flask, request, render_template
print("Flask imported successfully.")

print("Importing RAGPretrainedModel from ragatouille (this might take a while)...")
from ragatouille import RAGPretrainedModel
print("RAGPretrainedModel imported successfully.")

# Other imports (not expected to take long)
import argparse
import logging
import sys
import os
import pandas as pd  # Import pandas for data handling

print("All necessary imports completed.")

# Initialize Flask app
app = Flask(__name__)

# Global variables
K = None

# Initialize the engine
def init_engine():
    print("Initializing the engine...")
    index_name = "paper_abstracts"
    index_path = f"/homes/ecaplan/acl-searcher/data/.ragatouille/colbert/indexes/{index_name}"

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

engine = init_engine()  # Initialize the engine once and reuse it

data = pd.read_csv('/homes/ecaplan/acl-searcher/data/anthology+abstracts.csv')  # Load data for detailed retrieval
data = data.dropna(subset=['abstract'])

# Query the engine
def query_engine(engine, query, k=5):
    print(f"Processing query: {query}")
    results = engine.search(query, k=k)
    results = [result['content'] for result in results]
    print("Query processed successfully.")
    return results

def display_results(results):
    print("Retrieving paper details...")
    retrieved_df = data[data['abstract'].apply(lambda x: any(result in x for result in results))]
    for i, row in retrieved_df.iterrows():
        print(f"Title: {row['title']}")
        print(f"Year: {row['year']}")
        print(f"Authors: {row['author']}")
        print(f"Abstract: {row['abstract']}")
        print(f"Venue: {row['booktitle']}")
        print()

# Web interface
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    query = None
    if request.method == "POST":
        query = request.form.get("query")  # Get query from form input
        print(f"Received query via web interface: {query}")
        result = query_engine(engine, query, k=K)  # Process query
    return render_template("index.html", query=query, result=result)

# Console Mode (Interactive)
def console_mode():
    print("Starting interactive console mode. Type 'exit' to quit.")
    while True:
        query = input("Enter your query: ").strip()
        if query.lower() == "exit":
            print("Exiting console mode. Goodbye!")
            break
        if not query:
            print("Empty query. Please enter a valid query or type 'exit' to quit.")
            continue
        print("Searching...")
        results = query_engine(engine, query, k=K)
        display_results(results)
        print("---")

# CLI Mode
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
        app.run(debug=True)  # Start the Flask app
    elif args.console:
        console_mode()  # Run console mode
    else:
        print("Please specify either --console to run in interactive console mode or --web to run the web interface.")

if __name__ == "__main__":
    print("Script starting...")
    cli_mode()
