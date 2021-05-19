from API_NCBI import EntrezSearch

gene = "CFTR"

# list of variants pulled directly from ClinVar
# I noticed that the Accession version varies
# Check to see if issue is caused by searches for same variant but different accession version

variant_list = ["NM_000492.3:c.79G>T", "NM_000492.3:c.125C>T",
                "NM_000492.4:c.1573del", "NM_000492.3:c.1505T>A",
                "M_000492.4:c.1408G>A"]

esearch = EntrezSearch(gene=gene)

# iterate through variant list and create Entrez search terms
# term format is <gene>[gene]AND<variant>[varname]
for variant in variant_list:
    term = "{}[gene]AND{}[varname]".format(gene, variant)

    webenv, query_key = esearch.search(term)