from dataset import *
import sys
import numpy as np
import heapq
import nltk
from nltk import sent_tokenize, word_tokenize, Tree, pos_tag, WordNetLemmatizer
from collections import Counter

noun = "(<NN>|<NNS>)"
verb = "(<VB>|<VBD>|<VBG>|<VBN>|<VBP>|<VBZ>)"
adj = "(<JJ>|<JJS>|<JJR>)"
adv = "(<MD>|<RB>|<RBR>|<RBS>)"

def adj_NP():
    g="adj_NP: {<DT>?"
    g+=f"{adj}+{noun}+"
    g+="}"
    return g

def adv_VP():
    g="adv_VP: {"
    g+=f"(({adv}+{verb}+{adv}+)|({verb}+{adv}+{verb}+))"
    g+=f"<DT>?{adj}*{noun}*"
    g+="}"
    return g

def punctuation_strip(string):
    puncts = ",.?:;/<>!@#$%^&*()[]{}"
    for p in puncts:
        string = string.replace(p,' '+p+' ')
    return string

def extract_grammar(string, grammar):
    string = punctuation_strip(string)
    tokens = word_tokenize(string)
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
    s=""
    t=[]
    for item in tree:
        s+=item[0]+" "
        t.append(item)
    return s[:-1],t

def make_list(treelist):
    return list(dict(map(compress_tree, treelist)).keys()), list(dict(map(compress_tree, treelist)).values())

def remove_abb(string):
    string = string.replace("'m"," am")
    string = string.replace("'re"," are")
    string = string.replace("n't"," not")
    string = string.replace("'d"," would")
    return string

def process_product(typ, asin):
    l = products_list(typ)
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
    ripe_text = ' '.join(strlist)
    tagdict = dict([item for sublist in taglist for item in sublist])
    return raw_text, ripe_text, strlist, taglist, tagdict

def tfidf(term, document, collection):
    tf = Counter(word_tokenize(document))[term]
    df = sum(map(lambda t: term in t, collection))  
    return (1+np.log10(tf))*np.log10(len(collection)/df)

def normalize(word):
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
    sentence = punctuation_strip(sentence)
    return ' '.join(list(map(normalize,word_tokenize(sentence))))
        

def generate_score(typ, asin):
    raw_text, ripe_text, strlist, taglist, tagdict = process_product(typ, asin)
    document = normalize_sentence(raw_text)
    collection = list(map(normalize_sentence, reviewText(typ)))
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

def generate_summary(typ, asin, n):
    sd = generate_score(typ, asin)
    return heapq.nlargest(n, sd, key=sd.get)


if __name__ == '__main__':
    if (len(sys.argv) != 1):
        print("Usage: \npython summarizer.py\n")
        exit(1)
    print("Section 3.4 Review Summarizer")
    print("Developed by Jiang Haofeng\n2022/10/22\n--------------------------------------------\n")
    print("Here are the product types avaliable:")
    l = list(np.arange(len(TYPES)))
    d = dict(zip(l,TYPES))
    for key in d:
        print(f"{key}: {d[key]}") 
        
    next_or_exit = ""
    while (next_or_exit != "exit"):
        typ = input("\nPlease choose the type of the product by index (e.g. 0, 12, 23, etc.):")
        while not (typ.replace('-','',1).isdigit() and int(typ) >= -24 and int(typ) <= 23):
            print("The index must be an integer from -24 to 23")
            typ = input("Please choose the type of the product by index (e.g. 0, 12, 23, etc.):")
        writefile(typ)
        print(f"\nIn type {regularize(typ)}, some product ids are: (for simplexity, just showing up to 20 here)")
        l=product_id(typ)
        print(', '.join(l[:min(20,len(l))]))
        i = input(f"Please choose the product id that you want to view the review summary (e.g. {l[0]}):")
        while not (i in l):
            print("The asin must be in this type")
            i = input(f"Please choose the product id that you want to view the review summary (e.g. {l[0]}):")
        print(f"\nReview summary of the product {i}:")
        print('\n'.join(generate_summary(typ, i, 10)))
        print("\n")
        next_or_exit = ""
        while (next_or_exit != "next" and next_or_exit != "exit"):
            next_or_exit = input("Enter 'next' to view other products, or enter 'exit' to exit:")       
    print("\nThanks for using!")
    exit(0)