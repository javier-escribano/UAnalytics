import unittest
from UAnalytics.views import *
from django.test import TestCase

TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAPpNQgEAAAAAPv85kMRcVo7cQMRa0OF6gnJcs2E%3D3I1gMkVldvEnB3jx2P2TmwyIXixV2EJmYMpEL5khRbVGoTUGOI'
YOUTUBE_KEY = 'AIzaSyCrLxTazgdR1b4Mg2OOfUMduLQqUpXbuqI'
CLIENT_ID = '52upet9cwzgygo2y8iu68usifmzc6l'

#En los endpoints comprobamos el status code, a no ser que estemos testeando
#Una función que dependa de otra que ya fue llamada con satisfacción previamente

class TestViews(TestCase):

    def setUp(self):
        self.headerstw = {'Authorization': 'Bearer ' + TWITTER_BEARER_TOKEN}
        self.usuariotwitch = 'thegrefg'
        Tok = TwitchAuth()
        self.headerstwitch = {'client-id': CLIENT_ID,
                    'Authorization': 'Bearer ' + Tok.get('access_token')}
#----------------------------TWITTER------------------------#
     
    def test_get_tweets_user_not_found(self):
        tweets, status = Get_Tweets(self.headerstw, '000000000')
        self.assertEquals(status['errors'][0]['title'], 'Not Found Error')
        
    def test_get_tweets(self):
        tweets, status = Get_Tweets(self.headerstw, '398306220')
        self.assertEquals(tweets[0]['id_usuario'], '398306220')

    def test_get_twitter_info_failed(self):
        info, status = Accounts_TW_Info(self.headerstw, 'salkhguslgdudsbviuabgurñbarwg')
        self.assertEquals(status.status_code, 404)
        
    def test_get_twitter_info(self):
        info, status = Accounts_TW_Info(self.headerstw, 'rubiu5')
        self.assertEquals(info['id'], '398306220')
        self.assertEquals(info['login'], 'Rubiu5')
        self.assertEquals(info['verified'], True)

    def test_find(self):
        string = "Hola esto es una prueba https://udc.es"
        resultado = Find(string)
        self.assertEquals(resultado, ['https://udc.es'])

#----------------------------YOUTUBE---------------------------------̣---#
    def test_channels_info(self):
        #Por channelId, que es único para cada usuario.
        #Siempre por elementos que no cambien
        usuario = "elrubius"
        channels, status = Channels_YT_Info(usuario)
        self.assertEquals(channels['id']['channelId'], 'UCXazgXDIYyWH-yXLAkcrFxw')
        self.assertEquals(channels['nombre'], 'elrubiusOMG')
        self.assertEquals(status, 200)
       
    def test_more_channels_info(self):
        #Comprobamos el channel ID para ver si es el mismo que el que pedimos
        usuario = "elrubius"
        data,status = Channels_YT_Info(usuario)
        info= More_channels_YT_Info(data)
        self.assertEquals(info['id']['channelId'], 'UCXazgXDIYyWH-yXLAkcrFxw')

    def test_videos_yt_info(self):
        #Comprobar que devuelve 10 vídeos que es lo que le pedimos a la API
        userid= 'UCXazgXDIYyWH-yXLAkcrFxw'
        info, status = Videos_YT_Info(userid)
        numbervideos = len(info)
        self.assertEquals(numbervideos, 10)

    def test_videos_yt_info_failed(self):
        #Comprobamos si el usuario no tiene videos
        userid= 'UCXsadasdasdasdazgXDIYyWH-yXLAkcrFxw'
        info, status = Videos_YT_Info(userid)   
        listavacia = len(info)                          
        self.assertEquals(listavacia, 0)
    
    def test_categories_yt(self):
        #Es una lista. Que saque el titulo y el ID del canal de la última categoria
        #que devuelve la API
        categories, status = Categories_YT_Info()
        self.assertEquals(status, 200)
        self.assertEquals(categories[0]['Channel_id'] , 'UCBR8-60-B28hp2BmDPdntcQ')
        self.assertEquals(categories[0]['title'] , 'Film & Animation')


#----------------------------TWITCH---------------------------------̣---#

    def test_games_clip(self):
        #El Contenido es dinámico. TopGames y TopClips cambian.
        topgames,status, topclips, status2 = GamesClips(self.headerstwitch)
        listavaciagames = len(topgames)
        listavaciaclips = len(topclips)
        self.assertEquals(status, 200)
        self.assertEquals(status2, 200)
        self.assertNotEquals(listavaciagames, 0)
        self.assertNotEquals(listavaciaclips, 0)

    def test_user_info(self):
        info, status = User_Info(self.headerstwitch, self.usuariotwitch)
        self.assertEquals(status, 200)
        self.assertEquals(info['id'], '48878319')
        self.assertEquals(info['nombre'], 'TheGrefg')
        self.assertEquals(info['fecha_creacion'], '12-09-2013 00:45')

    def test_user_info_failed(self):
        #Falla
        info, status = User_Info(self.headerstwitch, 'asdasdasdasdasdasdasdasdasd')
        self.assertIsNone(info)

    def test_followers_info(self):
        #Comprobamos que tiene seguidores
        #Comprobamos que el ID es el correcto
        infototal, followerslist = Followers_Info(self.headerstwitch, '48878319')
        listanovacia = len(followerslist)
        self.assertEquals(infototal['id'], '48878319')
        self.assertNotEquals(listanovacia, 0)
    
    def test_channel_info_twitch(self):
        info, status = Channel_Info(self.headerstwitch, self.usuariotwitch)
        self.assertEquals(status, 200)
        usuario = info[0]
        self.assertEquals(usuario['lan'],'es')
        self.assertEquals(usuario['login'],'thegrefg')
        self.assertEquals(usuario['display'],'TheGrefg')
    
    def test_last_videos(self):
        #Sabemos que este usuario tiene 100 videos o menos. Sacamos los últimos
        lastvideos, status = Last_Videos(self.headerstwitch, '48878319')
        tamanolista = len(lastvideos)
        self.assertEquals(status, 200)
        self.assertLessEqual(tamanolista, 100)
