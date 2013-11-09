import cPickle
import random
import sys
# load a word map
word_map = cPickle.load(open('mileydavis.pkl','r'))
songs = cPickle.load(open('songtitles.pkl','r'))
seen_songs = []
TEMPLATE = "<html><head><title>{0}</title></head><body>{1}</body></html>"
CHAPTER_HEADING = "<h2>CHAPTER {0}</h2><h3>{1}</h3>"
TITLE = "<h1>Behind the Music: The {0} {1} Story</h1>"

artist_names = ['Miles Davis','Miley Cyrus']

def make_title():
    return TITLE.format(random.choice(artist_names[0].split(' ')), random.choice(artist_names[1].split(' ')))

def find_artist_starting_point(word_map):
    possibles = []
    for (k1,k2) in word_map.keys():
        if k1 == 'MilesDavis' or k2 == 'MilesDavis' or k1 == 'MileyCyrus' or k2 == 'MileyCyrus':
            possibles.append((k1, k2))
    return random.choice(possibles)

def make_chapter(count, songs):
    # if we run out of songs, load them again
    if len(songs) < 1:
        songs = cPickle.load(open('songtitles.pkl','r'))
    song = random.choice(songs)
    songs.remove(song)
    return CHAPTER_HEADING.format(count+1, song)

def finish(bio):
    print TEMPLATE.format('Miley Cyrus', bio)

def clean(text):
    # strip out special chars we use
    if text == 'MilesDavis':
        return 'Miles Davis'
    if text == 'MileyCyrus':
        return 'Miley Cyrus'
    return text.replace('+',' ')

# find a random starting point and get going
(one,two) = find_artist_starting_point(word_map)
words = 2
cur_paragraph_length = 0
max_paragraph_length = random.randint(300,400)
max_chapter_length = random.randint(15,25)
num_paragraphs = 0
# initialize bio with chaper one
bio = make_title() + make_chapter(0, songs) + "<p>" + clean(one) + " " + clean(two) + " "
chapter_count = 1
while True:
    if not word_map.has_key((one, two)):
        (one, two) = find_artist_starting_point(word_map)
        continue
    next = word_map[(one, two)]
    if len(next) > 1:
        next = random.choice(next)
    else:
        next = next[0]
    next = next.strip()
    if next.endswith('.') and cur_paragraph_length > max_paragraph_length:
        bio += clean(next) + "</p>"
        num_paragraphs += 1
        if words > 50000:
            finish(bio)
            break
        if num_paragraphs > max_chapter_length:
            bio += make_chapter(chapter_count, songs)
            chapter_count += 1
            num_paragraphs = 0
        cur_paragraph_length = 0
        max_paragraph_length = random.randint(200,300)
        bio += "<p>"
    else:
        bio += clean(next) + " "
        cur_paragraph_length += len(next)
    one = two
    two = next
    words += 1

