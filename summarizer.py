from dataset import *
import nltk
from nltk import sent_tokenize, word_tokenize, Tree, pos_tag
from nltk.corpus import stopwords
from collections import Counter

noun = "(<NN>|<NNS>|<NNP>|<NNPS>)"
verb = "(<VB>|<VBD>|<VBG>|<VBN>|<VBP>|<VBZ>)"
adj = "(<JJ>|<JJS>|<JJR>)"
adv = "(<MD>|<RB>|<RBR>|<RBS>)"

sentence0 = products_list(-2)[0]['reviewText']
sentence1 = products_list(-2)[1]['reviewText']
sentence2 = products_list(-2)[2]['reviewText']
sentence3 = products_list(-2)[3]['reviewText']
tokens = word_tokenize(sentence0)
pos = pos_tag(tokens)

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

def extract_grammar(string, grammar):
    string = string.replace(".", ". ")
    tokens = word_tokenize(string)
    tokens = [word for word in tokens if word.isalpha() or ("'" in word) or ("." in word)]
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
    string = string.replace("'m","am")
    string = string.replace("'re","are")
    string = string.replace("n't","not")
    string = string.replace("'d","would")
    return string

def process_product(typ, asin):
    l = products_list(typ)
    raw_text = ""
    ripe_text = ""
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
    return raw_text, ripe_text, strlist, taglist

