import requests
import json
from bs4 import BeautifulSoup

class GeniusAPI:

    # initalize data
    def __init__(self):
        self.__url = "https://api.genius.com/search?q="
        self.__url2 = "&access_token="
        self.__access_token = "api-key"
        self.__song_title = []
        self.__song_path = []
        self.__song_artist = []
        self.__results = ''
    # end def __init__
    
    # get top 10 results
    def find_song(self, info):
        # get information ex: song, lyric, or artist
        self.__search = info
        # make request to api
        self.__response = requests.get(self.__url + info + self.__url2 + self.__access_token)
        # read json
        self.__json_data = json.loads(self.__response.text)
        
        return len(self.__json_data['response']['hits']), " Are the top results"
    # end def find_song

    def top_results(self):
        # clear previous entries
        self.__song_title = []
        self.__song_artist = []
        for i in range(len(self.__json_data['response']['hits'])):
            self.__song_title.append(self.__json_data['response']['hits'][i]['result']['title'])
            self.__song_path.append(self.__json_data['response']['hits'][i]['result']['path'])
            self.__song_artist.append(self.__json_data['response']['hits'][i]['result']['primary_artist']['name'])
        return self.__song_title, self.__song_artist
    # end def top_results

    # return lyrics
    def song_lyrics(self, choice):
        # make request to genius.com with path to song
        self.__raw_html = requests.get('https://genius.com' + self.__song_path[choice])
        # parse html using BeautifulSoup
        self.__html = BeautifulSoup(self.__raw_html.text, 'html.parser')
        # get lyrics to song
        self.__lyrics = self.__html.find_all("p")[0].text
        
        return self.__lyrics
    # end def song_lyrics

    # return the song name and artist name
    def song_name_artist(self, choice):
        return self.__song_title[choice] + " by " + self.__song_artist[choice]
    
#end class GeniusAPI
