import pandas as pd
import random
import gzip
import json
import wget
import re
import string
import math
import os
import nltk
from nltk.tokenize import TreebankWordTokenizer, sent_tokenize
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from nltk.stem.porter import PorterStemmer
from nltk.probability import FreqDist
from collections import Counter

nltk.download('stopwords')

TYPES = ['Books', 'Electronics',
         'Movies and TV',
         'CDs and Vinyl',
         'Clothing, Shoes and Jewelry',
         'Home and Kitchen',
         'Kindle Store',
         'Sports and Outdoors',
         'Cell Phones and Accessories',
         'Health and Personal Care',
         'Toys and Games',
         'Video Games',
         'Tools and Home Improvement',
         'Beauty',
         'Apps for Android',
         'Office Products',
         'Pet Supplies',
         'Automotive',
         'Grocery and Gourmet Food',
         'Patio, Lawn and Garden',
         'Baby',
         'Digital Music',
         'Musical Instruments',
         'Amazon Instant Video']

global dataset200
global asin200
global reviewText200


def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield json.dumps(eval(l))


def regularize(typ):
    """
    Make the input type align with the official gz file name, and also enable using
    index of TYPES (i.e. an integer) to represent the corresponding product type.
    For example, as a function argument, 0, '0' and 'Books' refer to the same type.
    This function just intends to make life easier.
    """

    if type(typ) == int:
        typ = TYPES[typ]
    elif typ.replace('-', '', 1).isdigit():
        typ = TYPES[int(typ)]
    typ = typ.replace(' ', '_')
    typ = typ.replace(',', '')
    gz = "reviews_" + typ + "_5.json.gz"
    return typ, gz


def writefile(typ):
    """
  Download and write the corresponding data for a certain type.
  Both the downloaded gz file and the txt file will be stored in the "data" folder.
  If the current directory does not have "data" folder, it will create one.
  """

    typ, gz = regularize(typ)
    if not os.path.isdir("data"):
        os.mkdir("data")
    if os.path.isfile("data/" + gz):
        print(f"gz file of type {typ} has been already downloaded")
    else:
        print(f"Dowloading data of Type {typ}......")
        URL = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/" + gz
        response = wget.download(URL, "./data")
        print(f"\ngz file of type {typ} is successfully downloaded")

    f = open("./data/" + typ + ".txt", 'w')
    length = 0
    for l in parse("./data/" + gz):
        f.write(l + '\n')
        length += 1
    f.close()
    print(f"Full Data in {typ} is written to a txt file")


def initialize_dataset(typ):
    """
  Output a list of dictionaries of a certain product type.
  """

    t, gz = regularize(typ)
    reviews = []
    asins = []
    for p in parse("./data/" + gz):
        d = json.loads(p)
        reviews.append(d)
        if d['asin'] not in asins:
            asins.append(d['asin'])
    length = len(asins)
    random.seed(1000)
    index = sorted(random.sample(range(0, length), 200))
    global asin200
    asin200 = []
    for i in index:
        asin200.append(asins[i])
    global dataset200
    dataset200 = []
    global reviewText200
    reviewText200 = []
    for review in reviews:
        if review['asin'] in asin200:
            dataset200.append(review)
            reviewText200.append(review['reviewText'])


def products_list():
    return dataset200


def product_id():
    return asin200


def review_text():
    return reviewText200


def list_to_df(l):
    """
    Input a list and return a dataframe
    """
    for i in range(len(l)):
        if i == 0:
            df = pd.DataFrame([l[i]])
        else:
            df = pd.concat([df, pd.DataFrame([l[i]])])
    return df


def write_to_excel(typ, df):
    """
    write into excel file
    """
    df.to_excel('./output/' + typ + '.xlsx', index=False)


def sort_key(s):
    """
    Sort by the number in the string with a regular expression
    """
    if s:
        try:
            c = re.findall('\d+$', s)[0]
        except:
            c = -1
        return int(c)


def review_sentence_segmentation(corpus):
    """
    Do sentence segmentation to a corpus with many reviews
    Return a list, each element in the list is a sentence segmentation for a review
    """
    l = []
    for item in corpus:
        sentences = sent_tokenize(item['reviewText'])
        l.append(sentences)
    return l


def review_tokenization(corpus, punctuation=True):
    """
    Use Treebank Tokenization
    Return a list, each element in the list is a tokenization for a review
    """
    # remove punctuation
    remove = str.maketrans('', '', string.punctuation)
    l = []
    tokenizer = TreebankWordTokenizer()
    for item in corpus:
        if punctuation is False:
            without_punctuation = item['reviewText'].translate(remove)
            tokens = tokenizer.tokenize(without_punctuation)
        else:
            tokens = tokenizer.tokenize(item['reviewText'])
        l.append(tokens)
    return l


def stemming(word):
    """
    Use Porter Stemming
    """
    porter_stemmer = PorterStemmer()
    stemmed_word = porter_stemmer.stem(word)
    return stemmed_word


def review_sentence_distribution(corpus, typ):
    """
    Perform sentence segmentation on the reviews and compare the distribution of the
    two datasets in a single plot.

    The x-axis is the length of a review in number of sentences, and the y-axis is the
    number of reviews of each length.
    """
    title = 'The distribution of two dataset in terms of sentence segmentation'
    x_label = 'The length of a review in number of sentence'
    y_label = 'The number of reviews of each length'
    columns = []
    review_l = review_sentence_segmentation(corpus)
    # list the length of a review in number of sentences
    for item in review_l:
        sentence_length = len(item)
        while str(sentence_length) not in columns:
            columns.append(str(sentence_length))
    columns.sort(key=sort_key, reverse=False)
    df = pd.DataFrame(columns=columns, index=['sentence segmentation'])
    df.fillna(value=0, inplace=True)
    # fill in the number of reviews of each length
    for item in review_l:
        sentence_length = len(item)
        if str(sentence_length) in columns:
            df[str(sentence_length)]['sentence segmentation'] += 1
    print(df)
    plot_info = {'type': typ, 'title': title, 'xlabel': x_label, 'ylabel': y_label}
    return plot_info, df


def review_token_distribution(corpus, typ, punctuation=True):
    """
        Perform tokenization on the reviews and compare the distribution of the
        two datasets in a single plot.

        The x-axis is the length of a review in number of tokens, and the y-axis is the
        number of reviews of each length.
        """
    title = 'The distribution of two dataset in terms of tokenization'
    x_label = 'The length of a review in number of tokens'
    y_label = 'The number of reviews of each length'
    columns = []
    review_l = review_tokenization(corpus, punctuation=punctuation)
    # list the length of a review in number of tokens
    for item in review_l:
        token_length = len(item)
        while str(token_length) not in columns:
            columns.append(str(token_length))
    columns.sort(key=sort_key, reverse=False)
    df = pd.DataFrame(columns=columns, index=['tokenization'])
    df.fillna(value=0, inplace=True)
    # fill in the number of reviews of each length
    for item in review_l:
        token_length = len(item)
        if str(token_length) in columns:
            df[str(token_length)]['tokenization'] += 1
    print(df)
    plot_info = {'type': typ, 'title': title, 'xlabel': x_label, 'ylabel': y_label}
    return plot_info, df


def dataset_uni_token_distribution(corpus, typ, punctuation=True, stem=True, decapitalize=True, zoom=False, x_max=100,
                                   y_max=200):
    """
    At the dataset level, show two distributions to observe the impact of stemming.
    Show two distributions of the data, one without stemming, and the other with stemming.

    The x-axis is the number of unique tokens in a dataset,
    The y-axis is the number of times each token appears in the dataset.
    The tokens shall be sorted by their frequency in your plot.
    """
    words = []
    tokened_reviews = review_tokenization(corpus, punctuation=punctuation)
    for review in tokened_reviews:
        for word in review:
            if decapitalize:
                word.lower()
            if stem:
                words.append(stemming(word))
            else:
                words.append(word)
    fdist = FreqDist(words)
    l = []
    for k, v in fdist.items():
        l.append(v)
    l.sort()
    result = dict(Counter(l))
    if zoom:
        del_l = []
        for i, j in result.items():
            if j > x_max or i > y_max:
                del_l.append(i)
        for el in del_l:
            del result[el]
    x = list(result.values())
    y = list(result.keys())
    plt.scatter(x, y, label='stem=' + str(stem), s=2)
    plt.title('Dataset level unique token distribution (dataset: ' + typ + ' )')
    plt.xlabel('The number of unique tokens in a dataset')
    plt.ylabel('The number of times each token appears in the dataset')
    plt.legend()
    plt.show()


def compare_plot(dfA, dfB, plot_infoA, plot_infoB, zoom=False, xy_max=200):
    """
    Compare two distribution and draw the plot
    """
    xA = dfA.columns.values.tolist()
    yA = dfA.iloc[0].values.tolist()
    xB = dfB.columns.values.tolist()
    yB = dfB.iloc[0].values.tolist()

    xA_num = [int(i) for i in xA]
    xB_num = [int(i) for i in xB]

    if zoom:
        xA_num = xA_num[:xy_max]
        yA = yA[:xy_max]
        xB_num = xB_num[:xy_max]
        yB = yB[:xy_max]
    plt.scatter(xA_num, yA, label=plot_infoA['type'], s=1)
    plt.scatter(xB_num, yB, label=plot_infoB['type'], s=1)
    plt.title(plot_infoA['title'])
    plt.xlabel(plot_infoA['xlabel'])
    plt.ylabel(plot_infoA['ylabel'])
    plt.legend()
    plt.show()


def point_wise_relative_entropy(corpus_l, typ_l, punctuation=True, stop_word=True):
    """
    default: have punctuation, introduce stop words
    Perform pointwise relative entropy and do ranking
    """
    stop_words = stopwords.words('english')
    type_a = typ_l[0]
    type_b = typ_l[1]
    words_list_a = []
    words_list_b = []
    key_list_a = []
    key_list_b = []
    tokened_reviews_a = review_tokenization(corpus_l[0], punctuation=punctuation)
    tokened_reviews_b = review_tokenization(corpus_l[1], punctuation=punctuation)
    # get all words in two datasets
    for review in tokened_reviews_a:
        for word in review:
            if (word in stop_words) and stop_word:
                continue
            else:
                words_list_a.append(word)
    for review in tokened_reviews_b:
        for word in review:
            if (word in stop_words) and stop_word:
                continue
            else:
                words_list_b.append(word)
    # get all unique words and their frequency in two datasets
    u_words_f_dic_a = FreqDist(words_list_a)
    u_words_f_dic_b = FreqDist(words_list_b)
    # get all keys and corresponding values in two datasets
    for k, v in u_words_f_dic_a.items():
        key_list_a.append(k)
    for k, v in u_words_f_dic_b.items():
        key_list_b.append(k)
    # do smoothing in case of zero probabilities
    for key in key_list_a:
        if key not in key_list_b:
            u_words_f_dic_b[key] = 0
    for key in key_list_b:
        if key not in key_list_a:
            u_words_f_dic_a[key] = 0
    for k in u_words_f_dic_a.keys():
        u_words_f_dic_a[k] += 1
    for k in u_words_f_dic_b.keys():
        u_words_f_dic_b[k] += 1
    # calculate point-wise relative entropy
    u_words_e_dic_a = {}
    u_words_e_dic_b = {}
    for k, v in u_words_f_dic_a.items():
        u_words_e_dic_a[k] = v / len(u_words_f_dic_a) * \
                             (math.log(((v / len(u_words_f_dic_a)) / (u_words_f_dic_b[k] / len(u_words_f_dic_b))), 2))
    for k, v in u_words_f_dic_b.items():
        u_words_e_dic_b[k] = v / len(u_words_f_dic_b) * \
                             (math.log(((v / len(u_words_f_dic_b)) / (u_words_f_dic_a[k] / len(u_words_f_dic_a))), 2))
    # sort and get top 10
    a = sorted(u_words_e_dic_a.items(), key=lambda item: item[1], reverse=True)
    b = sorted(u_words_e_dic_b.items(), key=lambda item: item[1], reverse=True)

    return a[:10], b[:10]


if __name__ == "__main__":
    # Type = input("type is: ")
    Type1 = 'Digital Music'
    Type2 = 'Musical Instruments'

    initialize_dataset(Type1)
    sample1 = products_list()
    initialize_dataset(Type2)
    sample2 = products_list()

    plot_info1, df_rtd1 = review_sentence_distribution(sample1, Type1)
    plot_info2, df_rtd2 = review_sentence_distribution(sample2, Type2)
    compare_plot(df_rtd1, df_rtd2, plot_info1, plot_info2)

    plot_info3, df_rtd3 = review_token_distribution(sample1, Type1)
    plot_info4, df_rtd4 = review_token_distribution(sample2, Type2)
    compare_plot(df_rtd3, df_rtd4, plot_info3, plot_info4)

    dataset_uni_token_distribution(sample1, Type1, punctuation=False, stem=False)
    dataset_uni_token_distribution(sample1, Type1, punctuation=False, stem=True)
    dataset_uni_token_distribution(sample2, Type2, punctuation=False, stem=False)
    dataset_uni_token_distribution(sample2, Type2, punctuation=False, stem=True)

    indicative1, indicative2 = point_wise_relative_entropy([sample1, sample2], [Type1, Type2], punctuation=False, stop_word=True)
    print('top 10 indicative words for '+Type1+' are: ', indicative1)
    print('top 10 indicative words for '+Type2+' are: ', indicative2)