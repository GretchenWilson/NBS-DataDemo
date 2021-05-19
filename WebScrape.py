import requests

from bs4 import BeautifulSoup


r = requests.get('https://www.egl-eurofins.com/emvclass/emvclass.php?approved_symbol=GAA')
html = r.content.decode('utf-8')


soup = BeautifulSoup(html, 'html.parser') # different parsers have different speeds and levels of forgiveness
table = soup.find('table', id='results')
header = table.find('thead')
headers = [h.text.strip() for h in header.findAll('th')]
body = table.findAll('tr')[1:]

entries = [[cell.text for cell in row.findAll('td')] for row in body]
