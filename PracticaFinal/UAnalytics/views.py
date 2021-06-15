from django.shortcuts import render
from .forms import *
import requests, datetime
import pandas as pd
import numpy as np
from UserManagement import models
from datetime import datetime
import re
# Mejoria de tiempos
import concurrent.futures # Import concurrencia
import time # Para calcular tiempos


# ----------------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------TWITCH-------------------------------------------------------------------#
# ----------------------------------------------------------------------------------------------------------------------------#

# Constantes de twitch
CLIENT_ID = '52upet9cwzgygo2y8iu68usifmzc6l'
CLIENT_SECRET = 'ks0w9aibyf78f2xglnvawlnnwzu01f'
REFRESH_TOKEN = '7nnvv8dtsdrmnwdsx2wbsluwk9saub4cve3uv42q18do1o9zra'

# FUNCIONES PRINCIPALES
# ----------------------------------------------------------#

def index(request):
    return render(request, 'main/index.html')


def index_t(request):
    Usuario = None
    usuarios = None
    videos = None
    channels = None
    channel_selected = None
    topgames = None
    total_follows = None
    followers_list = None
    Tok = None
    topclips = None
    dates_tabla = None
    views_tabla = None
    status = None
    status2 = None

    start = time.time()

   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Conseguimos access_token
        Tok = TwitchAuth()
        headers = {'client-id': CLIENT_ID,
                    'Authorization': 'Bearer ' + Tok.get('access_token')}

       
        get_gamesandclips = executor.submit(GamesClips, headers)
        if 'usuario' in request.POST:
            Usuario = request.POST['usuario']
            
            current_user = request.user
            if current_user != "AnonymousUser":
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                
                # Añadir a la base de datos
                instance = models.History(username = current_user, searchquery = Usuario, platform="Twitch", dateandtime = dt_string)
                instance.save()

            get_channels = executor.submit(Channel_Info, headers, Usuario)
            get_user = executor.submit(User_Info, headers, Usuario)

            channels, status = get_channels.result()
            for channel in channels:
                if channel['login'] == Usuario.lower():
                    channel_selected = channel

            usuarios, status = get_user.result()
            if usuarios:
                get_videos = executor.submit(Last_Videos, headers, usuarios['id'])
                get_follows = executor.submit(Followers_Info, headers, usuarios['id'])
                total_follows, followers_list = get_follows.result()
                videos, status = get_videos.result()

            if videos:
                views_tabla,dates_tabla = CreacionTablaVideos(videos)

        topgames,status, topclips, status2 = get_gamesandclips.result()

        end = time.time()
        print(end-start)

    newProductForm = NewTwitchForm()
    context = {'usuario': Usuario, 'new_product_form': newProductForm, 'usuarios': usuarios, 'videos': videos,
               'channel_selected': channel_selected, 'topgames': topgames, 'total_follows': total_follows,
                'followers_list': followers_list, 'topclips': topclips, 'dates_tabla': dates_tabla, 'views_tabla': views_tabla}
    return render(request, 'main/twitch.html', context)

# FUNCIONES GENERALES
# ----------------------------------------------------------#

def GamesClips(headers):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        get_games = executor.submit(Top_Games, headers)
        topgames,status = get_games.result()
        get_clips = executor.submit(Top_Clips, headers, topgames[0])
        topclips,status2 = get_clips.result()
    
    return topgames,status, topclips, status2

# CREACION DE TABLAS CON PANDAS PARA CREAR GRAFICAS 
# Y TRATAR DATOS
# ----------------------------------------------------------#

def ParsearTabla(tabla):
    views = []
    dates = []
    d = tabla[['views']].to_dict()
    dict = d['views']

    reqd_index = tabla.query('views >= 0').index.tolist()
    for dato in reqd_index:
        views.append(dict.get(dato))
        dates.append(str(dato[0]) + '-' + str(dato[1]))

    return views, dates

def CreacionTablaVideos(videos_list):
    datos = pd.DataFrame.from_dict(videos_list)

    datos['fecha_creacion'] = pd.to_datetime(datos['fecha_creacion'], format='%d-%m-%Y %H:%M')
    result = pd.DataFrame
    result = datos.groupby([datos['fecha_creacion'].dt.year, datos['fecha_creacion'].dt.month]).sum('views')
    result.index.names = ['Month','Year']

    return ParsearTabla(result)

# AUTENTICACIÓN
# ----------------------------------------------------------#

def TwitchAuth():
    BASE_URL = 'https://id.twitch.tv/oauth2/token'
    DATA = {"grant_type": "refresh_token", "refresh_token":REFRESH_TOKEN, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}

    resp = requests.post(url=BASE_URL, data=DATA)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

# INFORMACIÓN DE USUARIO
# ----------------------------------------------------------#

def User_Info(headers, usuario):
    url = "https://api.twitch.tv/helix/users?login=" + usuario

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return Parse_User_Info(resp.json()), resp.status_code
    else:
        return None, resp.status_code

def Parse_User_Info(resp):
    array = resp['data']

    if array:
        data = array[0]

        datetimeobject = datetime.strptime(data['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
        newformat = datetimeobject.strftime('%d-%m-%Y %H:%M')
        views = data['view_count']
        viewsformat = "{:,}".format(views)
        usuarios = {
            'id': data['id'],
            'nombre': data['display_name'],
            'broadcaster_type': data['broadcaster_type'],
            'imagen': data['profile_image_url'],
            'views': viewsformat ,
            'fecha_creacion': newformat
        }

        return usuarios

# INFORMACIÓN DE SEGUIDORES
# ----------------------------------------------------------#

def Followers_Info(headers, id_usuario):
    url = "https://api.twitch.tv/helix/users/follows?to_id={0}&first=100".format(id_usuario)

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return Parse_Followers_Info(resp.json())
    else:
        return None

def Parse_Followers_Info(resp):
    array = resp['data']
    followers_list = list()

    if array:
        data = array[0] # Datos del primer seguidor que sacamos para asignarlo en el nombre e id de total follows
        
        follows = resp['total']
        followsformat = "{:,}".format(follows)

        total_follows = {
            'id': data['to_id'],
            'nombre': data['to_name'],
            'total': followsformat
        }

        for follow in array:
            datetimeobject = datetime.strptime(follow['followed_at'],'%Y-%m-%dT%H:%M:%SZ')
            newformat = datetimeobject.strftime('%d-%m-%Y %H:%M')
            follower ={
                'id_seguidor': follow['from_id'],
                'nombre_seguidor': follow['from_name'],
                'followed_at': newformat
            }

            followers_list.append(follower)

        return total_follows, followers_list  # Devuelve el total de follows y una lista de todos los seguidores
    else:
        return None,None

# INFORMACIÓN DE CANAL
# ----------------------------------------------------------#
def Channel_Info(headers, usuario):
    url = "https://api.twitch.tv/helix/search/channels?query=" + usuario

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return Parse_Channel_Info(resp.json()), resp.status_code
    else:
        return None, resp.status_code


def Parse_Channel_Info(resp):
    lista = resp['data']
    channels=list()

    for channel in lista:
        if channel['started_at'] != '':
            datetimeobject = datetime.strptime(channel['started_at'],'%Y-%m-%dT%H:%M:%SZ')
            newformat = datetimeobject.strftime('%d-%m-%Y %H:%M')
        else:
            newformat = ''
            
        info = {
            'lan': channel['broadcaster_language'],
            'login': channel['broadcaster_login'],
            'display': channel['display_name'],
            'game_id': channel['game_id'],
            'game_name': channel['game_name'],
            'id': channel['id'],
            'is_live': channel['is_live'],     
            'imagen': channel['thumbnail_url'].replace('%{width}','440').replace('%{height}','250'),
            'title': channel['title'],         
            'started_at': newformat
        }
        
        channels.append(info)

    return channels


# ULTIMOS 5 VIDEOS
# ----------------------------------------------------------#

def Last_Videos(headers, id_usuario):
    url = "https://api.twitch.tv/helix/videos?user_id={0}&first=100".format(id_usuario)

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return Parse_Videos_Info(resp.json()), resp.status_code
    else:
        return None, resp.status_code

def Parse_Videos_Info(resp):
    lista = resp['data']
    videos=list()

    for video in lista:
        datetimeobject = datetime.strptime(video['created_at'],'%Y-%m-%dT%H:%M:%SZ')
        newformat = datetimeobject.strftime('%d-%m-%Y %H:%M')

        video_info = {
            'id': video['id'],
            'nombre': video['title'],
            'url': video['url'],
            'imagen': video['thumbnail_url'].replace('%{width}','440').replace('%{height}','250'),
            'views': video['view_count'] ,
            'language': video['language'],
            'duration': video['duration'],
            'fecha_creacion': newformat
        }
        
        videos.append(video_info)

    return videos

# JUEGOS MAS STREMEADOS
# ----------------------------------------------------------#

def Top_Clips(headers, top_game):
    url = "https://api.twitch.tv/helix/clips?game_id={0}".format(top_game['id'])

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return Parse_Clips_Info(resp.json()), resp.status_code
    else:
        return None, resp.status_code

def Parse_Clips_Info(resp):
    lista = resp['data']
    clips=list()

    for clip in lista:
        datetimeobject = datetime.strptime(clip['created_at'],'%Y-%m-%dT%H:%M:%SZ')
        newformat = datetimeobject.strftime('%d-%m-%Y %H:%M')

        clip_info = {
            'id': clip['id'],
            'author': clip['broadcaster_name'],
            'creador': clip['creator_name'],
            'title': clip['title'],
            'game_id': clip['game_id'],
            'url': clip['url'],
            'imagen': clip['thumbnail_url'],
            'language':['language'],
            'views': clip['view_count'],
            'duration': clip['duration'],
            'created_at': newformat
        }
        clips.append(clip_info)

    return clips


# JUEGOS MAS STREMEADOS
# ----------------------------------------------------------#

def Top_Games(headers):
    url = "https://api.twitch.tv/helix/games/top?first=10"

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return Parse_Games_Info(resp.json()), resp.status_code
    else:
        return None, resp.status_code

def Parse_Games_Info(resp):
    lista = resp['data']
    games=list()

    for game in lista:
        game_info = {
            'id': game['id'],
            'nombre': game['name'],
            'imagen': game['box_art_url'].replace('{width}','138').replace('{height}','190')
        }
        games.append(game_info)

    return games

# ----------------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------YOUTUBE-------------------------------------------------------------------#
# ----------------------------------------------------------------------------------------------------------------------------#

#Constantes de Youtube
YOUTUBE_KEY = 'AIzaSyCrLxTazgdR1b4Mg2OOfUMduLQqUpXbuqI'

# FUNCIONES PRINCIPALES
# ----------------------------------------------------------#

def index_youtube(request):
    Usuario = None
    usuarios = None
    videos = None
    views_tabla = None
    dates_tabla = None
    likes_tabla = None
    get_categories = None
    categories = None
    status = None
    
    start = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        get_categories = executor.submit(Categories_YT_Info)
        if 'usuario' in request.POST:
            Usuario = request.POST['usuario']
            get_channels = executor.submit(Channels_YT_Info, Usuario)        
            usuarios, status = get_channels.result()
            if usuarios:
                get_videos = executor.submit(Videos_YT_Info, usuarios['id']['channelId'])
                videos, status = get_videos.result()
                current_user = request.user
                if current_user != "AnonymousUser":
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")      
                    # Añadir a la base de datos
                    instance = models.History(username = current_user, searchquery = Usuario, platform="YouTube", dateandtime = dt_string)
                    instance.save()
                
            if videos:
                views_tabla, dates_tabla, likes_tabla = CreacionTablaVideos_YT(videos)

        categories, status = get_categories.result()
        
    #Calculamos el tiempo de ejecucion
    end = time.time()
    print(end-start)

    newProductForm = NewYTForm()
    context = {'usuarios': usuarios, 'usuario': Usuario, 'videos': videos, 'new_YT_form': newProductForm, 'dates_tabla': dates_tabla, 
               'views_tabla': views_tabla, 'likes_tabla': likes_tabla, 'categories' : categories}
    return render(request, 'main/youtube.html', context)

# FUNCIONES GENERALES
# ----------------------------------------------------------#

def CreacionTablaVideos_YT(videos_list):
    datos = pd.DataFrame.from_dict(videos_list)
    
    views = list(np.flip(datos.views.values))
    dates = list(np.flip(datos.fecha_creacion.values))
    likes = list(np.flip(datos.likes.values))

    return views, dates, likes

# INFORMACIÓN DE CANALES
# ----------------------------------------------------------#

def Channels_YT_Info(Usuario):
    search_url = 'https://www.googleapis.com/youtube/v3/search'

    params = {
        'part' : 'snippet',
        'type' : 'channel',
        'maxResults' : 1,
        'q' : Usuario,
        'key' : YOUTUBE_KEY
    }

    resp = requests.get(search_url, params=params)
    if resp.status_code == 200:
        return Parse_YT_Channels_Info(resp.json()), resp.status_code
    else:
        return None, resp.status_code

def Parse_YT_Channels_Info(resp):
    array = resp['items']

    if array:
        data = array[0]

        datetimeobject = datetime.strptime(data['snippet']['publishedAt'],'%Y-%m-%dT%H:%M:%SZ')
        newformat = datetimeobject.strftime('%d-%m-%Y %H:%M')
        usuarios = {
            'id': data['id'],
            'nombre': data['snippet']['title'],
            'description': data['snippet']['description'],
            'imagen': data['snippet']['thumbnails']['default']['url'],
            'fecha_creacion': newformat
        }
        
        return More_channels_YT_Info(usuarios)
    
def More_channels_YT_Info(Usuario):
    search_url = 'https://www.googleapis.com/youtube/v3/channels'

    params = {
        'part' : 'statistics',
        'id' : Usuario['id']['channelId'],
        'key' : YOUTUBE_KEY
    }

    resp = requests.get(search_url, params=params)
    
    if resp.status_code == 200:
        return Add_more_Channel_Information(resp.json(), Usuario)
    else:
        return None
    
def Add_more_Channel_Information(resp, usuarios):
    array = resp['items']
    
    if array:
        data = array[0]
        views = int(data['statistics']['viewCount'])
        if data['statistics']['hiddenSubscriberCount'] == False:
            follows = int(data['statistics']['subscriberCount'])
            followsformat = "{:,}".format(follows)
            usuarios['follows'] = followsformat
        else:
            usuarios['follows'] = 0

        viewsformat = "{:,}".format(views)
        usuarios['views'] = viewsformat  
        usuarios['videos'] = data['statistics']['videoCount']

        return usuarios 
    
# VIDEOS DE CANALES
# ----------------------------------------------------------#    

def Videos_YT_Info(userId):
    search_url = 'https://www.googleapis.com/youtube/v3/search'

    params = {
        'part' : 'snippet',
        'channelId' : userId,
        'maxResults' : 10,
        'order' : 'date',
        'key' : YOUTUBE_KEY
    }

    resp = requests.get(search_url, params=params)
    
    if resp.status_code == 200:
        return Parse_YT_Videos_Info(resp.json()), resp.status_code
    else:
        return None, resp.status_code
    
def Parse_YT_Videos_Info(resp):
    lista = resp['items']
    videos=list()
    
    for video in lista:
        datetimeobject = datetime.strptime(video['snippet']['publishTime'],'%Y-%m-%dT%H:%M:%SZ')
        newformat = datetimeobject.strftime('%d-%m-%Y %H:%M')

        if video['id']['kind'] == 'youtube#video':
            video_info = {
                'id': video['id']['videoId'],
                'tipo' : video['id']['kind'],
                'nombre': video['snippet']['title'],
                'url': "https://www.youtube.com/watch?v=" + video['id']['videoId'],
                'url_emb' : "https://www.youtube.com/embed/" + video['id']['videoId'],
                'imagen': video['snippet']['thumbnails']['default']['url'],
                'fecha_creacion': newformat
            }
        elif video['id']['kind'] == 'youtube#playlist':
            video_info = {
                'id': video['id']['playlistId'],
                'tipo' : video['id']['kind'],
                'nombre': video['snippet']['title'],
                'url': "https://www.youtube.com/watch?v=" + video['id']['playlistId'],
                'imagen': video['snippet']['thumbnails']['default']['url'],
                'fecha_creacion': newformat
            }
        else:
            return None
        
        videos.append(video_info)

    
    return More_videos_YT_Info(videos)

def More_videos_YT_Info(videos):
    get_info = None
    for video in videos:
        search_url = 'https://www.googleapis.com/youtube/v3/videos'

        params = {
            'part' : 'statistics',
            'id' : video['id'],
            'key' : YOUTUBE_KEY
        }

        resp = requests.get(search_url, params=params)
        
        if resp.status_code == 200:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                get_info = executor.submit(Add_more_Videos_Information, resp.json(), videos)        
        else:
            return None
    if get_info:
        get_info.result()
    return videos
    

def Add_more_Videos_Information(resp, videos):
    array = resp['items']

    for video in videos:
        data = array[0]
      
        if data['id'] == video['id']:

            dislikes = int(data['statistics']['dislikeCount'])
            dislikesformat = "{:,}".format(dislikes)
            video['views'] = int(data['statistics']['viewCount'])
            video['likes'] = int(data['statistics']['likeCount'])
            video['dislikes'] = dislikesformat
            try:
                comments = int(data['statistics']['commentCount'])
                commentsformat = "{:,}".format(comments)
                video['comments'] = commentsformat
            except:
                video['comments'] = 0

            
           
            
# CATEGORIAS GENERALES
# ----------------------------------------------------------# 
def Categories_YT_Info():
    search_url = 'https://www.googleapis.com/youtube/v3/videoCategories'

    params = {
        'part' : 'snippet',
        'regionCode' : 'es',
        'key' : YOUTUBE_KEY
    }

    resp = requests.get(search_url, params=params)

    if resp.status_code == 200:
        return Parse_YT_Categories(resp.json()), resp.status_code
    else:
        return None, resp.status_code

def Parse_YT_Categories(resp):
    array = resp['items']
    categories = list()

    for category in array:
        
        category_info = {
                'Channel_id': category['snippet']['channelId'],
                'title': category['snippet']['title']
            }
        
        categories.append(category_info)
    
        
    return categories

# ----------------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------TWITTER-------------------------------------------------------------------#
# ----------------------------------------------------------------------------------------------------------------------------#

#Información de Twitter
TWITTER_KEY = 'mBW6zMxto9RkKBPSSyCLJr1jG'
TWITTER_SECRET_KEY = 'hVmffSIyxtqskpSK03ckMYtDIbw8m6USwPh0XAFVOXBkyRB4o2'
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAPpNQgEAAAAAPv85kMRcVo7cQMRa0OF6gnJcs2E%3D3I1gMkVldvEnB3jx2P2TmwyIXixV2EJmYMpEL5khRbVGoTUGOI'
TWITTER_ACCESS_TOKEN = '1403369623194673156-qHCrJqMLsZQqGtG5raWpknORC8jkt8'
TWITTER_ACCESS_SECRET = 'pL72p1EdGUf2dAn4IgODQKUBNwAjpxXucB3HM8fhBBfs5'


# FUNCIONES PRINCIPALES
# ----------------------------------------------------------#
def index_twitter(request):
    Usuario = None
    get_accounts = None
    get_tweets = None
    usuarios = None
    tweets = None
    tweets_tabla = None
    dates_tabla = None
    replies_tabla = None
    likes_tabla = None
    totalr = None
    totall = None
    status = None

    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        headers = {'Authorization': 'Bearer ' + TWITTER_BEARER_TOKEN}

        if 'usuario' in request.POST:
            Usuario = request.POST['usuario']
            get_accounts = executor.submit(Accounts_TW_Info, headers, Usuario)
            usuarios, status= get_accounts.result()

            if usuarios:
                get_tweets = executor.submit(Get_Tweets, headers, usuarios['id'])
                tweets , status = get_tweets.result()
                current_user = request.user
                
                if current_user != "AnonymousUser":
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")      
                    # Añadir a la base de datos
                    instance = models.History(username = current_user, searchquery = Usuario, platform="Twitter", dateandtime = dt_string)
                    instance.save()

                if tweets:
                    tweets_tabla, dates_tabla, likes_tabla, replies_tabla = CreacionTablaTweets(tweets)
                    totalr, totall = TotalRTsYFavs(tweets_tabla, likes_tabla)
                
    end = time.time()
    print(end-start)

    newproductForm = NewTwitterForm()
    context = {'usuarios' : usuarios ,'usuario': Usuario,'twitter_form': newproductForm, 'tweets' : tweets, 'tweets_tabla': tweets_tabla, 'dates_tabla': dates_tabla,
     'likes_tabla': likes_tabla, 'replies_tabla': replies_tabla, 'totalr' : totalr, 'totall' : totall }
    return render(request, 'main/twitter.html', context)


# FUNCIONES GENERALES
# ----------------------------------------------------------#
def ParsearTablaTweets(tabla):
    retweets = []
    dates = []
    likes = []
    replies = []
    d = tabla[['retweets']].to_dict()
    d2 = tabla[['likes']].to_dict()
    d3 = tabla[['replies']].to_dict()
    dict = d['retweets']
    dict2 = d2['likes']
    dict3 = d3['replies']
    
    reqd_index = tabla.query('retweets >= 0').index.tolist()
    for dato in reqd_index:
        retweets.append(dict.get(dato))
        likes.append(dict2.get(dato))
        replies.append(dict3.get(dato))
        dates.append(str(dato[0]) + '-' + str(dato[1]) + '-' + str(dato[2]))

    return retweets, dates, likes, replies

def TotalRTsYFavs(retweets,likes):
    #No necesario testearla, muy simple
    totalr = 0
    totall = 0
    
    for r in retweets:
        totalr += r
    for l in likes:
        totall += l
        
    return totalr, totall

def CreacionTablaTweets(tweets_list):
    data = pd.DataFrame.from_dict(tweets_list)

    data['fecha_creacion'] = pd.to_datetime(data['fecha_creacion'], format='%d-%m-%Y %H:%M')
    res = pd.DataFrame
    res = data.groupby([data['fecha_creacion'].dt.year, data['fecha_creacion'].dt.month, data['fecha_creacion'].dt.day]).sum('retweets')
    res.index.names = ['Year','Month','Day']

    return ParsearTablaTweets(res)

def Find(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)     
     
    return [x[0] for x in url]
      
# INFORMACIÓN DE CUENTAS
# ----------------------------------------------------------#
def Accounts_TW_Info(headers, usuario):
    parameters = "?user.fields=public_metrics,created_at,profile_image_url,verified"
    search_url = "https://api.twitter.com/2/users/by/username/" + usuario + parameters
    resp = requests.get(search_url, headers=headers) 

    if resp.status_code == 200:
        return Parse_Accounts_TW_Info(resp.json()), resp.json()
    else:
        return None, resp

def Parse_Accounts_TW_Info(resp):
    try:
        array = resp['data']
        if array:
        
            datetimeobject = datetime.strptime(array['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
            usuario = {
                'id': array['id'],
                'nombre': array['name'],
                'login': array['username'],
                'fecha_creacion': datetimeobject,
                'followers': array['public_metrics']['followers_count'],
                'logo': array['profile_image_url'],
                'verified': array['verified']
            }

        return usuario
    except:
        return None


# TWEETS
# ----------------------------------------------------------#

def Get_Tweets(headers, usuario):
    parameters = "/tweets?tweet.fields=created_at,public_metrics&expansions=author_id&user.fields=created_at&max_results=100&exclude=retweets"
    search_url = "https://api.twitter.com/2/users/" + usuario + parameters

    resp = requests.get(search_url, headers=headers)
    if resp.status_code == 200:
        return Parse_Get_Tweets(resp.json()), resp.json()
    else:
        None


def Parse_Get_Tweets(resp):
    try:
        if resp['meta']['result_count'] != 0:
            array = resp['data']
   
            tweets_list = list()

            for tweet in array:
                datetimeobject = datetime.strptime(tweet['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
                tweets = {
                    'id_usuario': tweet['author_id'],
                    'fecha_creacion': datetimeobject,
                    'id_tweet': tweet['id'],
                    'text': tweet['text'],
                    'retweets': tweet['public_metrics']['retweet_count'],
                    'replies': tweet['public_metrics']['reply_count'],
                    'likes': tweet['public_metrics']['like_count'],
                    'url' : Find(tweet['text'])
                }

                tweets_list.append(tweets)
    
            return tweets_list
        else:
            return None
    except:
        return None
