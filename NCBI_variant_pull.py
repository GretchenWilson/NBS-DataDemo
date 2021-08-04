from API_NCBI import EntrezSearch
import time

"""
This script searches clinvar for the variants listed with the variable variant_list_accession.
Uses the Entrez search class in the API_NCBI.py file.

Coming Soon: Command Line execution
"""

variant_list_accession = ["NM_000492.3:c.79G>T", "NM_000492.3:c.125C>T", "NM_000492.3:c.1573del",
                          "NM_000492.3:c.1505T>A", "NM_000492.3:c.1408G>A"]

# Specify variant for Clinvar search
gene = "CFTR"

def cv_format(variant):
    """
    Formats results for printing
    :param variant:
    :return: str
    """
    string = 'VariationID: {}\nName: {}'.format(variant[0], variant[1])

    # iterate through RCV results and format
    for e in variant[2]:
        string += '\n\tCondition: {}' \
                  '\n\tInterpretaion: {}' \
                  '\n\tReviewStatus: {}' \
                  '\n\tDateLastEvaluated: {}' \
                  '\n\tRCVAccession: {},' \
                  '\n\tSubmissionCount: {}\n'.format(*e)
    return string



# list of variants pulled directly from ClinVar
# I noticed that the Accession version varies from entry to entry. Verified that the 3rd version is present for
# majority of variants

# declare EntrezSearch object to facilitate Entrez ClinVar searches
esearch = EntrezSearch(gene=gene)

# use Esearch  functions to pull information on each variant in a list from clinvar
# returns for each: [VariantionID, VariationName, [[InterpretedCondition, Interpretation, ReviewStatus,
#                     DateLastEvaluated, RCVAccession, SubmissionCount]]]
summary = esearch.get_significance_summary_by_variant(variant_list_accession)

# format results for printing
for entry in summary:

    print(cv_format(entry))
