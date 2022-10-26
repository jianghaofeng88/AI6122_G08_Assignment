#!/usr/bin/env python3

from dataset import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import nltk 
from nltk import word_tokenize 
from nltk.corpus import stopwords 
from nltk.corpus import sentiwordnet as swn 
import string
from nltk.tokenize import sent_tokenize

nltk.download('sentiwordnet')
global dataset200
global asin200
global reviewText200


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


def remove_abb(string):
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

def get_review_by_id(i):
    texts_o = dataset200
    texts = []
    for t in texts_o:
        if t['asin'] == i:
            texts.append(t['reviewText'])
    return texts

def score_for_product(id):
    texts = get_review_by_id(id)
    if len(texts)==0:
        return -2 # No such product id
    score = 0
    for text in texts:
        text = remove_abb(text)
        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(text)
        score += vs['compound']
        # print("{:-<65} {}".format(text, str(vs)))
        # break
    score /= len(texts)
    # print(score)
    return score

def ranking_of_products():
    ids = asin200
    products_score = []
    for id in ids:
        score = score_for_product(id)
        if score == -2:
            continue
        products_score.append((id,score))
        
    for i in range(len(products_score)):
        for j in range(i+1,len(products_score)):
            a = products_score[i]
            b = products_score[j]
            if a[1]<b[1]:
                products_score[i] = b
                products_score[j] = a
    return products_score

def text_score(text):
    stop = stopwords.words("english") + list(string.punctuation)
    ttt = nltk.pos_tag([i for i in word_tokenize(str(text).lower()) if i not in stop])
    word_tag_fq = nltk.FreqDist(ttt)
    wordlist = word_tag_fq.most_common()

    key = []
    part = []
    frequency = []
    for i in range(len(wordlist)):
        key.append(wordlist[i][0][0])
        part.append(wordlist[i][0][1])
        frequency.append(wordlist[i][1])
    textdf = pd.DataFrame({'key':key,
                      'part':part,
                      'frequency':frequency},
                      columns=['key','part','frequency'])

    n = ['NN','NNP','NNPS','NNS','UH']
    v = ['VB','VBD','VBG',' ','VBP','VBZ']
    a = ['JJ','JJR','JJS']
    r = ['RB','RBR','RBS','RP','WRB']

    for i in range(len(textdf['key'])):
        z = textdf.iloc[i,1]

        if z in n:
            textdf.iloc[i,1]='n'
        elif z in v:
            textdf.iloc[i,1]='v'
        elif z in a:
            textdf.iloc[i,1]='a'
        elif z in r:
            textdf.iloc[i,1]='r'
        else:
            textdf.iloc[i,1]=''
            
    score = []
    for i in range(len(textdf['key'])):
        m = list(swn.senti_synsets(textdf.iloc[i,0],textdf.iloc[i,1]))
        s = 0
        ra = 0
        if len(m) > 0:
            for j in range(len(m)):
                s += (m[j].pos_score()-m[j].neg_score())/(j+1)
                ra += 1/(j+1)
            score.append(s/ra)
        else:
            score.append(0)
            
    return pd.concat([textdf,pd.DataFrame({'score':score})],axis=1)

def get_senti_words(text):
    text = remove_abb(text)
    df = text_score(text)
    stop = list(string.punctuation)

    n = ['NN','NNP','NNPS','NNS','UH']
    v = ['VB','VBD','VBG',' ','VBP','VBZ']
    a = ['JJ','JJR','JJS']
    r = ['RB','RBR','RBS','RP','WRB']
    ttt = nltk.pos_tag([i for i in word_tokenize(str(text).lower()) if i not in stop])
    words = []
    rownum = df.shape[0]
    for i in ttt:
        for j in range(rownum):
            if i[0] == df.iloc[j,0]:
                temp_score = df.iloc[j,3]
        if i[1] in n:
            words.append((i[0],'n',temp_score))
        elif i[1] in v:
            words.append((i[0],'v',temp_score))
        elif i[1] in a:
            words.append((i[0],'a',temp_score))
        elif i[1] in r:
            words.append((i[0],'r',temp_score))
        else:
            words.append((i[0],'',temp_score))
    
    # print(df)
    
    senti_words_indexes = []
    for i in range(rownum):
        if (df.iloc[i,3] >= 0.1 or df.iloc[i,3] <= -0.1):
            for j in range(len(words)):
                tp = words[j]
                if tp[0] == df.iloc[i,0]:
                    senti_words_indexes.append(j)
            # print(df.iloc[i,0],df.iloc[i,1],df.iloc[i,3])
    results = []

    index = senti_words_indexes[0]
    i = 0
    while len(senti_words_indexes) != 0:
        if words[index][0]=="i":
            del senti_words_indexes[i]
            i -= 1
        elif words[index][1]=="a":
            temp = index - 1
            while words[temp][1]=="r":
                temp -= 1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1

        elif words[index][1]=="v":
            temp = index - 1
            while words[temp][1]=="r":
                temp -= 1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1
            
        elif words[index][1]=="n":
            temp = index - 1
            while words[temp][1]=="r":
                temp -= 1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1
        
        else:
            del senti_words_indexes[i]
            i -= 1

        if len(senti_words_indexes) == 0:
            break
        i = (i+1)%len(senti_words_indexes)
        index = senti_words_indexes[i]
    return results

def get_neg_words(text):
    text = remove_abb(text)
    df = text_score(text)
    stop = list(string.punctuation)

    n = ['NN','NNP','NNPS','NNS','UH']
    v = ['VB','VBD','VBG',' ','VBP','VBZ']
    a = ['JJ','JJR','JJS']
    r = ['RB','RBR','RBS','RP','WRB']
    ttt = nltk.pos_tag([i for i in word_tokenize(str(text).lower()) if i not in stop])
    words = []
    rownum = df.shape[0]
    for i in ttt:
        temp_score = 0
        for j in range(rownum):
            if i[0] == df.iloc[j,0]:
                temp_score = df.iloc[j,3]
        if i[1] in n:
            words.append((i[0],'n',temp_score))
        elif i[1] in v:
            words.append((i[0],'v',temp_score))
        elif i[1] in a:
            words.append((i[0],'a',temp_score))
        elif i[1] in r:
            words.append((i[0],'r',temp_score))
        else:
            words.append((i[0],'',temp_score))
    # print(df)
    
    senti_words_indexes = []
    # for i in range(rownum):
    #     if (df.iloc[i,3] >= 0.1 or df.iloc[i,3] <= -0.1):
    #         for j in range(len(words)):
    #             tp = words[j]
    #             if tp[0] == df.iloc[i,0]:
    #                 senti_words_indexes.append(j)
    #         # print(df.iloc[i,0],df.iloc[i,1],df.iloc[i,3])
    
    for i in range(len(words)):
        if (words[i][2] >= 0.1 or words[i][2] <= -0.1):
                senti_words_indexes.append(i)

    results = []

    if len(senti_words_indexes) == 0:
        return []
    index = senti_words_indexes[0]
    i = 0
    while len(senti_words_indexes) != 0:
        sign = 1
        if words[index][0]=="i":
            del senti_words_indexes[i]
            i -= 1
        elif words[index][1]=="a":
            if words[index][2]<=-0.1:
                sign*=-1
            temp = index - 1
            while words[temp][1]=="r":
                temp -= 1
                if words[temp][2]<=-0.1:
                    sign*=-1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    if sign == -1:
                        results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    if sign == -1:
                        results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1

        elif words[index][1]=="v":
            if words[index][2]<=-0.1:
                sign*=-1
            temp = index - 1
            while words[temp][1]=="r":
                if words[temp][2]<=-0.1:
                    sign*=-1
                temp -= 1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    if sign == -1:
                        results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    if sign == -1:
                        results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1
            
        elif words[index][1]=="n":
            if words[index][2]<=-0.1:
                sign*=-1
            temp = index - 1
            while words[temp][1]=="r":
                if words[temp][2]<=-0.1:
                    sign*=-1
                temp -= 1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    if sign == -1:
                        results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    if sign == -1:
                        results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1
        
        else:
            del senti_words_indexes[i]
            i -= 1

        if len(senti_words_indexes) == 0:
            break
        i = (i+1)%len(senti_words_indexes)
        index = senti_words_indexes[i]
    return results

def get_pos_words(text):
    text = remove_abb(text)
    df = text_score(text)
    stop = list(string.punctuation)

    n = ['NN','NNP','NNPS','NNS','UH']
    v = ['VB','VBD','VBG',' ','VBP','VBZ']
    a = ['JJ','JJR','JJS']
    r = ['RB','RBR','RBS','RP','WRB']
    ttt = nltk.pos_tag([i for i in word_tokenize(str(text).lower()) if i not in stop])
    words = []
    rownum = df.shape[0]
    for i in ttt:
        temp_score = 0
        for j in range(rownum):
            if i[0] == df.iloc[j,0]:
                temp_score = df.iloc[j,3]
        if i[1] in n:
            words.append((i[0],'n',temp_score))
        elif i[1] in v:
            words.append((i[0],'v',temp_score))
        elif i[1] in a:
            words.append((i[0],'a',temp_score))
        elif i[1] in r:
            words.append((i[0],'r',temp_score))
        else:
            words.append((i[0],'',temp_score))
    
    # print(df)
    
    senti_words_indexes = []
    for i in range(rownum):
        if (df.iloc[i,3] >= 0.1 or df.iloc[i,3] <= -0.1):
            for j in range(len(words)):
                tp = words[j]
                if tp[0] == df.iloc[i,0]:
                    senti_words_indexes.append(j)
            # print(df.iloc[i,0],df.iloc[i,1],df.iloc[i,3])
    results = []

    if len(senti_words_indexes) == 0:
        return []

    index = senti_words_indexes[0]
    i = 0
    while len(senti_words_indexes) != 0:
        sign = 1
        if words[index][0]=="i":
            del senti_words_indexes[i]
            i -= 1
        elif words[index][1]=="a":
            if words[index][2]<=-0.1:
                sign*=-1
            temp = index - 1
            while words[temp][1]=="r":
                temp -= 1
                if words[temp][2]<=-0.1:
                    sign*=-1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    if sign == 1:
                        results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    if sign == 1:
                        results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1

        elif words[index][1]=="v":
            if words[index][2]<=-0.1:
                sign*=-1
            temp = index - 1
            while words[temp][1]=="r":
                if words[temp][2]<=-0.1:
                    sign*=-1
                temp -= 1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    if sign == 1:
                        results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    if sign == 1:
                        results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1
            
        elif words[index][1]=="n":
            if words[index][2]<=-0.1:
                sign*=-1
            temp = index - 1
            while words[temp][1]=="r":
                if words[temp][2]<=-0.1:
                    sign*=-1
                temp -= 1
            temp+=1
            # print(temp)
            if temp != index:
                phrase = ""
                for j in range(temp,index):
                    phrase = phrase + words[j][0] + " "
                phrase = phrase + words[index][0]
                if phrase not in results:
                    if sign == 1:
                        results.append(phrase)
                # print(phrase)
                del senti_words_indexes[i]
                i -= 1
                # print("1",senti_words_indexes)
                for j in range(temp,index):
                    # print("j",j)
                    for k in range(len(senti_words_indexes)):
                        # print("k",senti_words_indexes[k])
                        if j == senti_words_indexes[k]:
                            del senti_words_indexes[k]
                            i -= 1
                            break
                # print("2",senti_words_indexes)
                # break
            else:
                if words[index][0] not in results:
                    if sign == 1:
                        results.append(words[index][0])
                del senti_words_indexes[i]
                i -= 1
        
        else:
            del senti_words_indexes[i]
            i -= 1

        if len(senti_words_indexes) == 0:
            break
        i = (i+1)%len(senti_words_indexes)
        index = senti_words_indexes[i]
    return results

if __name__ == '__main__':
    typ = "Digital Music"
    
    writefile(typ)
    initialize_dataset(typ)
    get_global_values()
    rank = ranking_of_products()
    for i in rank:
        print(i[0],'%.4f'%i[1])
    print("------------------------------------")
    ids = asin200
    texts = get_review_by_id(ids[0])
    v = []
    all_phrase_pos = []
    all_phrase_neg = []
    # s = "I love you."
    # result = get_neg_words(s)
    for text in texts:
        sentences = sent_tokenize(text)
        for s in sentences:
            result = get_pos_words(s)
            analyzer = SentimentIntensityAnalyzer()
            vs = analyzer.polarity_scores(s)
            if vs['compound']>0:
                for phrase in result:
                    if phrase not in all_phrase_pos:
                        all_phrase_pos.append(phrase)
            
            result = get_neg_words(s)
            analyzer = SentimentIntensityAnalyzer()
            vs = analyzer.polarity_scores(s)
            if vs['compound']<0:
                for phrase in result:
                    if phrase not in all_phrase_neg:
                        all_phrase_neg.append(phrase)
    
    print("positive words:")
    print(all_phrase_pos)
    print("------------------------------------")
    print("negtive words:")
    print(all_phrase_neg)
