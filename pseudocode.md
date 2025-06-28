### Pseudocode
1. Accept a user genotype(s)
   - For now, we can accept [VariantsToTable](https://gatk.broadinstitute.org/hc/en-us/articles/360036483472-VariantsToTable) tsv outputs
   - This is important as parsing VCF files to genotypes is not recommended - dont reinvent the wheel.
2. SNPedia wiki articles/pages will be stored in a vector database, using snp ids as keys.
   - List the users rsids
   - Find rsids that were added to the vector db.
   - add those rsids to the vector db
3. Accept a query from user.
   - Use the vector db to perform the semantic search. I believe it will encode the query and find the closest embeddings in the database.
   - Return top N results
4. Get the text for those N results.
   - Use the genotype knowledge to extract the phenotype summary info-
5. Attach phenotype summaries and  N results to the context window of the LLM.
   - LLM will generate responses with the knowledge gained.
   - I am not sure what kind of template here would be more suitable. pheno_sum_1 + text_1 + ... OR text_1 + text_2 .. + pheno_sums.

### Tech used
- Chroma DB
- Streamlit
- Langchain

### Potential Considerations

- Text splitting