import pandas as pd
import sys
from ragatouille import RAGPretrainedModel

sys.setrecursionlimit(100000)

# read the data from csv
data = pd.read_csv('/homes/ecaplan/acl-searcher/data/anthology+abstracts.csv')

# drop all rows with NaN values in the abstract column
data = data.dropna(subset=['abstract'])
# only include rows past the year 2010
data = data[data['year'] > 2010]

conferences = ['Association for Computational Linguistics', 'The Association for Computational Linguistics', 'ACL', 'Association of Computational Linguistics']

# only include rows with the publisher in the list 'conferences'
acl_data = data[data['publisher'].isin(conferences)]

RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
paper_metadatas = acl_data.to_dict(orient='records')
paper_abstracts = acl_data['abstract'].tolist()

index_path = RAG.index(
    index_name="paper_abstracts",
    collection=paper_abstracts,
    # document_metadatas=paper_metadatas,
)