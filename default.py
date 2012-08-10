
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, xbmcaddon, xbmcvfs, buggalo

plugin =  'Revision3'
__author__ = 'stacked <stacked.xbmc@gmail.com>'
__url__ = 'http://code.google.com/p/plugin/'
__date__ = '08-05-2012'
__version__ = '2.0.5'
settings = xbmcaddon.Addon(id='plugin.video.revision3')
buggalo.SUBMIT_URL = 'http://www.xbmc.byethost17.com/submit.php'
dbg = False
dbglevel = 3
next_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'next.png' )
more_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'more.png' )
downloads_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'downloads.png' )
old_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'old.png' )
current_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'current.png' )
search_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'search.png' )

import CommonFunctions
common = CommonFunctions
common.plugin = plugin + ' ' + __version__

import SimpleDownloader as downloader
downloader = downloader.SimpleDownloader()

def build_main_directory(url):
	path = url
	html = common.fetchPage({"link": url})['content']
	shows = common.parseDOM(html, "ul", attrs = { "id": "shows" })[0]
	url_name = re.compile('<h3><a href="(.+?)">(.+?)</a></h3>').findall(shows)
	image = re.compile('class="thumbnail"><img src="(.+?)" /></a>').findall(shows)
	plot = common.parseDOM(shows, "p", attrs = { "class": "description" })
	if settings.getSetting('folder') == 'true' and settings.getSetting( 'downloadPath' ) and path == 'http://revision3.com/shows/':
		url = settings.getSetting("downloadPath")
		listitem = xbmcgui.ListItem(label = '[ ' + settings.getLocalizedString( 30012 ) + ' ]', iconImage = downloads_thumb, thumbnailImage = downloads_thumb )
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = listitem, isFolder = True)
	if path == 'http://revision3.com/shows/':
		listitem = xbmcgui.ListItem(label = '[ ' + settings.getLocalizedString( 30013 ) + ' ]', iconImage = current_thumb, thumbnailImage = current_thumb)
		u = sys.argv[0] + "?mode=1&name=" + urllib.quote_plus(settings.getLocalizedString( 30013 )) + "&url=" + urllib.quote_plus('http://revision3.com/episodes/page?&hideArrows=1&type=recent&page=1')
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)
		listitem = xbmcgui.ListItem(label = '[ ' + settings.getLocalizedString( 30014 ) + ' ]', iconImage = old_thumb, thumbnailImage = old_thumb)
		u = sys.argv[0] + "?mode=3&url=" + urllib.quote_plus('http://revision3.com/shows/archive')
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)
		listitem = xbmcgui.ListItem(label = '[ ' + settings.getLocalizedString( 30015 ) + ' ]', iconImage = search_thumb, thumbnailImage = search_thumb)
		u = sys.argv[0] + "?mode=4&url=" + urllib.quote_plus('search')
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)
	count = 0
	for url, name in url_name:
		fanart = url.replace('/','')
		url = 'http://revision3.com' + url + '/episodes'
		listitem = xbmcgui.ListItem(label = name, iconImage = image[count].replace('160x160','200x200'), thumbnailImage = image[count].replace('160x160','200x200'))
		listitem.setProperty('fanart_image',settings.getSetting(fanart))
		listitem.setInfo( type = "Video", infoLabels = { "Title": name, "Studio": plugin, "Plot": plot[count] } )
		u = sys.argv[0] + "?mode=1&name=" + urllib.quote_plus(name) + "&url=" + urllib.quote_plus(url)
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)
		count += 1
	xbmcplugin.addSortMethod( handle = int(sys.argv[ 1 ]), sortMethod = xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_sub_directory(url, name):
	saveurl = url
	studio = name
	savestudio = name
	html = common.fetchPage({"link": url})['content']
	ret = common.parseDOM(html, "div", attrs = { "id": "main-episodes" })
	pageLoad = common.parseDOM(ret, "a", ret = "onclick")
	if len(ret) == 0:
		ret = common.parseDOM(html, "div", attrs = { "id": "all-episodes" })
		pageLoad = common.parseDOM(ret, "a", ret = "onclick")
	if len(ret) == 0:
		ret = common.parseDOM(html, "ul", attrs = { "class": "episode-grid" })
		pageLoad = common.parseDOM(html, "a", ret = "onclick")
	current = common.parseDOM(html, "span", attrs = { "class": "active" })
	episodes = common.parseDOM(ret, "li", attrs = { "class": "episode item" })
	try:
		img = common.parseDOM(episodes[0], "img", ret = "src")[0]
		downloads = 'http://revision3.com/' + img.rsplit('/')[6] + '/' + img.rsplit('/')[6] + '_downloads'
		fresult = common.fetchPage({"link": downloads})['content']
		data = re.compile( '<a href="(.+?)" target="_blank">1920x1200</a>' ).findall(fresult)
		if len(data) > 1:
			fanart = data[1]
		else:
			fanart = data[0]
		settings.setSetting(img.rsplit('/')[6], fanart)
		if studio == settings.getLocalizedString( 30013 ):
			fanart = ''
	except:
		fanart = ''
	try:
		child = common.parseDOM(html, "div", attrs = { "id": "child-episodes" })
		label = common.parseDOM(html, "a", attrs = { "href": "#child-episodes" })[0]
		childshow = common.parseDOM(child, "a", attrs = { "class": "thumbnail" }, ret = "href" )[0].rsplit('/')[1]
		csaveurl = 'http://revision3.com/' + childshow + '/episodePage?type=recent&limit=15&hideShow=1&hideArrows=1&page=1'
		listitem = xbmcgui.ListItem( label = '[ ' + label + ' ]', iconImage = more_thumb, thumbnailImage = more_thumb )
		listitem.setProperty('fanart_image',fanart)
		u = sys.argv[0] + "?mode=1&name=" + urllib.quote_plus(studio) + "&url=" + urllib.quote_plus(csaveurl)
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)
	except:
		pass
	try:
		strs = 'http://revision3.com' + pageLoad[-1:][0].rsplit('\'')[1]
		params = common.getParameters(strs)
		saveurl = strs.rstrip('&page=' + params['page']) + '&page=' + str( int(current[0]) + 1 )
		if int(params['page']) > int(current[0]):
			next = True
		else:
			next = False
	except:
		next = False
	for data in episodes:
		thumb = common.parseDOM(data, "img", ret = "src")[0].replace('small.thumb','medium.thumb')
		plot = clean(common.parseDOM(data, "img", ret = "alt")[0])
		name = clean(common.stripTags(common.parseDOM(data, "a")[1]))
		cut = common.parseDOM(data, "a")[1]
		try:
			studio = clean(common.parseDOM(cut, "strong")[0])
		except:
			pass
		name = name.replace(studio + '   ','')
		url = 'http://revision3.com' + common.parseDOM(data, "a", attrs = { "class": "thumbnail" }, ret = "href")[0]
		try:
			episode = name.rsplit(' ')[1]
			date = name.rsplit(' ')[3].rsplit('/')[1] + '.'  + name.rsplit(' ')[3].rsplit('/')[0] + '.' + name.rsplit(' ')[3].rsplit('/')[2]
		except:
			episode = '0'
			date = '00.00.0000'
		duration = name[-6:].rstrip(')').replace('(','')
		listitem = xbmcgui.ListItem(label = plot, iconImage = thumb, thumbnailImage = thumb)
		listitem.setProperty('fanart_image',fanart)
		listitem.setInfo( type = "Video", infoLabels = { "Title": plot, "Director": plugin, "Studio": studio, "Plot": plot, "Episode": int(episode), "Date": date, "Duration": duration } )
		listitem.setProperty('IsPlayable', 'true')
		u = sys.argv[0] + "?mode=2&name=" + urllib.quote_plus(plot) + "&url=" + urllib.quote_plus(url) + "&plot=" + urllib.quote_plus(plot) + "&studio=" + urllib.quote_plus(studio) + "&episode=" + urllib.quote_plus(episode) + "&thumb=" + urllib.quote_plus(thumb)
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = False)
	if next == True:
		listitem = xbmcgui.ListItem( label = settings.getLocalizedString( 30016 ) + ' (' + str( int(current[0]) + 1 ) + ')' , iconImage = next_thumb, thumbnailImage = next_thumb )
		listitem.setProperty('fanart_image',fanart)
		u = sys.argv[0] + "?mode=1&name=" + urllib.quote_plus(savestudio) + "&url=" + urllib.quote_plus(saveurl)
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)	
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_EPISODE )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_search_directory(url):
	if url == 'search':
		search = common.getUserInput("Enter search term", "").replace(' ','+')
		url = 'http://revision3.com/search/page?type=video&q=' + search + '&limit=10&page=1'
	html = common.fetchPage({"link": url})['content']
	current = common.parseDOM(html, "span", attrs = { "class": "active" })
	pageLoad = common.parseDOM(html, "a", ret = "onclick")
	try:
		strs = 'http://revision3.com' + pageLoad[-1:][0].rsplit('\'')[1]
		params = common.getParameters(strs)
		saveurl = strs.rstrip('&page=' + params['page']) + '&page=' + str( int(current[0]) + 1 )
		if int(params['page']) > int(current[0]):
			next = True
		else:
			next = False
	except:
		next = False
	episodes = common.parseDOM(html, "li", attrs = { "class": "video" })
	if len(episodes) == 0:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok( plugin , settings.getLocalizedString( 30009 ) + '\n' + settings.getLocalizedString( 30010 ) )
		return
	for data in episodes:
		thumb = common.parseDOM(data, "img", ret = "src")[0]
		url = common.parseDOM(data, "a", attrs = { "class": "thumbnail" }, ret = "href" )[0]
		url = clean(url.replace('http://www.videosurf.com/webui/inc/go.php?redirect=','')).replace('&client_id=revision3','')
		title = clean(common.parseDOM(data, "a", attrs = { "class": "title" })[0])
		plot = clean(common.stripTags(common.parseDOM(data, "div", attrs = { "class": "description" })[0]))
		try:
			studio = title.rsplit(' - ')[1]
		except:
			studio = ''
		listitem = xbmcgui.ListItem(label = title, iconImage = thumb, thumbnailImage = thumb)
		listitem.setInfo( type = "Video", infoLabels = { "Title": title, "Director": plugin, "Studio": studio, "Plot": plot } )
		listitem.setProperty('IsPlayable', 'true')
		u = sys.argv[0] + "?mode=2&name=" + urllib.quote_plus(title) + "&url=" + urllib.quote_plus(url) + "&plot=" + urllib.quote_plus(plot) + "&studio=" + urllib.quote_plus(studio) + "&episode=" + urllib.quote_plus('0') + "&thumb=" + urllib.quote_plus(thumb)
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = False)
	if next == True:
		listitem = xbmcgui.ListItem( label = settings.getLocalizedString( 30016 ) + ' (' + str( int(current[0]) + 1 ) + ')' , iconImage = next_thumb, thumbnailImage = next_thumb )
		u = sys.argv[0] + "?mode=4&name=" + urllib.quote_plus(studio) + "&url=" + urllib.quote_plus(saveurl)
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)	
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def clean(name):
	remove = [('&amp;','&'), ('&quot;','"'), ('&#039;','\''), ('\r\n',''), ('&apos;','\''), ('&#150;','-'), ('%3A',':'), ('%2F','/'), ('<link>',''), ('</link>','')]
	for trash, crap in remove:
		name = name.replace(trash,crap)
	return name
	
def clean_file(name):
    remove=[('\"',''),('\\',''),('/',''),(':',' - '),('|',''),('>',''),('<',''),('?',''),('*','')]
    for old, new in remove:
        name=name.replace(old,new)
    return name

def get_video(url, name, plot, studio, episode, thumb):
	result = common.fetchPage({"link": url})['content']
	video_id = re.compile('player\.loadRevision3Item\(\'video_id\',(.+?)\);').findall(result)[0].replace(' ','')
	api = common.fetchPage({"link": 'http://revision3.com/api/flash?video_id=' + video_id})['content']
	videos_api = common.parseDOM(api, "media", ret = "type")
	videos_api[:] = (value for value in videos_api if value != 'thumbnail')
	durl = {}
	for type_api in videos_api:
		content_api = clean(common.parseDOM(api, "media", attrs = { "type": type_api })[0])
		durl[type_api] = content_api
	list = ['MP4','Quicktime','Xvid','WMV']
	for type in list:
		content = common.parseDOM(result, "div", attrs = { "id": "action-panels-download-" + type })
		videos = common.parseDOM(content, "a", attrs = { "class": "sizename" })
		links = common.parseDOM(content, "a", attrs = { "class": "sizename" }, ret="href")
		count = 0
		for add in videos:
			code = type + ':' + add
			durl[code] = links[count]
			count += 1
	dictList = [] 
	for key, value in durl.iteritems():
		dictList.append(key)
	quality = settings.getSetting('type')
	try:
		try:
			purl = durl[quality]
		except:
			if quality == 'MP4:HD':
				if 'Quicktime:HD' in durl:
					quality_api = 'Quicktime:HD'
				else:
					quality_api = 'hd'
			if quality == 'MP4:Large':
				if 'Quicktime:Large' in durl:
					quality_api = 'Quicktime:Large'
				else:
					quality_api = 'high'
			if quality == 'MP4:Phone':
				quality_api = 'low'
			purl = durl[quality_api]
		ret = None
	except:
		dialog = xbmcgui.Dialog()
		ret = dialog.select(settings.getLocalizedString( 30017 ), dictList)
		purl = durl[dictList[ret]]
	if ret != -1:
		if settings.getSetting('download') == 'true':
			while not settings.getSetting('downloadPath'):
				dialog = xbmcgui.Dialog()
				ok = dialog.ok(plugin, settings.getLocalizedString( 30011 ))
				settings.openSettings()
			params = { "url": purl, "download_path": settings.getSetting('downloadPath'), "Title": name }
			downloader.download(clean_file(name) + '.' + purl.split('/')[-1].split('.')[-1], params)
		else:
			listitem = xbmcgui.ListItem(label = name , iconImage = 'DefaultVideo.png', thumbnailImage = thumb, path = purl)
			listitem.setInfo( type = "Video", infoLabels={ "Title": name, "Director": plugin, "Studio": studio, "Plot": plot, "Episode": int(episode)  } )
			xbmcplugin.setResolvedUrl( handle = int( sys.argv[1] ), succeeded = True, listitem = listitem )	

params = common.getParameters(sys.argv[2])
url = None
name = None
mode = None
plot = None
studio = None
episode = None
thumb = None

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass
try:
	plot = urllib.unquote_plus(params["plot"])
except:
	pass
try:
	studio = urllib.unquote_plus(params["studio"])
except:
	pass
try:
	episode = int(params["episode"])
except:
	pass
try:
	thumb = urllib.unquote_plus(params["thumb"])
except:
	pass

try:
	if mode == None:
		url = 'http://revision3.com/shows/'
		build_main_directory(url)
	elif mode == 1:
		build_sub_directory(url, name)
	elif mode == 2:
		get_video(url, name, plot, studio, episode, thumb)
	elif mode == 3:
		build_main_directory(url)
	elif mode == 4:
		build_search_directory(url)
except Exception:
	buggalo.onExceptionRaised()
