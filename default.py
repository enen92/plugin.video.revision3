
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, xbmcaddon

__plugin__ =  'Revision3'
__author__ = 'stacked <stacked.xbmc@gmail.com>'
__url__ = 'http://code.google.com/p/plugin/'
__date__ = '07-12-2010'
__version__ = '1.0.0'
__settings__ = xbmcaddon.Addon(id='plugin.video.revision3')

def open_url(url):
	req = urllib2.Request(url)
	content = urllib2.urlopen(req)
	data = content.read()
	content.close()
	return data

def check_for_updates():
	print __plugin__+' v'+__version__
	url = 'http://code.google.com/feeds/p/plugin/downloads/basic'
	data = open_url(url)
	match = re.compile('detail\?name=plugin.video.revision3-(.+?)\.zip').findall(data)
	for newversion in match :
		if newversion.find(__version__) != 0:
			dia = xbmcgui.Dialog()
			ok = dia.ok(__plugin__, __settings__.getLocalizedString(30012) + ' tinyurl.com/addonupdates\n' + __settings__.getLocalizedString(30013) + __version__ + '  -  ' + __settings__.getLocalizedString(30014) + newversion)

def build_main_directory():
	quality = __settings__.getLocalizedString(30000 + 5 + int(__settings__.getSetting('quality')))
	url = 'http://revision3.com/shows/'
	data = open_url(url)
	match = re.compile('<ul id="shows">(.+?)<div id="footer" class="clear">', re.DOTALL).findall(data)
	url_name = re.compile('<h3><a href="(.+?)">(.+?)</a></h3>').findall(match[0])
	image = re.compile('class="thumbnail"><img src="(.+?)" /></a>').findall(match[0])
	count = 0
	for url, name in url_name:
		url = 'http://revision3.com' + url + '/feed/' + quality
		listitem = xbmcgui.ListItem(label = name, iconImage = image[count], thumbnailImage = image[count])
		u = sys.argv[0] + "?mode=1&name=" + urllib.quote_plus(name) + "&url=" + urllib.quote_plus(url)
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)
		count += 1

def build_sub_directory(url, name):
	genre = name
	data = open_url(url)
	plot = re.compile('<content:encoded>\n(.+?)\n      </content:encoded>', re.DOTALL).findall(data)
	number = re.compile('<guid isPermaLink="false">(.+?)</guid>').findall(data)
	match = re.compile('<item>(.+?)<title>(.+?) - ', re.DOTALL).findall(data)
	link = re.compile('<enclosure url="(.+?)"').findall(data)
	image = re.compile('</media:description>\n        (<media:thumbnail url="(.+?)" width="100" height="100" />\n        )?<media:player url', re.DOTALL).findall(data)
	count = 0
	if len(match) == 0:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__plugin__, __settings__.getLocalizedString(30021) + '\n' + __settings__.getLocalizedString(30000 + 5 + int(__settings__.getSetting('quality'))) + __settings__.getLocalizedString(30022)) 
	for title in match:
		episode = int(number[count].rsplit('/', 2)[1].lstrip('0'))
		url = link[count]
		listitem = xbmcgui.ListItem(label = clean(match[count][1]), iconImage = image[count][1], thumbnailImage = image[count][1])
		listitem.setInfo( type = "Video", infoLabels = { "Title": clean(match[count][1]), "Director": __plugin__, "Studio": __plugin__, "Genre": genre, "Plot": clean(plot[count]), "Episode": episode } )
		u = sys.argv[0] + "?mode=2&name=" + urllib.quote_plus(clean(match[count][1])) + "&url=" + urllib.quote_plus(url) + "&plot=" + urllib.quote_plus(clean(plot[count])) + "&genre=" + urllib.quote_plus(genre) + "&episode=" + urllib.quote_plus(str(episode))
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = False)
		count += 1
	xbmcplugin.addSortMethod( handle = int(sys.argv[ 1 ]), sortMethod = xbmcplugin.SORT_METHOD_NONE )

def clean(name):
	remove = [('&amp;','&'), ('&quot;','"'), ('&#039;','\''), ('\r\n',''), ('&apos;','\'')]
	for trash, crap in remove:
		name = name.replace(trash,crap)
	return name
			
def play_video(url, name, plot, genre, episode):
	filename = genre + ' Episode ' + str(episode) + '.' + url.replace('/tzdaily','').rsplit('/')[10].split('.')[2]
	def Download(url, dest):
		dialog = xbmcgui.DialogProgress()
		dialog.create(__settings__.getLocalizedString(30015), name, __settings__.getLocalizedString(30016) + filename)
		urllib.urlretrieve(url, dest, lambda nb, bs, fs, url = url: _pbhook(nb, bs, fs, url, dialog))
	def _pbhook(numblocks, blocksize, filesize, url = None,dialog = None):
		try:
			percent = min((numblocks * blocksize * 100) / filesize, 100)
			dialog.update(percent)
		except:
			percent = 100
			dialog.update(percent)
		if dialog.iscanceled():
			dialog.close()
	filepath = None
	stream = 'false'
	if (__settings__.getSetting('download') == 'true'):
			filepath = xbmc.translatePath(os.path.join(__settings__.getSetting('download_path'), filename))
			Download(url, filepath)
	elif (__settings__.getSetting('download') == 'false' and __settings__.getSetting('download_ask') == 'true'):
		dialog = xbmcgui.Dialog()
		choice = dialog.select(__plugin__, [__settings__.getLocalizedString(30017), __settings__.getLocalizedString(30018), __settings__.getLocalizedString(30019)])
		if (choice == 0):
			filepath = xbmc.translatePath(os.path.join(__settings__.getSetting('download_path'), filename))
			Download(url, filepath)
		elif (choice == 1):
			stream = 'true'
		else:
			pass
	elif (__settings__.getSetting('download') == 'false' and __settings__.getSetting('download_ask') == 'false'):
		stream = 'true'
	if __settings__.getSetting('dvdplayer') == 'true':
		player_type = xbmc.PLAYER_CORE_DVDPLAYER
	else:
		player_type = xbmc.PLAYER_CORE_MPLAYER
	image = xbmc.getInfoImage( 'ListItem.Thumb' )
	listitem = xbmcgui.ListItem(label = name , iconImage = 'DefaultVideo.png', thumbnailImage = image)
	listitem.setInfo( type = "Video", infoLabels={ "Title": name, "Director": __plugin__, "Studio": __plugin__, "Genre": genre, "Plot": plot, "Episode": int(episode)  } )
	if (filepath != None and os.path.isfile(filepath)):
		xbmc.Player(player_type).play(str(filepath), listitem)
	elif (stream == 'true'):
		xbmc.Player(player_type).play(str(url), listitem)
	xbmc.sleep(200)

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

params = get_params()
url = None
name = None
mode = None
page = 1
plot = None
genre = None
episode = None

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
	page = int(params["page"])
except:
	pass
try:
	plot = urllib.unquote_plus(params["plot"])
except:
	pass
try:
	genre = urllib.unquote_plus(params["genre"])
except:
	pass
try:
	episode = int(params["episode"])
except:
	pass

if mode == None:
	#if __settings__.getSetting('update') == 'true':
	#	check_for_updates()
	build_main_directory()
elif mode == 1:
	build_sub_directory(url, name)
elif mode == 2:
	play_video(url, name, plot, genre, episode)

xbmcplugin.addSortMethod( handle = int(sys.argv[ 1 ]), sortMethod = xbmcplugin.SORT_METHOD_NONE )
xbmcplugin.endOfDirectory(int(sys.argv[1]))
