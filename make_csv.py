import bibtexparser
import pandas as pd

# Specify the file path
bib_file_path = 'anthology+abstracts.bib'

# Read the .bib file
with open(bib_file_path) as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

print(f"Done reading {bib_file_path}")

# Convert the parsed entries into a pandas DataFrame
df = pd.DataFrame(bib_database.entries)

# Display the DataFrame
print(df)

# Optionally save the DataFrame to a CSV file for further analysis
output_csv_path = 'anthology+abstracts.csv'
df.to_csv(output_csv_path, index=False)
print(f"DataFrame saved to {output_csv_path}")

