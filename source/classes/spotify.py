import spotipy, json, pathlib
import spotipy.util as util

"""user-read-playback-state user-modify-playback-state user-top-read\
                 user-read-currently-playing"""


class SpotifyClient():

    CLIENT_ID='your_client_id'
    CLIENT_SECRET='your_client_secret'
    REDIRECT_URI='http://127.0.0.1:5000/spotify_callback/'
    REQUEST_SCOPE=('user-read-playback-state'
                   ' '
                   'user-modify-playback-state'
                   ' '
                   'user-top-read'
                   ' '
                   'user-read-currently-playing')
    username=''
    oauth=None
    client=None
    code=''
    __url=''

    def __init__(self, username):
        self.username = username
        #self.code = code
        #if self.__search_token():
        #    print("Exists")
        #else:
        #    print("Doesn't exist")
        #    return None

        self.oauth = spotipy.oauth2.SpotifyOAuth(client_id=self.CLIENT_ID,
                                                  client_secret=self.CLIENT_SECRET,
                                                  redirect_uri=self.REDIRECT_URI,
                                                  scope=self.REQUEST_SCOPE,
                                                  username=self.username)
        self.client = spotipy.client.Spotify(requests_session=True,
                                        oauth_manager=self.oauth,
                                        requests_timeout=5,
                                        retries=2)

        print("Initiated the Spotify Object")


    def __search_token(self):
        file = pathlib.Path(f".cache-{self.username}")
        return file.is_file()

    def get_url(self):
        self.__url = self.oauth.get_authorize_url()
        return self.__url

    def set_token(self, code):
        result = self.oauth.get_access_token(code=code)
        print("Succesfully set Token")
        #print(result)

    def get_current_track(self):
        results = self.client.current_user_playing_track()

        if results == None:
            return 0

        try:
            artist_name = results['item']['artists'][0]['name']
            track_name = results['item']['name']
            img_url = results['item']['album']['images'][0]['url']

            current_track_infoDICT = {'artist' : artist_name,
                                      'track': track_name,
                                      'img': img_url}

            current_track_infoJSON = json.dumps(current_track_infoDICT)

        except TypeError:
            print('Type Error Occured')
            current_track_infoDICT = {'artist' : 'Unknown',
                                      'track': 'Unknown',
                                      'img': 'https://cdn1.iconfinder.com/data/icons/rounded-flat-country-flag-collection-1/2000/_Unknown.png'}

            current_track_infoJSON = json.dumps(current_track_infoDICT)
            return current_track_infoJSON

        return current_track_infoJSON

    def next_track(self):
        try:
            self.client.next_track(device_id=None)
        except Exception as e:
            print("Ooops", e.__class__, " occured!")

    def pause_track(self):
        try:
            self.client.pause_playback(device_id=None)
        except Exception as e:
            print("Ooops", e.__class__, " occured!")

    def previous_track(self):
        try:
            self.client.previous_track(device_id=None)
        except Exception as e:
            print("Ooops", e.__class__, " occured!")

    def resume_track(self):
        try:
            self.client.start_playback(device_id=None)
        except Exception as e:
            print("Ooops", e.__class__, " occured!")

    def play_track(self, song, artist):
        try:
            result = None

            if artist != None:
                print(artist)
                result = self.client.search(q=artist+'%'+song,  type="track")
                track = [result['tracks']['items'][0]['external_urls']['spotify']]

                self.client.start_playback(uris=track)

            pass


        except Exception as e:
            print("OOops", e.__class__, " occured!")
