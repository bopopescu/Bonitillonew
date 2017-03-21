'''
    Ultimate Whitecream
    Copyright (C) 2015 Whitecream

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re

import xbmcplugin
from resources.lib import utils

addon = utils.addon

sortlistxt = [addon.getLocalizedString(30022), addon.getLocalizedString(30023), addon.getLocalizedString(30024),
            addon.getLocalizedString(30025)]   


@utils.url_dispatcher.register('20')
def XTMain():
    utils.addDir('[COLOR hotpink]Categories[/COLOR]','http://xtheatre.net/categories/',22,'','')
    utils.addDir('[COLOR hotpink]Search[/COLOR]','http://xtheatre.net/page/1/?s=',24,'','')
    Sort = '[COLOR hotpink]Current sort:[/COLOR] ' + sortlistxt[int(addon.getSetting("sortxt"))]
    utils.addDir(Sort, '', 25, '', '')    
    XTList('http://xtheatre.net/category/movies/page/1/',1)
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('25')
def XTSort():
    addon.openSettings()
    XTMain()


@utils.url_dispatcher.register('22', ['url'])
def XTCat(url):
    cathtml = utils.getHtml(url, '')
    match = re.compile('src="([^"]+)"[^<]+</noscript>.*?<a href="([^"]+)"[^<]+<span>([^<]+)</s.*?">([^<]+)', re.DOTALL | re.IGNORECASE).findall(cathtml)
    for img, catpage, name, videos in match:
        catpage = catpage + 'page/1/'
        name = name + ' [COLOR deeppink]' + videos + '[/COLOR]'
        utils.addDir(name, catpage, 21, img, 1)
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('24', ['url'], ['keyword'])
def XTSearch(url, keyword=None):
    searchUrl = url
    if not keyword:
        utils.searchDir(url, 24)
    else:
        title = keyword.replace(' ','+')
        searchUrl = searchUrl + title
        print "Searching URL: " + searchUrl
        XTList(searchUrl, 1)


@utils.url_dispatcher.register('21', ['url'], ['page'])
def XTList(url, page=1):
    sort = getXTSortMethod()
    if re.search('\?', url, re.DOTALL | re.IGNORECASE):
        url = url + '&filtre=' + sort + '&display=extract'
    else:
        url = url + '?filtre=' + sort + '&display=extract'
    try:
        listhtml = utils.getHtml(url, '')
    except:
        utils.notify('Oh oh','It looks like this website is down.')
        return None
    match = re.compile(r'src="([^"]+?)" class="attachment.*?<a href="([^"]+)" title="([^"]+)".*?<div class="right">(.*?)</div>\s+</li>', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for img, videopage, name, desc in match:
        name = utils.cleantext(name)
        desc = utils.cleanhtml(desc)
        desc = utils.cleantext(desc)
        utils.addDownLink(name, videopage, 23, img, desc)
    if re.search('<link rel="next"', listhtml, re.DOTALL | re.IGNORECASE):
        npage = page + 1        
        url = url.replace('/page/'+str(page)+'/','/page/'+str(npage)+'/')
        utils.addDir('Next Page ('+str(npage)+')', url, 21, '', npage)
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('23', ['url', 'name'], ['download'])
def XTVideo(url, name, download=None):
    utils.PLAYVIDEO(url, name, download)


def getXTSortMethod():
    sortoptions = {0: 'date',
                   1: 'title',
                   2: 'views',
                   3: 'likes'}
    sortvalue = addon.getSetting("sortxt")
    return sortoptions[int(sortvalue)]    
