from pyechonest import artist as en_artist, song as en_song
import cPickle
import re
import sys
from pymarkovchain import MarkovChain

from pyechonest import config
config.ECHO_NEST_API_KEY=cPickle.load(open('api_key.pkl'))

def create(name):
    # let's grab some text for our artist
    corpus = create_corpus(name)
    return create_wordmap(corpus)

def create_wordmap(corpus):
    pass

def create_corpus(name):
    artist = en_artist.Artist(name)
    corpus = u''

    # stuff bios and news nto a shared corpus
    for bio in artist.biographies:
        # skip bios that are too short to be any good
        if len(bio['text']) < 200:
            continue
        #raw_bios.write('site-' + bio['site'] + '\n---\n' + bio['text']+'\n----\n')
        text = bio['text'].replace(name,name.replace(' ',''))
        
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

f = codecs.open('mileydavis.txt',encoding='utf-8',mode='w')
f.write(corpus)
f.close()

# get 50 hottest songs for each artist to use as chapter headings
song_titles = []
for name in artist_names:
    songs = en_song.search(artist=name,results=50,sort='song_hotttnesss-desc')
    for song in songs:
        if song.title not in song_titles:
            song_titles.append(song.title)
f = open('songtitles.pkl','w')
cPickle.dump(song_titles,f)
