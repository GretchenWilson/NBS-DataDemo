try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
    print("Choosing ElementTree instead of cElementTree")


import requests
import logging
from socket import gaierror
import time

logger = logging.getLogger(__name__)


class EntrezSearch(object):
    """
    Entrez Search Class using Eutils url building rules
    search = clinvar_base + esearch.fcgi?db=<database>$term=<query>
    """
    def __init__(self, gene, start=None, stop=None, chr=None):
        """

        :param gene:
        """
        self.gene = gene
        self.start = start
        self.stop = stop
        self.chr = chr
        self.xml = None
        self.entries = None

        self.base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.info_url = self.base + "/einfo.fcgi"
        self.search_url = self.base + "/esearch.fcgi?db=<database>&term=<query>&usehistory=y"
        self.fetch_url = self.base + "/efetch.fcgi?db=<database>&retmode=<retmode>&rettype=<rettype>&<additional>&WebEnv=<webenv>&query_" \
                                     "key=<querykey>&usehistory=y"
    # ---------Collect ClinVar Gene Variant Results--------------

    def get_snp_from_entrez(self):
        term = '{}:{}[Base Position] AND "{}" [CHR] AND txid9606'.format(self.start, self.stop, self.chr)
        a_webenv, a_querykey = self.search(term, "snp")
        self.fetch(a_webenv, a_querykey, db="snp", return_type="variation", return_mode="xml")

        return

    def get_cv_from_entrez(self):
        """
        First point of entry for accessing specific set of Entrez functions for NBSVI
        :return:
        """
        a_webenv, a_querykey = self.search(self.gene,"clinvar")  # search and post return UIDS to history accessible through webenv and querykey
        self.fetch(a_webenv, a_querykey, db="clinvar", return_type='vcv', return_mode="xml", additional='is_variationid')
        return self.xml

    def get_significance_summary_by_variant(self, variants):
        """Iterate through variant list and create Entrez search terms
               -term format is <gene>[gene]AND<variant>[varname]
           :param variant_list:
           :return: [VariantionID, VariationName, [[InterpretationCondition, Interpretation, ReviewStatus,
                    DateLastEvaluated, RCVAccession, Submissions]]]
           """
        # format each variant
        variants = ['"{}"[varname]'.format(variant) for variant in variants]
        # join variants by OR
        variant_term= 'OR'.join(variants)
        term = '"{}"[gene]AND{}'.format(self.gene, variant_term)

        # search for clinvar ID
        webenv, querykey, ids = self.search_for_ids(term)

        # fetch information from clinvar and read string into Etree object for parsing
        info = self.fetch(webenv, querykey, db='clinvar', return_type='vcv', return_mode='json', additional='is_variationid')
        tree_of_records = etree.fromstring(self.xml)

        # build list of clinvar information for each variant
        records = []
        for record in tree_of_records.iter(tag='VariationArchive'):
            # print(records)
            variant_id = record.get('VariationID')
            variant_name = record.get('VariationName')
            variant_classification_record = record.findall('.//RCVList/RCVAccession')

            # RCV records are interpretation to disorder records and a variant can have multiple
            rcv_records = []
            for rcv in variant_classification_record:
                rcv_record = [rcv.find('.//InterpretedCondition').text, rcv.get('Interpretation'),
                              rcv.get('ReviewStatus'), rcv.get('DateLastEvaluated'),
                              rcv.get('Accession'), rcv.get('SubmissionCount')]


                rcv_records.append(rcv_record)

            variant_record = [variant_id, variant_name, rcv_records]
            records.append(variant_record)

        return records


    def info(self):
        """
        get info on the etuils features
        :return:
        """

        print(self.info_url)
        get_info = requests.get(self.info_url).content.decode('utf-8')
        return get_info


    def search_for_ids(self, term, db="clinvar"):
        """
                :param term: search term format: <gene>[gene]AND<variant>[varname]
                :param db:
                :return: ClinVar Variant ID for search as well as web_env and query_key to access history
                """
        current_search = self.search_url.replace("<database>", "clinvar").replace("<query>", term)
        print('Searching Entrez with url: {}'.format(current_search))
        try:
            request = requests.get(current_search, timeout=5)
        except [requests.ConnectionError, requests.ReadTimeout, requests.Timeout] as e:
            logger.error(e)
            logger.warning('Request received with code: %s', request.status_code)
            raise IOError from e
        if not request.status_code == 200:
            raise IOError('Request Status code was'.format(request.status_code))

        get_search = request.content.decode('utf-8')
        tree = etree.fromstring(get_search)
        webenv = tree.find('WebEnv').text
        query_key = tree.find('QueryKey').text
        id_tree = tree.findall('IdList/Id')
        ids = [id.text for id in id_tree]

        return webenv, query_key, ids


    def search(self, term, db="clinvar"):
        """

        :param term:
        :param db:
        :return:
        """
        current_search = self.search_url.replace("<database>", db).replace("<query>", term)
        print('Searching Entrez with url: {}'.format(current_search))
        try:
            request = requests.get(current_search, timeout=5)
        except [requests.ConnectionError, requests.ReadTimeout, requests.Timeout] as e:
            logger.error(e)
            logger.warning('Request received with code: %s', request.status_code)
            raise IOError from e
        if not request.status_code == 200:
            raise IOError('Request Status code was'.format(request.status_code))
        logger.debug('Request received with code: %s', request.status_code)
        get_search = request.content.decode('utf-8')
        tree = etree.fromstring(get_search)
        webenv = tree.find('WebEnv').text
        query_key = tree.find('QueryKey').text

        return webenv, query_key


    def fetch(self, web_env, query_key, db, return_type, return_mode, additional):
        """
        :param web_env:
        :param query_key:
        :param db:
        :param return_type:
        :param return_mode:
        :return:
        """
        # self.fetch_url = self.base + "/efetch.fcgi?db=<database>&retmode=<retmode>&rettype=<rettype>&<additional>&WebEnv=<webenv>&query_key=<querykey>&usehistory=y"
        current_fetch = self.fetch_url.replace("<webenv>", web_env)\
                                        .replace("<querykey>", query_key)\
                                        .replace("<database>", db)\
                                        .replace("<rettype>", return_type)\
                                        .replace("<retmode>", return_mode)\
                                        .replace("<additional>", additional)
        print('Fetching Entrez with url: {}'.format(current_fetch))
        try:
            request = requests.get(current_fetch)
        except requests.ConnectionError as e:
            raise IOError from e

        if not request.status_code == 200:
            raise IOError('Request Status code was'.format(request.status_code))
        logger.debug('Request received with code: %s', request.status_code)
        self.xml = request.content.decode('utf-8')
        return request.status_code



if __name__ == '__main__':
    import requests

    request_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=GAA[gene]&retmode=json&usehistory=y'
    r = requests.get(request_url)
    j = r.json()

    webenv = j['esearchresult']['webenv']
    querykey = j['esearchresult']['querykey']

    fetch_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=clinvar&retmax=20&retmode=xml&rettype=vcv&is_variationid&WebEnv=<webenv>&query_key=<querykey>&usehistory=y'
    fetch_url = fetch_url.replace('<webenv>', webenv).replace('<querykey>', querykey)
    r = requests.get(fetch_url)

    x = r.content.decode('utf-8')

    import xml.etree.cElementTree as etree

    tree = etree.fromstring(x)
    short_tree = tree[:20]

    for entry in short_tree:
        assertions = entry.findall('.//ClinicalAssertionList/ClinicalAssertion')

        assertion_string = ''
        for a in assertions:
            assertion_string += '\tSubmitter: {}\n\tClassification: {}\n'.format(
                a.find('ClinVarAccession').get('SubmitterName'), a.find('Interpretation/Description').text)
        print('VariationID:{}\nName:{}\nAssertions:\n{}'.format(entry.get('VariationID', entry), entry.get('VariationName'),
                                                                assertion_string))

    fetch_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=11738358&retmode=text&rettype=abstract'
    r = requests.get(fetch_url)
    x = r.content.decode('utf-8')