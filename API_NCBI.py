try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
    print("Choosing ElementTree instead of cElementTree")


import requests
import logging
from socket import gaierror

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
        self.search_url = self.base + "/esearch.fcgi?db=<database>&term=<query>[gene]&usehistory=y"
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


    def info(self):
        """
        get info on the etuils features
        :return:
        """

        print(self.info_url)
        get_info = requests.get(self.info_url).content.decode('utf-8')
        return get_info

    def search(self, term, db="clinvar"):
        """

        :param term:
        :param db:
        :return:
        """
        current_search = self.search_url.replace("<database>", db).replace("<query>", term)
        logger.debug('Searching Entrez with url: %s', current_search)
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
        logger.debug('Fetching Entrez with url: %s', current_fetch)
        try:
            request = requests.get(current_fetch)
        except requests.ConnectionError as e:
            raise IOError from e

        if not request.status_code == 200:
            raise IOError('Request Status code was'.format(request.status_code))
        logger.debug('Request received with code: %s', request.status_code)
        self.xml = request.content.decode('utf-8')
        return request.status_code


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
fetch
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