import polars as pl
from typing import NewType

# Define semantic types for clarity
VariantId = NewType('VariantId', str)
Genotype = NewType('Genotype', str)

class Genotypes:
    """
    A class to handle genotype data loaded from a TSV file using Polars LazyFrames.
    """
    lazyframe: pl.LazyFrame # Define class variable with type hint

    def __init__(self, filepath: str):
        """
        Initializes the Genotypes object by creating a LazyFrame from a TSV file.

        Args:
            filepath: The path to the TSV file.
        """
        # Use scan_csv for lazy loading
        self.lazyframe = pl.scan_csv(filepath, separator='\t')

    def get_snp_ids(self) -> list[VariantId]:
        """
        Returns a list of SNP IDs, excluding '.' entries, using lazy evaluation.

        Returns:
            A list of SNP IDs.
        """
        # Filter out rows where the 'ID' column is '.' and collect the 'ID' column as a list
        snp_ids = self.lazyframe.filter(pl.col('ID') != '.').select('ID').collect()['ID'].to_list()
        return snp_ids

    def get_individual_genotypes(self, individual_id: str) -> dict[VariantId, Genotype]:
        """
        Returns a DataFrame of SNP IDs and genotypes for a single individual using lazy evaluation.

        Args:
            individual_id: The column name for the individual's genotype.

        Returns:
            A Polars DataFrame with 'ID' and the specified individual's genotype column.
            excluding rows where 'ID' is '.'.

        Raises:
            ValueError: If the individual_id is not found in the LazyFrame columns.
        """
        colnames: list[str] = self.lazyframe.collect_schema().names()
        # Check if the column exists in the schema before collecting
        if individual_id not in colnames:
            raise ValueError(f"Individual ID '{individual_id}' not found in the file.")


        # Select 'ID' and the specified individual's genotype column, filter, and collect
        individual_df = self.lazyframe.select(['ID', individual_id]).filter(pl.col('ID') != '.').collect()

        mapping_id_to_gt = dict(zip(individual_df["ID"], individual_df[individual_id]))

        return mapping_id_to_gt