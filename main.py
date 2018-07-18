""" A simple web-app – Enter any artist in the search field and get a report of
the audio features – acousticness, danceability, energy, musical key, tempo, etc. –
of their top ten hits, with downloadable previews, as well as their genre and
popularity. """

import spotipy # Used to query an artist and return information about their top ten tracks
import generatehtml as util # Import the file that generates a report about the artist as html code
from spotipy.oauth2 import SpotifyClientCredentials # For authentication purposes and access to the Spotify API
from http.server import BaseHTTPRequestHandler, HTTPServer # To launch the final artist report with a local server

client_credentials_manager = SpotifyClientCredentials(client_id='YOUR CLIENT ID HERE',
                                                      client_secret='YOUR CLIENT SECRET HERE')

spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Searches for information about the top ten tracks of a given artist
def artistinfo(name):
    results = spotify.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    # At this point, the artist inputted was not found; exit
    if not items:
        return
    artist = items[0]
    name = artist['name']
    if artist['images']:
        img = artist['images'][-2]['url']
    else:
        img = None
    genres = ', '.join(artist['genres'])
    popularity = artist['popularity']
    uri = artist['uri'] # The unique identifier of any artist registered with Spotify
    tracks = spotify.artist_top_tracks(uri)['tracks'] # Find the top ten tracks
    cache = {} # A dictionary where each key is a track and each value is a dictionary containing audio features and their values
    for track in tracks:
        features = spotify.audio_features(tracks=[track['uri']])[0]
        preview = track['preview_url']
        if preview: # The track has a 30-second preview available
            features['preview'] = preview
        cache[track['name']] = features
    return util.report(parameters, cache, name, img, genres, popularity) # Generate the report of the artist as html code

# The audio features of interest; can be substituted with any from https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/ ""
parameters = ['acousticness',
              'danceability',
              'energy',
              'liveness',
              'key',
              'valence',
              'tempo',
              'mode',
              'time_signature']

# Basic server info
HOST_NAME = 'localhost'
PORT_NUMBER = 8000

# A class that handles client-server communication to get an artist as input and display the html report page
class MyHandler(BaseHTTPRequestHandler):

    # The html page displayed should be blank (except for the form field) to start
    blank = True

    # Respond to a GET request (e.g. an artist was inputted into the form field)
    def do_GET(self):
        #print("In do_GET", self.path); # Print out the GET request to the console
        response = self.handle_http(500, self.path) # Generate an appropriate response
        self.wfile.write(response) # Show the generated response

    # Called by do_GET to generate the server's response – an html page – to a client's request
    def handle_http(self, status_code, path):
        print("In handle_http", self)
        print('Artist Path:', path)
        self.send_response(status_code) # Send the HTTP status code associated with the call to do_GET
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # The page is initialized
        if MyHandler.blank:
            content = util.setup() + util.finish_setup() # Sets up a minimal interface with just a form prompting client for an artist name
            MyHandler.blank = False
        else:
            name = path[9:].replace('+', ' ').title() # Gets the name of the artist from the path received from the form submission
            print('Artist Name:', name)
            artist_report = artistinfo(name) # Gets a report of an artist if the artist is found
            if artist_report: # Artist was found, and a report was generated
                content = util.setup() + artist_report # Displays the client form with a full report of the queried artist
            else: # Artist queried was not found; prints the client form and an error message
                content = util.setup() + util.error_msg() + util.finish_setup()
        return bytes(content, 'UTF-8')


if __name__ == "__main__":
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print('Server Live - %s:%s' % (HOST_NAME, PORT_NUMBER))
    # Serve forever locally
    try:
        httpd.serve_forever()
    # To kill the server, use KeyboardInterrupt
    except KeyboardInterrupt:
        pass
    httpd.server_close()
