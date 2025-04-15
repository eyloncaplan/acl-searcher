import pandas as pd
import sys
import argparse
import requests
import gzip
import csv
import shutil
import bibtexparser
from ragatouille import RAGPretrainedModel

# Define file paths
bib_path = '/homes/ecaplan/acl-searcher/data/anthology+abstracts.bib'
csv_path = '/homes/ecaplan/acl-searcher/data/anthology+abstracts.csv'

def load_data():
    data = pd.read_csv(csv_path)
    data = data.dropna(subset=['abstract'])
    data = data[data['year'] > 2010]
    conferences = [
        'Association for Computational Linguistics',
        'The Association for Computational Linguistics',
        'ACL',
        'Association of Computational Linguistics'
    ]
    acl_data = data[data['publisher'].isin(conferences)]
    return acl_data

def to_csv():
    try:
        with open(bib_path, 'r', encoding='utf-8') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)

        if not bib_database.entries:
            print("No entries found in the .bib file.")
            return

        fieldnames = sorted(set([
            'ENTRYTYPE', 'ID', 'abstract', 'address', 'author', 'booktitle', 'doi',
            'editor', 'isbn', 'journal', 'language', 'month', 'note', 'number', 'pages',
            'publisher', 'title', 'url', 'volume', 'year'
        ]))

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(bib_database.entries)

        print(f"CSV file saved to {csv_path}...")
    except Exception as e:
        print(f"Error processing .bib file: {e}")

def index(acl_data):
    sys.setrecursionlimit(100000)
    RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
    paper_abstracts = acl_data['abstract'].tolist()
    index_path = RAG.index(index_name="paper_abstracts", collection=paper_abstracts)

def download_data():
    url = "https://aclanthology.org/anthology+abstracts.bib.gz"
    output_path = f"{bib_path}.gz"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print("Downloaded zip file...")
    else:
        print(f"Failed to download. Status code: {response.status_code}")
        return

    extracted_path = output_path.replace(".gz", "")
    with gzip.open(output_path, 'rt', encoding='utf-8') as gz_file, open(extracted_path, 'w', encoding='utf-8') as out_file:
        shutil.copyfileobj(gz_file, out_file)
    print("Extracted bib file...")

    to_csv()

def main():
    parser = argparse.ArgumentParser(description="Process ACL anthology data.")
    parser.add_argument("--download", action="store_true", help="Download the latest dataset and convert to CSV")
    parser.add_argument("--index", action="store_true", help="Index the data")
    args = parser.parse_args()

    if args.download:
        download_data()
    
    acl_data = load_data()
    if args.index:
        index(acl_data)
    else:
        print("Skipping indexing step.")

if __name__ == '__main__':
    main()
