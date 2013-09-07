from flask import Flask
import xmltodict
import urllib2, simplejson as json
import os

def xmlopen(url, nome):
	if not os.path.isfile('cache/'+nome+'.xml'):
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		try:
			raw = opener.open(url).read()
		except:
			raw = None
		if raw:
			cache = open('cache/'+nome+'.xml', 'w')
			cache.write(raw)
			cache.close()
			response = raw
		else:
			response = None
	else:
		response = open('cache/'+nome+'.xml').read()
	return response

def getInfo(tipo, numero, ano):
	base_url = "http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ObterProposicao?"
	url = base_url + "tipo=" + tipo + "&numero=" + numero + "&ano=" + ano
	soup = xmlopen(url, 'info'+tipo+'-'+numero+'-'+ano)
	soup = xmltodict.parse(soup)
	return soup['proposicao']

def getVoto(tipo, numero, ano):
	base_url = "http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ObterVotacaoProposicao?"
	url = base_url + "tipo=" + tipo + "&numero=" + numero + "&ano=" + ano
	soup = xmlopen(url, 'voto-'+tipo+'-'+numero+'-'+ano)
	if soup:
		soup = xmltodict.parse(soup)
		soup = soup['proposicao']['Votacoes']['Votacao']
	else:
		soup = getDeputados()
	return soup

def getDeputados():
	url = "http://www.camara.gov.br/SitCamaraWS/Deputados.asmx/ObterDeputados"
	raw = xmlopen(url, 'deputados')
	raw = xmltodict.parse(raw)
	soup = []
	for d in raw['deputados']['deputado']:
		deputado = {}
		deputado['@Nome'] = d['nomeParlamentar']
		deputado['@Partido'] = d['partido']
		deputado['@UF'] = d['uf']
		deputado['@Email'] = d['email']
		deputado['@Voto'] = None #getVoto(d['email'])
		soup.append(deputado)
	return [{ "votos" : { "Deputado" : [soup] } }]

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World!"

@app.route("/<tipo>/<numero>/<ano>")
def projeto(tipo, numero, ano):
	p = { "info" : getInfo(tipo, numero, ano), "voto" : getVoto(tipo, numero, ano)}
	soup = json.dumps(p)
	return soup

if __name__ == "__main__":
    app.run(debug=True)