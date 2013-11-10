import random

CHAPTER_HEADING = "CHAPTER {0}"
CHAPTER_SUBHEAD = "{1}"
TITLE = "Behind the Music: The {0} {1} Story"

def make_title(artists):
    return TITLE.format(random.choice(artists[0].split(' ')), random.choice(artists[1].split(' ')))

def find_artist_starting_point(word_map, artists):
    ccArtists = [x.replace(' ','+') for x in artists]
    possibles = []
    for (k1,k2) in word_map.keys():
        if k1 in ccArtists:
            possibles.append((k1, k2))
    if len(possibles) < 1:
        return random.choice(word_map.keys())
    else:
        return random.choice(possibles)

def make_chapter(count, songs, text):
    song = random.choice(songs)
    # TODO how to prevent dupes without removing songs (have more chapters than songs)
    #songs.remove(song)
    return {'Head': CHAPTER_HEADING.format(count+1),
            'Subhead': song,
            'Text': text}

def clean(text):
    # strip out special chars we use
    return text.replace('+',' ')

def generate_book(artists, word_map, songs):
    book = {'Title': make_title(artists),
            'Chapters': []}
    # find a random starting point and get going
    (one,two) = find_artist_starting_point(word_map, artists)
    words = 2
    cur_paragraph_length = 0
    max_paragraph_length = random.randint(400,600)
    max_chapter_length = random.randint(15,25)
    num_paragraphs = 0
    # init book
    chapter_text = clean(one) + " " + clean(two) + " "
    while True:
        if not word_map.has_key((one, two)):
            (one, two) = find_artist_starting_point(word_map, artists)
            continue
        next = word_map[(one, two)]
        if len(next) > 1:
            next = random.choice(next)
        else:
            next = next[0]
        next = next.strip()
        if next.endswith('.') and cur_paragraph_length > max_paragraph_length:
            # new paragraph, also check for end of chapter / end of book
            chapter_text += clean(next) + "</p>"
            num_paragraphs += 1
            if words > 50000:
                # done with book
                return book
            if num_paragraphs > max_chapter_length:
                # finish up, start new chapter
                book['Chapters'].append(make_chapter(len(book['Chapters']), songs, chapter_text))
                num_paragraphs = 0
                chapter_text = ''
            cur_paragraph_length = 0
            max_paragraph_length = random.randint(200,300)
            chapter_text += "<p>"
        else:
            chapter_text += clean(next) + " "
            cur_paragraph_length += len(next)
        one = two
        two = next
        words += 1

