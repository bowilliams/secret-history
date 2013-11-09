
# add to PyMarkovChain
#mc = MarkovChain('./mileydavis')
#mc.generateDatabase(corpus)
#print mc.generateString()
#sys.exit()
import cPickle
import codecs
corpus = codecs.open('mileydavis.txt','r')

word_map = {}
for line in corpus.readlines():
    print line
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
        print ' '.join([one,two,word])
        if word_map.has_key((one, two)):
            if word in word_map[(one, two)]:
                continue
            word_map[(one, two)].append(word)
        else:
            word_map[(one, two)] = [word]
        one = two
        two = word

# let's write that out to a thing we can use later
pkl_file = open('mileydavis.pkl', 'w')
cPickle.dump(word_map, pkl_file)

