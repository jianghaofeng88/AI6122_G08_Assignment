from dataset import *
import sys
import numpy as np
import heapq
import nltk
from nltk import sent_tokenize, word_tokenize, Tree, pos_tag, WordNetLemmatizer
from collections import Counter

global dataset200
global asin200
global reviewText200

nltk.download("averaged_perceptron_tagger")
nltk.download("punkt")

noun = "(<NN>|<NNS>)"
verb = "(<VB>|<VBD>|<VBG>|<VBN>|<VBP>|<VBZ>)"
adj = "(<JJ>|<JJS>|<JJR>)"
adv = "(<MD>|<RB>|<RBR>|<RBS>)"


def get_global_values():
    '''
    Get the initialized dataset from dataset.py.
    '''
    
    global dataset200
    dataset200 = products_list()
    global asin200
    asin200 = product_id()
    global reviewText200  
    reviewText200 = review_text()


def set_global_values(d,a,r):
    '''
    Enable other python files to set the dataset.
    '''
    
    global dataset200
    dataset200 = d
    global asin200
    asin200 = a
    global reviewText200  
    reviewText200 = r


def adj_NP():
    '''
    Regular expression for NP with adjectives.
    '''
    
    
    g="adj_NP: {<DT>?"
    g+=f"{adj}+{noun}+"
    g+="}"
    return g


def adv_VP():
    '''
    Regular expression for VP with adverbs.
    '''
    
    g="adv_VP: {"
    g+=f"(({adv}+{verb}+{adv}+)|({verb}+{adv}+{verb}+))"
    g+=f"<DT>?{adj}*{noun}*"
    g+="}"
    return g


def punctuation_strip(string):
    '''
    Add strips to all popular punctuations to avoid unexpected tokenization result.
    '''    
    
    puncts = ",.?:;!"
    for p in puncts:
        string = string.replace(p,' '+p+' ')
    return string


def extract_grammar(string, grammar):
    '''
    The core of extract candidate noun phrases and verb phrases based on the two regular expressions just defined.
    '''
        
    string = punctuation_strip(string)
    tokens = word_tokenize(string)
    tokens = [word for word in tokens if word.isalnum() \
              or '-' in word or word in [',','.','?',':',';','!']]
    pos = pos_tag(tokens)  
    cp = nltk.RegexpParser(grammar)
    parse_tree = cp.parse(pos)
    result = []
    for child in parse_tree:
        if isinstance(child, Tree):               
            if child.label() == grammar[:grammar.index(':')]:
                result.append(child)   
    return result
  

def compress_tree(tree):
    '''
    Process the parse tree to get a user-friendly data structure.
    '''
    
    s=""
    t=[]
    for item in tree:
        s+=item[0]+" "
        t.append(item)
    return s[:-1],t


def make_list(treelist):
    '''
    Get the list of both candidate strings and the corresponding tags.
    '''
    
    return list(dict(map(compress_tree, treelist)).keys()), list(dict(map(compress_tree, treelist)).values())


def remove_abb(string):
    '''
    Remove possible abbreviations may appear in the review.
    '''
        
    string = string.replace("'m"," am")
    string = string.replace("'re"," are")
    string = string.replace("n't"," not")
    string = string.replace("doesnt","does not")
    string = string.replace("dont","do not")
    string = string.replace("didnt","did not")
    string = string.replace("isnt","is not")
    string = string.replace("arent","are not")    
    string = string.replace("'d"," would")
    return string


def normalize(word):
    '''
    Normalize a single word by case-folding, lemmatization, abbreviation processing.
    '''
    
    # Remove abbreviation
    word = remove_abb(word)
    # Lemmatization
    word = WordNetLemmatizer().lemmatize(word)
    word = WordNetLemmatizer().lemmatize(word, pos ="a")
    word = WordNetLemmatizer().lemmatize(word, pos ="v")
    # Case folder
    word = word.lower()
    return word


def normalize_sentence(sentence):
    '''
    Normalize a phrase by case-folding, lemmatization, abbreviation processing.
    '''    
    
    sentence = punctuation_strip(sentence)
    return ' '.join(list(map(normalize,word_tokenize(sentence))))
 
        
def process_product(asin):
    '''
    Traverse through the dataset and find the target product id.
    Record all useful information.
    '''
    
    l = dataset200
    raw_text = ""
    strlist = []
    taglist = []
    for item in l:
        if item['asin']==asin:
            sentence = remove_abb(item['reviewText'])
            raw_text += sentence
            NPs = extract_grammar(sentence,adj_NP())
            VPs = extract_grammar(sentence,adv_VP())
            strlist.extend(make_list(NPs)[0])
            strlist.extend(make_list(VPs)[0])
            taglist.extend(make_list(NPs)[1])
            taglist.extend(make_list(VPs)[1])
    tagdict = dict([item for sublist in taglist for item in sublist])
    return raw_text, strlist, tagdict


def tfidf(term, document, collection):
    '''
    The essential calculation of TF-IDF algorithm.
    '''
    
    tf = max(1,Counter(word_tokenize(document))[term])
    df = sum(map(lambda t: term in t, collection))  
    return (1+np.log10(tf))*np.log10(len(collection)/df)


def generate_score(asin):
    '''
    Generate the TF-IDF weight of each candidate phrases.
    '''
    
    raw_text, strlist, tagdict = process_product(asin)
    document = normalize_sentence(raw_text)
    collection = list(map(normalize_sentence, reviewText200))
    score_dictionary = {}
    for s in strlist:
        normalized_keys = list(map(normalize_sentence, score_dictionary.keys()))
        if normalize_sentence(s) in ' '.join(normalized_keys) or sum(map(lambda k: k in normalize_sentence(s), normalized_keys))>0:
            continue
        score = 0
        tokens = word_tokenize(s)
        for word in tokens:
            if (tagdict[word] != 'DT' and tagdict[word] != 'MD' and word != 'not'):
                score += tfidf(normalize(word), document, collection)
        score_dictionary[s]=score
    return score_dictionary

def generate_summary(asin, n):
    '''
    Sort and output n highest scores among candidate phrases.
    '''  
    
    sd = generate_score(asin)
    return heapq.nlargest(n, sd, key=sd.get)


if __name__ == '__main__':
    writefile(-2)
    writefile(-3)
    print("\n---------------------------------------------------\n")
    
    initialize_dataset(-2)
    get_global_values()
    review_number = {}
    for review in dataset200:
        if review['asin'] not in review_number:
            review_number[review['asin']] = 1
        else:
            review_number[review['asin']] += 1
    mid_asin = list(review_number.keys())[list(review_number.values()).index(10)]
    print(f"type = {regularize(-2)[0]}, asin = {mid_asin}\nReview summary:")
    print('\n'.join(generate_summary(mid_asin, 10)))
    print("\n---------------------------------------------------\n")
    
    initialize_dataset(-3)
    get_global_values()
    review_number = {}
    for review in dataset200:
        if review['asin'] not in review_number:
            review_number[review['asin']] = 1
        else:
            review_number[review['asin']] += 1
    mid_asin = list(review_number.keys())[list(review_number.values()).index(10)]
    print(f"type = {regularize(-3)[0]}, asin = {mid_asin}\nReview summary:")
    print('\n'.join(generate_summary(mid_asin, 10)))
    print("\n---------------------------------------------------\n")
    
    exit(0)