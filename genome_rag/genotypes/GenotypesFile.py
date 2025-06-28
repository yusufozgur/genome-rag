import polars as pl
from Genotype import VariantId, Genotype

class GenotypesFile:
    """
    A class to handle genotype data loaded from a TSV file using Polars LazyFrames.
    """
    lazyframe: pl.LazyFrame

    def __init__(self, filepath: str):
        self.lazyframe = pl.scan_csv(filepath, separator='\t')

    def get_snp_ids(self) -> list[VariantId]:
        # Filter out rows where the 'ID' column is '.' and collect the 'ID' column as a list
        snp_ids = self.lazyframe.filter(pl.col('ID') != '.').select('ID').collect()['ID'].to_list()
        return snp_ids

    def get_individual_genotypes(self, individual_id: str) -> dict[VariantId, Genotype]:
        colnames: list[str] = self.lazyframe.collect_schema().names()
        # Check if the column exists in the schema before collecting
        if individual_id not in colnames:
            raise ValueError(f"Individual ID '{individual_id}' not found in the file.")

        individual_df = self.lazyframe.select(['ID', individual_id]).filter(pl.col('ID') != '.').collect()

        mapping_id_to_gt_str: dict[VariantId, str] = dict(zip(individual_df["ID"], individual_df[individual_id]))

        mapping_id_to_gt: dict[VariantId, Genotype] = {k:Genotype(v) for k,v in mapping_id_to_gt_str.items()}

        return mapping_id_to_gt