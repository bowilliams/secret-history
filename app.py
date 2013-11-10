from flask import Flask, render_template, request
import cPickle
import uuid
import codecs
import random
import soundcloud
import wordmapper
from generate import generate_book

app = Flask(__name__)
app.debug = True

# key is name, val is tuple (word_map_pickle_name, song_pickle_name)
artist_cache = {}

def make_file_safe_name(name):
    return "".join([c for c in name if c.isalpha() or c.isdigit()]).rstrip() + ".pkl"

@app.route("/")
def hello():
    # find some mashups
    sc = soundcloud.Client(client_id='140e38c1e2f7f00bbf3068c52cddd69c')
    vs_list = sc.get('/tracks', q='vs')
    tracks = []
    if len(vs_list) > 1:
        tracks = wordmapper.filter_sc_tracks(vs_list)
    return render_template('index.html', tracks=tracks)

@app.route("/book", methods=['POST'])
def book():
    artists = [request.form['artist1'], request.form['artist2']]
    return generate_from_artists(artists)

@app.route("/mashup_book/<int:track_id>", methods=['GET'])
def mashup_book(track_id):
    # load tracks from cache
    tracks = cPickle.load(open('mashups.pkl'))
    t = [t for t in tracks if t.id == track_id][0]
    artists = wordmapper.get_artists_from_title(t.title)
    return generate_from_artists(artists, track=t)

def generate_from_artists(artists, track=None):
    # do we have pickles for these artist names already
    word_maps = []
    all_songs = []
    all_images = []
    for name in artists:
        if artist_cache.has_key(name) and len(artist_cache[name]) == 3:
            word_maps.append(cPickle.load(open(artist_cache[name][0])))
            all_songs += cPickle.load(open(artist_cache[name][1]))
            all_images += cPickle.load(open(artist_cache[name][2]))
        else:
            try:
                word_map = wordmapper.create(name)
            except Exception:
                error = "Could not find an artist named {0}".format(name)
                return render_template('index.html',error=error)
            artist_songs = wordmapper.get_songs(name)
            artist_images = wordmapper.get_images(name)
            filename = make_file_safe_name(name)
            cPickle.dump(word_map, open(filename+'words','w'))
            cPickle.dump(artist_songs, open(filename+'songs','w'))
            cPickle.dump(artist_images, open(filename+'images','w'))
            artist_cache[name] = (filename+'words', filename+'songs', filename+'images')
            word_maps.append(word_map)
            all_songs += artist_songs
            all_images += artist_images
    # make a book
    word_map = wordmapper.consolidate(word_maps)
    book = generate_book(artists, word_map, all_songs, all_images)
    permalink = str(uuid.uuid4())+'.html'
    text = render_template('book.html', book=book, track=track, permalink=permalink)
    # save text to new file
    f = codecs.open(permalink,encoding='utf-8',mode='w')
    f.write(text)
    return text

if __name__ == "__main__":
    app.run()
