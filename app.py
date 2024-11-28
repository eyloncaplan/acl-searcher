from flask import Flask, request, render_template
import argparse
import logging
import sys
import os
from ragatouille import RAGPretrainedModel

# Initialize Flask app
app = Flask(__name__)

# Initialize the engine
def init_engine():
    index_name = "paper_abstracts"
    index_path = f"/homes/ecaplan/acl_searcher/.ragatouille/colbert/indexes/{index_name}"

    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')  # Redirect stdout to suppress library output

    engine = RAGPretrainedModel.from_index(index_path)
    for i in range(5):
        try:
            engine.search("dummy", k=10)  # Test the index
            break
        except Exception as e:
            sys.stdout = original_stdout
            logging.error(f"Failed to make index on attempt {i}: {e}")
    sys.stdout = original_stdout  # Restore stdout
    return engine

engine = init_engine()  # Initialize the engine once and reuse it

# Query the engine
def query_engine(engine, query, k=5):
    results = engine.search(query, k=k)
    results = [result['content'] for result in results]
    return results

# Web interface
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    query = None
    if request.method == "POST":
        query = request.form.get("query")  # Get query from form input
        result = query_engine(engine, query, k=5)  # Process query
    return render_template("index.html", query=query, result=result)

# CLI Mode
def cli_mode():
    parser = argparse.ArgumentParser(description="Run the search engine in CLI or web mode.")
    parser.add_argument("--query", type=str, help="Query to search for")
    parser.add_argument("--web", action="store_true", help="Run the web interface")
    args = parser.parse_args()

    if args.web:
        app.run(debug=True)  # Start the Flask app
    elif args.query:
        results = query_engine(engine, args.query, k=5)  # Query the engine
        print("Results:")
        for i, result in enumerate(results, start=1):
            print(f"{i}. {result}")
    else:
        print("Please specify a query with --query or run the web interface with --web.")

if __name__ == "__main__":
    cli_mode()
