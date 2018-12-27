# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para TVG
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 
from core import jsontools

DEBUG = False
CHANNELNAME = "tvg"

def mainlist(item):
    logger.info("tvalacarta.channels.tvg mainlist")
    itemlist=[]
    itemlist.append( Item(channel=CHANNELNAME, title="Directos"    , action="loadlives", folder=True))
    itemlist.append( Item(channel=CHANNELNAME, title="Últimos"     , action="novedades"  , url="http://www.crtvg.es/tvg/a-carta"))
    itemlist.append( Item(channel=CHANNELNAME, title="Do A ao Z"   , action="programas"  , url="http://www.crtvg.es/tvg/a-carta"))
    itemlist.append( Item(channel=CHANNELNAME, title="Categorías"  , action="categorias" , url="http://www.crtvg.es/tvg/a-carta"))
    return itemlist

def directos(item=None):
    logger.info("tvalacarta.channels.tvg directos")

    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="TVG Europa",   url="http://europa-crtvg.flumotion.com/playlist.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/tvg.png", category="Autonómicos", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="TVG América",   url="http://america-crtvg.flumotion.com/playlist.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/tvg.png", category="Autonómicos", action="play", folder=False ) )

    return itemlist

def loadlives(item):
    logger.info("tvalacarta.channels.rtve play loadlives")

    itemlist = []

    for directo in directos(item):
        itemlist.append(directo)

    return itemlist

def novedades(item):
    logger.info("tvalacarta.channels.tvg novedades")
    itemlist = []

    # Lee la página del programa
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,"LTIMAS ENTRADAS -->(.*?)<!--")

    # Extrae los videos
    '''
    <img src="/files/thumbs/IMG0788.jpg" alt="A Revista FDS" />
    </div>
    <div id="info-programa-1777516" class="info-programa">
    <div id="titulo-programa-1777516" class="listadoimagenes-titulo">
    A Revista FDS
    </div>
    <div class="listadoimagenes-subtitulo">
    A Revista FDS                                       
    </div>
    <div id="data-programa-1777516" class="entrada-blog-fecha">
    31/01/2016
    '''
    patron  = '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<div id="imagen-programa[^<]+'
    patron += '<img src="([^"]+)".*?'
    patron += '<div id="data-programa[^>]+>([^<]+)<'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle,scrapedthumbnail,fecha in matches:
        title = scrapedtitle.strip()+" - "+fecha.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="tvg", url=url, thumbnail=thumbnail, plot=plot , folder=False) )

    return itemlist

def categorias(item):
    logger.info("tvalacarta.channels.tvg categorias")
    itemlist=[]
    
    # Extrae los programas
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,"<!-- LISTADO POR CAT(.*?)</ul>")
    
    '''
    <div class="item-a-carta titulo-a-carta">
    <h3>
    Series												</h3>
    </div>
    '''
    '''
    <div class="item-a-carta">
    <a href="/tvg/a-carta/programa/15-zona-cerco-aos-matalobos"
    title="15 Zona: cerco aos Matalobos">
    15 Zona: cerco aos Matalobos
    </a>
    </div>
    '''
    patron = '<div class="item-a-carta(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for bloque in matches:
        if "<h3>" in bloque:
            scrapedtitle = "[COLOR blue]"+scrapertools.get_match(bloque,"<h3>([^<]+)</h3>").strip().upper()+"[/COLOR]"
            scrapedurl=""
            folder=False
        else:
            scrapedtitle = "  "+scrapertools.get_match(bloque,'<a href="[^"]+"[^>]+>([^<]+)<').strip()
            scrapedurl = urlparse.urljoin(item.url,scrapertools.get_match(bloque,'<a href="([^"]+)"[^>]+>[^<]+<').strip())
            folder=True

        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, page=scrapedurl , thumbnail=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle , category = item.category , folder=folder) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.tvg programas")
    itemlist=[]
    
    # Extrae los programas
    data = scrapertools.cachePage(item.url)
    #logger.info("data="+data)

    data = scrapertools.get_match(data,"<!-- LISTADO DE LA A A LA Z -->(.*?)<!-- LISTADO POR CAT")
    
    '''
    <div class="item-a-carta">
    <a href="/tvg/a-carta/programa/15-zona-cerco-aos-matalobos"
    title="15 Zona: cerco aos Matalobos">
    15 Zona: cerco aos Matalobos
    </a>
    </div>
    '''
    
    patron  = '<div class="item-a-carta"[^<]+'
    patron += '<a href="([^"]+)"[^>]+>([^<]+)<'
                                                
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for url,title in matches:
        scrapedtitle = title.strip()
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, page=scrapedurl , thumbnail=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle , category = item.category , folder=True) )

    return itemlist

def episodios(item, load_all_pages = False):
    logger.info("tvalacarta.channels.tvg episodios")
    itemlist = []

    # Lee la página del programa y extrae el id_programa
    if "/ax/" in item.url:
        headers=[]
        headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:17.0) Gecko/20100101 Firefox/17.0"])
        headers.append(["X-Requested-With","XMLHttpRequest"])
        headers.append(["Referer",item.url])
        data = scrapertools.cache_page(item.url, post="", headers=headers)
        data = data.replace("\\n"," ")
        data = data.replace("\\\"","\"")
        data = data.replace("\\/","/")
    else:
        data = scrapertools.cache_page(item.url)
        try:
            id_programa = scrapertools.get_match(data,"initAlaCartaBuscador.(\d+)")
        except:
            id_programa = ""
        
        # Lee la primera página de episodios
        #http://www.crtvg.es/ax/tvgalacartabuscador/programa:33517/pagina:1/seccion:294/titulo:/mes:null/ano:null/temporada:null
        logger.info("tvalacarta.channels.tvg videos - hay programa")
        url = "http://www.crtvg.es/ax/tvgalacartabuscador/programa:"+id_programa+"/pagina:1/seccion:294/titulo:/mes:null/ano:null/temporada:null"
        headers=[]
        headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:17.0) Gecko/20100101 Firefox/17.0"])
        headers.append(["X-Requested-With","XMLHttpRequest"])
        headers.append(["Referer",item.url])
        data = scrapertools.cache_page(url, post="", headers=headers)
        data = data.replace("\\n"," ")
        data = data.replace("\\\"","\"")
        data = data.replace("\\/","/")

    #logger.info("data="+data)

    # Extrae los videos
    '''
    <tr>                  
    <td class="a-carta-resultado-titulo">                      
    <a href="\/tvg\/a-carta\/rea-publica-74" title="\u00c1rea p\u00fablica">\u00c1rea p\u00fablica<\/a>                 <\/td>                                                       <td class="a-carta-resultado-tempada">                                           <\/td>                                     <td class="a-carta-resultado-data">                  26\/01\/2016 18:30                 <\/td>                              <\/tr>
    '''

    patron  = '<tr[^<]+'
    patron += '<td class="a-carta-resultado-titulo[^<]+'
    patron += '<a href="([^"]+)"\s+title="([^"]+)".*?'
    patron += '<td class="a-carta-resultado-data">(.*?)</td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,fecha in matches:
        title = scrapedtitle.strip()
        json_title = jsontools.load_json('{"title":"'+title+'"}')
        title = json_title["title"]
        title = scrapertools.htmlclean(title)+" - "+fecha.strip()

        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        aired_date = scrapertools.parse_date(fecha)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="tvg", url=url, thumbnail=thumbnail, plot=plot , show=item.show , aired_date=aired_date, folder=False) )

    #<a href=\"#\" title=\"Seguinte\" onclick=\"return posteriorpaginaclick(33517, 2, 294)
    patron  = '<a href="\#" title="Seguinte" onclick="return posteriorpaginaclick\((\d+), (\d+), (\d+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = ">>> Página siguiente"
        #http://www.crtvg.es/ax/tvgalacartabuscador/programa:33517/pagina:2/seccion:294/titulo:/mes:null/ano:null/temporada:null
        scrapedurl = "http://www.crtvg.es/ax/tvgalacartabuscador/programa:%s/pagina:%s/seccion:%s/titulo:/mes:null/ano:null/temporada:null" % (match[0],match[1],match[2])
        scrapedthumbnail = urlparse.urljoin(item.url,match[2])
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        next_page_item = Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show , category = item.category , folder=True)
        if load_all_pages:
            itemlist.extend( episodios(next_page_item, load_all_pages) )
        else:
            itemlist.append( next_page_item )

        break

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # Menu
    mainlist_items = mainlist(Item())

    # Novedades
    novedades_items = novedades(mainlist_items[0])
    if len(novedades_items)==0:
        return False

    # Categorías
    categorias_items = categorias(mainlist_items[2])
    if len(categorias_items)==0:
        return False

    # Todos los programas
    programas_items = programas(mainlist_items[1])
    if len(programas_items)==0:
        return False

    for programa_item in programas_items:
        episodios_items = episodios(programas_items[0])
        if len(episodios_items)>0:
            return True

    return False
