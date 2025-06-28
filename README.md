# Genome-RAG

Genome-RAG is an experimental LLM based chat assistant that accepts user's genotype, and answers the users questions. By leveraging SNPedia using Retrieval Augmented Generation, it aims to give accurate and personalized responses.

# Getting started

Convert your vcf.gz formatted genotypes to tsv format with [VariantsToTable](https://gatk.broadinstitute.org/hc/en-us/articles/360036483472-VariantsToTable).
```
docker pull broadinstitute/gatk
docker run --rm -ti -v ./data:/data broadinstitute/gatk gatk VariantsToTable -V /data/sample.vcf -O /data/sample.tsv -F CHROM -F POS -F ID -F REF -F ALT -GF GT
```