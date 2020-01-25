# NOTE: to install nltk
#       command line: pip3 install nltk
#       in idle shell: import nltk, press enter
#       in idle shell: nltk.download(), press enter
#       a graphical interface will show, click all and click download

from nltk.corpus import stopwords #common words
from nltk.cluster.util import cosine_distance  # return cosine between vectors
import numpy as np # scientific computing
import networkx as nx  # study of complex networks
import re # regular expression
import io

# pip3 install dash==0.42.0
# pip3 install dash-daq==0.1.0
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import genius_api_class

# global variables for lyrics, songs names, and artist names
# two of the same for comparing 
genius = genius_api_class.GeniusAPI()
song_titles = []
song_artist = []
song_choice = 10
wordX = []
countY = []
songNameArtist = ""
        
genius2 = genius_api_class.GeniusAPI()
song_titles2 = []
song_artist2 = []
song_choice2 = 10
wordX2 = []
countY2 = []
songNameArtist2= ""

# NOTE: Need to use command line, not idle
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def main():
    dash_plot()
    app.run_server()
# end def main
    
def dash_plot():
    # text that is going to overwritten
    markdown_text = '''
    # MADE MAIN FUNCTION
    ### Dash and Markdown
    
    Dash apps can be written in Markdown.
    Dash uses the [CommonMark](http://commonmark.org/)
    specification of Markdown.
    Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
    if this is your first introduction to Markdown!
    '''

    app.layout = html.Div([
        # first song
        # make input
        dcc.Input(id='input-1-submit', type='text', value='', placeholder="Enter Song or Artist"),

        # make drpdown
        dcc.Dropdown(
            id="dropdown1",
            options=[
                    {'label': 'Doomsday', 'value': 0},
                    {'label': 'Beef Rap', 'value': 1}
                ],
            placeholder="Select a Song"
        ),
        html.P(" "),

        # secong song
        dcc.Input(id='input-2-submit', type='text', value='', placeholder="Enter Song or Artist"),
        # make drpdown
        dcc.Dropdown(
            id="dropdown2",
            options=[
                    {'label': 'Doomsday', 'value': 0},
                    {'label': 'Beef Rap', 'value': 1}
                ],
            placeholder="Select a Song"
        ),

        html.P(""),
        # make graph
        dcc.Graph(id='example-graph'),

        # make h2 text
        html.H2(children='Summarization'),

        # make markdown
        dcc.Markdown(id='markdown1', children=markdown_text),

        # make space at the bottom of the screen
        html.P(" "),
        html.P(" "),

        dcc.Markdown(id='markdown2', children=markdown_text)
    ])

    # First callback for input to update dropdown
    @app.callback(Output('dropdown1', 'options'),
                  [Input('input-1-submit', 'n_submit'), Input('input-1-submit', 'n_blur')],
                  [State('input-1-submit', 'value')])
    
    # update dropdown with new labels and values
    def update_dropdown(ns1, nb1, input1):
    
        # empty array
        songs = []
        song_titles = []
        song_artist = []

        # find songs
        genius.find_song(input1)
        
        # get top songs and artist
        song_titles, song_artist = genius.top_results()
        # loop through all songs titles and artist and combine them
        for i in range(len(song_titles)):
            songs.append((song_titles[i] + ' by ' + song_artist[i]))

        # return results    
        return [{'label': songs[i], 'value': i} for i in range(len(songs))]
    # end def update_dropdown

    # second song
    # First callback for input to update dropdown
    @app.callback(Output('dropdown2', 'options'),
                  [Input('input-2-submit', 'n_submit'), Input('input-2-submit', 'n_blur')],
                  [State('input-2-submit', 'value')])
    
    # update dropdown with new labels and values
    def update_dropdown2(ns1, nb1, input1):
    
        # empty array
        songs = []
        song_titles2 = []
        song_artist2 = []

        # find songs
        genius2.find_song(input1)
        
        # get top songs and artist
        song_titles2, song_artist2 = genius2.top_results()

        # loop through all songs titles and artist and combine them
        for i in range(len(song_titles2)):
            songs.append((song_titles2[i] + ' by ' + song_artist2[i]))

        #print(songs)
        # return results    
        return [{'label': songs[i], 'value': i} for i in range(len(songs))]
    #end def update_dropdown2

    # second callback for dropdown to update chart
    @app.callback(
        Output('example-graph', 'figure'),
        [dash.dependencies.Input('dropdown1', 'value'),
         Input('dropdown2', 'value')]
    )

    # update graph with words and word count from dropdown
    def update_figure(input1, input2):
        # NOTE: returns index 0-9
        # clear variables
        countY = []
        wordX = []
        songNameArtist = ""
        countY2 = []
        wordX2 = []
        songNameArtist2 = ""
        
        # input is not empty
        if input1 is not None:
            # get most common words from song
            countY, wordX = mostCommonWords(genius.song_lyrics(input1))
            # get song name and artist
            songNameArtist = genius.song_name_artist(input1)
        # input is not empty
        if input2 is not None:
            # get most common words from song
            countY2, wordX2 = mostCommonWords(genius2.song_lyrics(input2))
            wordX2 = wordX
            countY2 = matchLists(wordX, wordX2, countY2)
            # get song name and artist
            songNameArtist2 = genius2.song_name_artist(input2)
        # plot words, word count, and legend to a graph
        return {
            'data': [go.Scatter(
                {'marker': {'size': 300}},
                x = wordX,
                y = countY,
                name = songNameArtist
                
            ),go.Scatter(
                {'marker': {'size': 300}},
                x = wordX2,
                y = countY2,
                name = songNameArtist2
            )],
            'layout': go.Layout(
                xaxis={
                    'title': "Words"
                    },
                yaxis={
                    'title': "Word Count"
                    },
                title = "Compare Songs", 
                hovermode = 'closest'
            )
        }
    # end def update_figure

    # third callback for dropdown to update text
    @app.callback(
        Output('markdown1', 'children'),
        [dash.dependencies.Input('dropdown1', 'value')]
    )

    # update text with text summarization for first song
    def update_text(input1):
        #print(input1)
        summary = ""
        if input1 is not None:
            summary = generate_summary( genius.song_lyrics(input1), 10)
        return u' '.join(summary)
    #end def update_text

    # Second Song
    # third callback for dropdown to update text
    @app.callback(
        Output('markdown2', 'children'),
        [dash.dependencies.Input('dropdown2', 'value')]
    )

    # update text with text summarization for second song
    def update_text(input1):
        #print(input1)
        summary = ""
        if input1 is not None:
            summary = generate_summary( genius2.song_lyrics(input1), 10)
        return u' '.join(summary)
    #end def update_text
# end dash_plot

def matchLists(list1word, list2word, list2count):
    newlist2 = []
    newtemp = []
    
    # loop 35 times
    for i in range(35):
        temp = 0
        try:
            # get index of word
            temp = list2word.index(list1word[i])
        except ValueError:
            # if no word
            temp = -1

        # if word exists
        if temp is not -1:
            # append word count
            newlist2.append(list2count[temp])
            newtemp.append(list2word[temp])
        else:
        # if word doesn't exists append 0
            newlist2.append(0)
            newtemp.append(list1word[i])

    # return new list
    return newlist2
# end def matchLists

def selectionSortInternally(word_count, word):
    for i in range(len(word_count)): #i goes from = to lenth of array
        smallest=findSmallestFrom(word_count,i) #find smallest item in array from current i
        holdSmallest=word_count[smallest] #hold current smallest value found
        holdWord=word[smallest]
        word_count[smallest]=word_count[i] #move the value in the current lower index to whatever smallest was
        word[smallest]=word[i]
        word_count[i]=holdSmallest #put smallest's value in its propar place
        word[i]=holdWord
    return word_count, word #return array of sorted. Only one array every existed
# end def selectionSortInternally

def findSmallestFrom(word_count, index):
    smallest = word_count[index] #hold start item for comparision
    smallest_index = index #hold start location given
    for i in range(index+1, len(word_count)): #go from star+1 to end of array
        if word_count[i] <smallest: #if current smallest is greater then current item
            smallest=word_count[i] #replace current smallest 
            smallest_index=i #store current smallest location
    return smallest_index #return smallest indexx after completing array
# end def findSmallestFrom

def mostCommonWords(song):
    # NOTE: list
    lyrics = readSongs(song)
    stop_words = stopwords.words('english')
    
    # dictionary
    dictWords = { }
    # list
    word = []
    word_count = []
    # string of characters allowed
    validLetters = "abcdefghijklmnopqrstuvwxyz'"

    # loop through lyrics
    for l in lyrics:
        # loop through words in one ine
        for w in l:
            # lower word
            w = str(w).lower()
            # only keep letters
            w = ''.join([char for char in w if char in validLetters])
            # check if word is common
            if w in stop_words:
                continue
            # check if w is in dictionary
            if w not in dictWords:
                dictWords[w] = 1
            elif w in dictWords:
                # if in dectionary get key and value and add to value
                temp = dictWords.get(w)
                dictWords[w] = temp + 1
    
    keys = list(dictWords.keys())
    #loop through allkeys
    for k in range(len(keys)):
        #put keys and values into lists
        word.append(keys[k])
        word_count.append(dictWords[keys[k]])

    # sort words and word count
    word_count, word = selectionSortInternally(word_count,word)

    # reverse lists
    word = word[::-1]
    word_count = word_count[::-1]

    return word_count, word
# end def mostCommonWords
    
def readSongs(songNames):
    '''
    # open file
    file = open("msft.txt", "r")
    # read lines in file
    filedata = file.readlines()
    print(type(file))
    print(type(filedata))
    '''
    # use readlines on a string
    buf = io.StringIO(songNames)
    filedata = buf.readlines()

    # store lyrics
    lyrics = []
    # read line and pllit at newline
    for f in filedata:
        lyrics.append(f.split("\n")[0])
        
    sentences = []

    # loop through new lines in song
    for s in lyrics:
        #print(s)
        # append while only keeping letters
        sentences.append(s.replace("[^a-zA-Z]", " ").split(" "))
    # remove last index in array
    sentences.pop() 
    # return sentences
    return sentences
# end def readSongs

def sentence_similarity(sent1, sent2, stopwords=None):
    # if there is no stop words
    if stopwords is None:
        # make empty array
        stopwords = []
    
    # make sentences lower case
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    # make set of both sentences that are in a list
    # set doesn't have suplicated words
    # set in list
    all_words = list(set(sent1 + sent2))

    # array of zeros that span the length of words
    # ex: [0] * 3 = [0,0,0] or [1,2] * 2 = [1,2,1,2]
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    # loop through words in 1 sentence
    for w in sent1:
        # if word is a common word
        if w in stopwords:
            continue
        # find index of word
        # in vector go to that index and increment word
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return cosine_distance(vector1, vector2)
    #return 1 - cosine_distance(vector1, vector2)
# end def sentence_similarity

def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    # returns a 2d array of zeros 
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    # loop through length of sentence array
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            # if indexes are the same
            if idx1 == idx2: 
                continue
            # get vector
            # pass sentence one and next sentenes with stop words
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
    #print(similarity_matrix[0][0])
    # return matrix of vectors
    return similarity_matrix
# end def build_similarity_matrix

def generate_summary(file_name, top_n=5):
    # get list of common words in english language
    stop_words = stopwords.words('english')
    # empty array
    summarize_text = []

    # read text and slip at new line
    sentences =  readSongs(file_name)

    # get matrix of every sentnce or vectors
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # array of dictionaries that contain an object
    # [sentence][index of dictionary of every other sentence]["weight"]
    # weights every sentence to every other senteces
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)

    # ranks nodes from a graph
    # score every sentence
    # dictionary index:score
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    # sort in reverse
    # number every index
    # return score[index], sentence that is with that index
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    

    #print("Indexes of top ranked_sentence order are ", ranked_sentence)    
    tempLen = len(sentences) / 6
    for i in range(int(tempLen)):
        # get the top sentences
        summarize_text.append(" ".join(ranked_sentence[i][1]))

    # output the summary
    #print("Summarize Text: \n", ". ".join(summarize_text))
    return summarize_text
# end def generate_summary

if __name__ == "__main__":
    main()