"""Agente extractor de datos de artículos

Este agente se encarga de la extracción de datos de la revista
https://www.sciencedirect.com/journal/swarm-and-evolutionary-computation

Para funcionar, el script requiere que estén instaladas las
bibliotecas `bs4`, `date` `numpy`, re`, `requests` y `time`, utilizadas para formatear un poco el html, ver las fechas, hacer una función de valor aleatorio, expresiones regulares, captar datos y poder esperar un período de tiempo según lo obtenido por numpy para evitar que nos bloqueen, respectivamente.


"""
# Ok primero de todo importamos las bibliotecas que nos interesan
from bs4 import BeautifulSoup
#from lxml import html
import numpy as np
import re
import requests
#import socks
import time
from datetime import datetime
#from urllib.requests import *

def getHumano (url,
               proxy=None,
               accept='application/json;q=0.9,*/*;q=0.8', 
               acceptEncoding='gzip, deflate', 
               acceptLanguage='en-US, en;q=0.9, es;q=0.8', 
               userAgent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0', 
               referer='https://duckduckgo.com/'):
    """Función auxiliar empleada para realizar un GET creíble que parezca humano a una url. Se ha dejado con parámetros de Ubuntu por defecto"""

    
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    # Por algún extraño motivo usar esto provoca un error "Missing dependencies for SOCKS support." a pesar de tener instalado pysocks.
    response = ""
    if proxy==None:
        response = requests.get(url, headers = {
            'Accept': accept,
            'Accept-Encoding': acceptEncoding,
            'Accept-Language': acceptLanguage,
            'User-Agent': userAgent,
            'Referer' : referer
            })
        proxyWork=proxy
    else:
        try:
            response = requests.get(url, headers = {
                'Accept': accept,
                'Accept-Encoding': acceptEncoding,
                'Accept-Language': acceptLanguage,
                'User-Agent': userAgent,
                'Referer' : referer
                },
                proxies=proxies
            )
            print("Utilizando proxy Tor")
            proxyWork=proxy
        except:
            print("No tenemos proxy, ten cuidado")
            response = requests.get(url, headers = {
                'Accept': accept,
                'Accept-Encoding': acceptEncoding,
                'Accept-Language': acceptLanguage,
                'User-Agent': userAgent,
                'Referer' : referer
                }#, proxies=proxies
            )
            proxyWork=None
    return response, proxyWork
    

def extract(n, since=None, urlarticuloBaseEntrada='https://www.sciencedirect.com/', elJournalABuscarEntrada = 'journal/swarm-and-evolutionary-computation', codif='utf-8'):
    """Extrae la información de los últimos n artículos hasta since
  
    :param n: El número de artículos de los que extraer datos. Debe
        ser un entero mayor que 0.
    :param since: La fecha desde cuándo sacar la información. Debe
        ser un objeto date. si no se especifica, se presupone la
        fecha del día en el que se ejecuta la función
    :return: Una lista de tuplas donde cada tupla tendrá la
        siguiente forma: (str, str, str, str, List[str], List[str])

    *Nombre de la publicación: El nombre de la publicación (no tiene por qué extraerse, ya que para cada grupo sólo se usa una única publicación.
    *Título del artículo: Cadena de texto sin caracteres extraños y sin espacios alrededor.
    *Fecha de publicación: Cadena de texto en en formato YYYYMMDD. Por ejemplo, el 10 de febrero de 2023 sería 20230210.
    *Abstract del artículo: Cadena de texto sin caracteres extraños y sin espacios alrededor.
    *Palabras clave: En el caso de que exista, lista de cadenas de texto sin caracteres extraños y sin espacios alrededor. Si no existe, una lista vacía.
    
    # PASO 0 Se listan los patrones a buscar. Se recomiendan compilar para reducir su peso, sobre todo si se usan mucho.
    
    # PASO 1: búsqueda de articulos en cada volumen.
    
        # PASO 1.1 el título de la publicación y todos los volúmenes del journal se extraen de la página principal de issues.
        # PASO 1.2 para cada volumen se extraen todos los artículos científicos y se ponen en una variable auxiliar.
    
    # PASO 2: Búsqueda de info adicional para cada artículo candidato.
        # 2.1 Primero visitamos la página específica de cada artículo para sacar su fecha de publicación.
        # 2.2 si la fecha dada es mayor que la obtenida, no incluimos el artículo. Acá hemos supuesto que lo que nos piden es que busquemos artículos más viejos que los de la fecha actual.
        # 2.3 obtenemos el abstracto (ignormaos las highlights) y las palabras clave.
        # 2.4 se crea el objeto unArtículo con los valores extraídos anteriormente.
        # 2.5 se hace append a la respuesta.
        
    
    """


    result = []
    
    fecha = ""
    if n <= 0:
        print ("Se ha introducido un número de artículos inválido. Se tomará solo un artículo")
        n = 1
    if not since:
        """
        # si no se especifica, se presupone la fecha del día en el que se ejecuta la función.
        # NOTA: como el universo es en situaciones normales lineal y esto no es una TARDIS, podemos quitarnos lo de buscar la fecha actual y no utilizar from datetime import date, fechaDesde = date.today()
        """
        fecha = "00000000" # esto está acá por si hubiese errores que lo reconozcamos como código de error
    else:
        # Si la fecha existe pues debería ser Date, la pasamos a nuestro querido formato YYYYMMDD para ser procesada más tarde
        fecha = str(since.year).rjust(4, '0')+str(since.month).rjust(2, '0')+str(since.day).rjust(2, '0')
        print("Fecha encontrada, desde: "+fecha)
            
    
    
    # PETICIONES HTTPS
    """Utilizamos requests para obtener la información de la página, usando el mayor número de cabeceras para parecer humanos"""
    urlarticuloBase = urlarticuloBaseEntrada                # Nos interesa mucho tener esta separada para el paso 2.1
    elJournalABuscar = elJournalABuscarEntrada              # Así queda modular y bonito
    issues = "/issues"
    print("Analizando journal: GET "+urlarticuloBase+elJournalABuscar+issues+"...")
    response, proxyFunciona = getHumano(urlarticuloBase+elJournalABuscar+issues, "Tor")
    contenido = response.content
    response.encoding = codif                               # Puede sernos útil para cambiarlo más tarde
    texto = response.text                                   # TEXTO
    cabeceras = response.headers                            # CABECERAS
    print("...GET del journal completado")
    #print(cabeceras)
    #print(codif)
    #print(texto)
    #tree = html.fromstring(contenido)
    #print(tree.xpath('//*/text()'))
    
    # EXTRACCIÓN
    print("Extracción de datos del journal: INICIANDO")
    
    patronVolumenes = re.compile('<a class="anchor js-issue-item-link text-m anchor-default" href="([a-zA-Z0-9_ \/-]*)"')
    patronTituloPublicacion = re.compile('<a class="anchor js-title-link [a-zA-Z0-9_ \/-]*" href="[a-zA-Z0-9_ \/-]*" usageZone="jrnl_banner" id="journal-title"><span class="anchor-text">(.*?)<\/span>')
    patronTituloArticulo = re.compile('<dl class="js-article article-content"><dd class="article-info text-xs">.*?<span class="js-article-subtype">Research article<\/span>.*?<\/dd><dt><h3 class="text-m u-font-serif u-display-inline"><a(?: id="[a-zA-Z0-9_ \/-]*"|) class="anchor article-content-title[a-zA-Z0-9_ \/-]*" href="([a-zA-Z0-9_ \/)(-]*)" (?:data-aa-name="Article title" |)id="([a-zA-Z0-9_ \/-]*)" usageZone="rslt_list_item"><span class="anchor-text"><span(?: class="js-article-title"|)>(.*?)<\/span')
    
    patronAutores = re.compile('<div class="Banner" id="banner"><div class="wrapper truncated"><div class="AuthorGroups text-s"><div class="author-group" id="author-group"><span class="sr-only">Author links open overlay panel<\/span>((?:.*?<span class="given\-name">.*?<\/span> <span class="text surname">.*?<\/span>.*?<\/span>)+)')
    patronAutorBueno = re.compile('<span class="given\-name">(.*?)<\/span> <span class="text surname">(.*?)<\/span>.*?<\/span>')
    patronFecha = re.compile('<meta name="citation_publication_date" content="([0-9]+)\/([0-9]+)\/([0-9]+)" \/>')
    patronAbstract = re.compile('<div class="Abstracts[a-zA-Z0-9_ \/-]*" id="abstracts">(.*?<div class="abstract author" id="[a-zA-Z0-9_ \/-]*"><h2 class="section-title[a-zA-Z0-9_ \/-]*">Abstract<\/h2><div id="[a-zA-Z0-9_ \/-]*"><p id="[a-zA-Z0-9_ \/-]*">.*?<\/p>)') # Hemos decidido Tener en cuenta los abstract highlights como parte del abstract y por lo tanto permitir su formato y el caracter utilizado para puntos de una lista de highlights.
    patronKeywords = re.compile('(<div class="Keywords[a-zA-Z0-9_ \/-]*"><div id="[a-zA-Z0-9_ \/-]*" class="keywords-section[a-zA-Z0-9_ \/-]*">(?:<h2 class="section-title[a-zA-Z0-9_ \/-]*">Keywords<\/h2>)*?.*?<div id="[a-zA-Z0-9_ \/)(-]*" class="keyword"><span(?: id="[a-zA-Z0-9_ \/-]*"|)>[a-zA-Z0-9_ \/)(-]*<\/span><\/div><\/div><\/div>)')
    #patronKeywords = re.compile('(<div class="Keywords[a-zA-Z0-9_ \/-]*"><div id="[a-zA-Z0-9_ \/-]*" class="keywords-section[a-zA-Z0-9_ \/-]*">(?:<h2 class="section-title[a-zA-Z0-9_ \/-]*">Keywords<\/h2>)*?.*?(<div id="[a-zA-Z0-9_ \/-]*" class="keyword"><span(?: id="[a-zA-Z0-9_ \/-]*"|)>[a-zA-Z0-9_ \/-]*<\/span>)*?<\/div><\/div><\/div>)')
    patronKeywordsBueno = re.compile('<div id="[a-zA-Z0-9_ \/-]*" class="keyword"><span(?: id="[a-zA-Z0-9_ \/-]*"|)>([a-zA-Z0-9_ \/-]*)<\/span>')
    
    # Inicialmente probamos con findall, es mejor usar search pero al menos nos avisa de si algo extraño ocurre
    Nombre_de_la_publicación = re.findall(patronTituloPublicacion, texto)
    volúmenes = re.findall(patronVolumenes, texto)
    if len(Nombre_de_la_publicación) > 1:
        print ("Algo raro ocurre, es posible que nos hayan engañado o hayan actualizado el formato")
    
    infoSuperBasic = []
    totalArts = 0
    print("Número de volúmenes en el journal: "+str(len(volúmenes)))
    print("Analizando volúmenes del journal:")
    for i in volúmenes:
        print(i)
        urlTotal = urlarticuloBase + i # url base + url parcial = url total
        responseA, proxyFunciona = getHumano(urlTotal, proxyFunciona)
        responseA.encoding = codif                               # Puede sernos útil para cambiarlo más tarde
        textoA = responseA.text
        # Esto me devuelve tres grupos para cada artículo encontrado: la url parcial del artículo, un identificativo especial del html y su título. Esto resulta ventajoso para el futuro
        infoSuperBasic1 = re.findall(patronTituloArticulo, textoA)
        # Pongo todos los artículos en la lista general
        for articulo in infoSuperBasic1:
            infoSuperBasic.append(articulo)
        totalArts = totalArts + len(infoSuperBasic1)
        time.sleep(np.random.uniform(low=0.25, high=0.8))
        
    print("Número total de artículos de investigación en el journal:"+str(totalArts))
    #print(infoSuperBasic)
    print("Procediendo a cribar los artículos a número y fecha pedidos")
    i = 0 # cont num articulos válidos
    artCon = 0 # contador num de articulos visitados
    
    while artCon < totalArts and i < n:
        # Hacemos petición GET de esta nueva url
        urlTotal = urlarticuloBase + infoSuperBasic[artCon][0] # url base + url parcial = url total
        responseA, proxyFunciona = getHumano(urlTotal, proxyFunciona)
        responseA.encoding = codif                               # Puede sernos útil para cambiarlo más tarde
        textoA = responseA.text  
        
        # Dormir aleatoriamente para prevenir que nos identifiquen. Acá para que todos los árboles de decisión duerman
        time.sleep(np.random.uniform(low=0.25, high=0.8))
        
        # Antes de todo cribar solo los research articles, en sí ya se cribaron antes en la expresión regular del título, pero por si acaso. Sabemos que los que no son de investigación tienen un título preciso 
        if infoSuperBasic[artCon][2] == "Editorial Board":
            print("articulo no de investigación, descartando...")
            artCon = artCon + 1
            continue
        
        # Obtenemos autores. EL primero es para englobar todos y el segundo para cribarlos del primero bien
        infoTempAutores = re.findall(patronAutores, textoA)
        if len(infoTempAutores) > 0:
            infoTempAutoresBuena = re.findall(patronAutorBueno, infoTempAutores[0])
        else:    
            infoTempAutoresBuena = "ERROR!"
            print("error")
        
        # Obtenemos la fecha y la ponemos en el formato YYYYMMDD
        infoFecha = re.findall(patronFecha, textoA)
        # Como son ingleses usan Año/Día/Mes, así que lo corregimos
        fechaFormateada = infoFecha[0][0].rjust(4, '0')+infoFecha[0][2].rjust(2, '0')+infoFecha[0][1].rjust(2, '0')
        # Si tenemos una fecha base, comparamos con ella para decidir que hacer
        if not since:
            print("Sin verificación de fecha")
        elif int(fechaFormateada) > int(fecha):
            print("Articulo "+str(artCon)+" de título "+infoSuperBasic[artCon][2]+" y fecha "+fechaFormateada+" más nuevo de lo pedido, descartando...")
            artCon = artCon + 1
            continue
        else:
            print("Artículo de fecha adecuada encontrado")
        
        # Obtenemos el abstracto, que en la página de donde lo extraemos es un párrafo a veces precedido de highlights
        Abstract_del_artículo = re.findall(patronAbstract, textoA)
        
        # Obtenemos la sección de keywords para luego afinar en dicha subsección
        Palabras_clave_temp = re.findall(patronKeywords, textoA)
        if len(Palabras_clave_temp) > 0:
            Palabras_clave = re.findall(patronKeywordsBueno, Palabras_clave_temp[0])
        else:
            Palabras_clave = []
        
        unArticulo = ["No encontrado", 
                      "Sin título?", 
                      "Aparentemente fuera del vórtice del Tiempo", 
                      "N/A", 
                      "", 
                      [], 
                      urlTotal]
        
        if Nombre_de_la_publicación[0]:
            unArticulo[0] = Nombre_de_la_publicación[0]
        if infoSuperBasic[artCon][2]:
            unArticulo[1] = infoSuperBasic[artCon][2]           
        if fechaFormateada:
            unArticulo[2] = fechaFormateada    
        if len(Abstract_del_artículo) >= 1 and Abstract_del_artículo[0]:
            # Buscamos algo para limpiarnos el abstracto un poco en caso de caracteres de formato extraño al pasar de html a string
            soup = BeautifulSoup(Abstract_del_artículo[0])
            unArticulo[3] = soup.get_text()
        if Palabras_clave:
            unArticulo[4] = Palabras_clave
        if infoTempAutoresBuena:
            unArticulo[5] = infoTempAutoresBuena
        
        result.append(unArticulo)
        
        i = i + 1
        artCon = artCon + 1
        print("next")
        
    print("Extracción de datos del journal: COMPLETADO")
    return result

if __name__ == '__main__':
    for row in extract(n=20):
        print(row)
