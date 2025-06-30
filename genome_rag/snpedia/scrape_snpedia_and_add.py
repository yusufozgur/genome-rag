import mwclient
from mwclient import Site
from tqdm import tqdm # Import tqdm
import os # Import the os module
from genome_rag.snpedia.VectorDB import VectorDB # Import VectorDB

def main():

    agent = 'MySNPBot. Run by User:Xyz. xyz@foo.com Using mwclient/'
    # tokens and secrets are only necessary if your bot will write into SNPedia.
    # get your own tokens at http://bots.snpedia.com/index.php/Special:OAuthConsumerRegistration
    site = mwclient.Site('bots.snpedia.com', path='/', clients_useragent=agent, scheme='https')

    file_path = 'tmp.txt'

    # Check if tmp.txt already exists
    if os.path.exists(file_path):
        print(f"File '{file_path}' already exists. Skipping scraping. Starting adding.")
        # Load SNP IDs from the file
        with open(file_path, 'r') as f:
            snp_ids = [line.strip() for line in f if line.strip()] # Read lines, strip whitespace, ignore empty lines

        # Initialize VectorDB and add the loaded SNP IDs
        db = VectorDB()
        db.add_snps_to_db_if_not_added(snp_ids)

    else:
        # Open the file to save the SNP names
        with open(file_path, 'w') as f:
            # Iterate through the pages with a progress bar
            # The total number of SNPs is approximately 111,728
            for page in tqdm(site.Categories['Is_a_snp'], total=111728, desc="Scraping SNPedia"):
                f.write(page.name + '\n') # Write the page name to the file
        print(f"Scraping complete. SNP names saved to '{file_path}'.")


if __name__ == "__main__":
    main()
