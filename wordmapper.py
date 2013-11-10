from pyechonest import artist as en_artist, song as en_song
import os
import soundcloud
import random
import cPickle
import re
import sys

from pyechonest import config
config.ECHO_NEST_API_KEY=cPickle.load(open('ellis_key.pkl'))

def get_artists_from_title(title):
    splits = title.split('vs')
    # we assume the splits have an artist name, some whitespace,
    # and some kind of delimiter (usually a dash) from the title 
    # of the mashup
    artists = []
    for split in splits:
        artist = split.strip()
        if '-' in artist:
            artist = artist[:artist.index('-')].strip()
        for delim in ['&',',']:
            if delim in artist:
                # so yeah there's bands like 'huey lewis & the news
                # or 'crosby, stills & nash', but again
                # not trying to be perfect here
                artist = random.choice(artist.split(delim)).strip()
        artists.append(artist)
    return artists

def filter_sc_tracks(tracklist):
    # do we have a cached copy
    if os.path.exists('mashups.pkl'):
        return cPickle.load(open('mashups.pkl'))
    # this is not even trying to be perfect- given a big list
    # we just want to find a few tracks we think we can pull artist
    # names from given a pattern of "[artist] vs [artist] - [name]"
    possibles = []
    good_tracks = []
    for t in tracklist:
        title = t.title.replace('Vs','vs').replace('VS','vs')
        if not 'vs' in title:
            continue
        artists = get_artists_from_title(title)
        if len(artists) == 2:
            t.match_artists = artists
            possibles.append(t)
    # so now we have some things we think we have artist, let's also
    # check that we can get an echonest artist
    # as soon as we have 10, stop
    for track in possibles:
        for artist in track.match_artists:
            try:
                a = en_artist.Artist(artist)
                if not en_artist.Artist(artist):
                    continue
            except Exception:
                continue
        good_tracks.append(track)
    f = open('mashups.pkl','w')
    cPickle.dump(good_tracks, f)
    f.close()
    return good_tracks

def consolidate(word_maps):
    new_map = {}
    for map in word_maps:
        for key in map:
            if new_map.has_key(key):
                for val in map[key]:
                    if val not in new_map[key]:
                        new_map[key].append(val)
            else:
                new_map[key] = map[key]
    return new_map

def create(name):
    # let's grab some text for our artist
    corpus = create_corpus(name)
    return create_wordmap(corpus)

def create_wordmap(corpus):
    word_map = {}
    for line in corpus.split('\n'):
        # restart at each line (should just be one huge line anyway)
        one = None
        two = None
        for word in line.split():
            word = word.strip()
            if not one:
                one = word
                continue
            if not two:
                two = word
                continue
            if word_map.has_key((one, two)):
                if word in word_map[(one, two)]:
                    continue
                word_map[(one, two)].append(word)
            else:
                word_map[(one, two)] = [word]
            one = two
            two = word
    return word_map

def create_corpus(name):
    artist = en_artist.Artist(name)
    corpus = u''

    # stuff bios and news nto a shared corpus
    for bio in artist.biographies:
        # skip bios that are too short to be any good
        if len(bio['text']) < 200:
            continue
        #raw_bios.write('site-' + bio['site'] + '\n---\n' + bio['text']+'\n----\n')
        text = bio['text'].replace(name,name.replace(' ','+'))
        
        for line in text.split('\n'):
            # skip wikipedia headers
            if len(line) < 50:
                continue
            for sentence in re.split('\.\W+', line):
                if len(sentence) <= 5:
                    continue
                # keep quotes together
                qt_match = re.match('.+("[^"]+")', sentence)
                if qt_match:
                    sentence = sentence.replace(qt_match.group(1), qt_match.group(1).replace(' ','+'))
                # doesn't always end with a .
                sentence = sentence.rstrip('.')
                corpus += sentence + u'. '

    #for new in artist.news:
    #    corpus = corpus + u' ' + new['summary'].replace(name,name.replace(' ',''))
    #for review in artist.reviews:
    #    corpus = corpus + u' ' + review['summary'].replace(name,name.replace(' ',''))
    return corpus

def get_images(name):
    image_urls = []
    artist = en_artist.Artist(name)
    for img in artist.images:
        image_urls.append(img['url'])
    return image_urls

def get_songs(name):
    # get 50 hottest songs for each artist to use as chapter headings
    song_titles = []
    songs = en_song.search(artist=name,results=50,sort='song_hotttnesss-desc')
    for song in songs:
        if song.title not in song_titles:
            song_titles.append(song.title)
    return song_titles
