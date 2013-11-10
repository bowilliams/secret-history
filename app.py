from flask import Flask, render_template, request
import cPickle
import uuid
import codecs

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
    return render_template('index.html')

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    artists = [request.form['artist1'], request.form['artist2']]
    # do we have pickles for these artist names already
    word_maps = []
    all_songs = []
    for name in artists:
        if artist_cache.has_key(name):
            word_maps.append(cPickle.load(open(artist_cache[name][0])))
            all_songs += cPickle.load(open(artist_cache[name][1]))
        else:
            word_map = wordmapper.create(name)
            artist_songs = wordmapper.get_songs(name)
            filename = make_file_safe_name(name)
            cPickle.dump(word_map, open(filename+'words','w'))
            cPickle.dump(artist_songs, open(filename+'songs','w'))
            artist_cache[name] = (filename+'words', filename+'songs')
            word_maps.append(word_map)
            all_songs += artist_songs
    # make a book
    word_map = wordmapper.consolidate(word_maps)
    book = generate_book(artists, word_map, all_songs)
    text = render_template('book.html', book=book)
    # save text to new file
    f = codecs.open(str(uuid.uuid4())+'.html',encoding='utf-8',mode='w')
    f.write(text)
    return text

if __name__ == "__main__":
    app.run()
