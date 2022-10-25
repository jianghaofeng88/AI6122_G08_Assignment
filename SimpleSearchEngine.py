import string
import math
import demjson
import collections

def tokenize_field(field):
    string_field = str(field).lower() #Convert to lowercase
    transtab = str.maketrans('', '', string.punctuation)
    wout_punc_field = string_field.translate(transtab)  #Perform data cleaning
    return list(filter(None, wout_punc_field.split()))    #Returns the filtered split string

def idf(doc_count, inverted_index, term):
    if inverted_index.get(term):
        return math.log(doc_count / len(inverted_index[term]) + 1) + 1
    else:
        return 0

def get_inverted_index(alldocs):
    inverted_index = collections.defaultdict(set)
    for index, docnum in enumerate(alldocs):
        for field, fieldnum in docnum.items():
            for termnum in set(tokenize_field(fieldnum)):
                inverted_index[termnum].add(index)
    return inverted_index

def get_vector_norm(vector):    #normalization of vectors
    return math.sqrt(sum(value['score'] ** 2 for value in vector.values()))

def get_query_vector(doc_count, inverted_index, tokenized_query):   #make the vector of query
    return {term: {'score': idf(doc_count, inverted_index, term)} for term in tokenized_query}

def get_weight_doc(docnum, doc_count, inverted_index, field_norm):    #assign weight to each file
    term_weight_docs = dict()
    for field, fieldnum in docnum.items():
        term_weight_docs[field] = {}
        field_len = len(str(fieldnum))
        term = tokenize_field(fieldnum)
        for termnum in set(term):
            TF = math.sqrt(term.count(termnum))
            IDF = idf(doc_count, inverted_index, termnum)
            weight = TF * IDF * (1 / math.sqrt(field_len) if field_norm else 1)
            term_weight_docs[field][termnum] = weight
    return term_weight_docs

def get_doc_vectors(alldocs, doc_count, inverted_index, tokenized_query):   #make the vector of document
    doc_vectors = dict()
    for doc_index, doc in alldocs.items():
        doc_term_scores = dict()
        for field, terms in doc['weights'].items():
            for term, score in terms.items():
                if term in tokenized_query and score > doc_term_scores.get(term, {}).get('score', 0):
                    field_text = doc['doc'][field]
                    fieldall = doc['doc']
                    term_score = {'field_name': field, 'field_text': field_text,'score': score, 'fieldall': fieldall}
                    doc_term_scores[term] = term_score  #match
        if doc_term_scores:
            doc_vectors[doc_index] = doc_term_scores
    return doc_vectors

def get_ranking_list(alldocs, num_terms_in_query, query_vector, doc_vectors, num_results, field_boosts):  #ranking module
    ranking_list = []
    query_vector_norm = get_vector_norm(query_vector)
    for doc_index, doc_vector in doc_vectors.items():
        dot_product = matching_terms = 0
        for query_term, query_score in query_vector.items():
            if query_term in doc_vector:
                field_name = doc_vector[query_term]['field_name']
                field_boost = field_boosts.get(field_name, 1)
                dot_product += query_score['score'] ** field_boost * doc_vector[query_term]['score']
                matching_terms += 1
        dot_product = dot_product * (matching_terms / num_terms_in_query)
        doc_vector_norm = get_vector_norm(doc_vector)
        dot_product = dot_product / (query_vector_norm * doc_vector_norm)
        field_matches = dict()
        for value in doc_vector.values():
            field_matches[value['field_name']] = value['field_text']
        ranking_list.append({'doc_index': doc_index, 'ranking': round(dot_product, 4), 'field_name': field_name, 'field_matches': field_matches, 'terms': ', '.join(doc_vector.keys()), 'doc': doc_vector})
    ranking_list = sorted(ranking_list, key = lambda x: x['ranking'], reverse = True)
    if num_results:
        return ranking_list[:num_results]
    else:
        return ranking_list

class SearchEngine: #core module
    def __init__(self, alldocs, field_norm=False):    #init
        self.field_norm = field_norm
        self.doc_count = len(alldocs)
        self.create_inverted_index(alldocs)
        self.index_documents(alldocs)

    def create_inverted_index(self, alldocs):
        self.inverted_index = get_inverted_index(alldocs)

    def index_documents(self, alldocs): #make index for documents
        doc_index = dict()
        for index, docnum in enumerate(alldocs):
            doc_index[index] = {'doc': docnum, 'weights': get_weight_doc(docnum, self.doc_count, self.inverted_index, self.field_norm)}
        self.alldocs = doc_index

    def query(self, phrase, num_results=10, field_boosts={}): #query module
        self.phrase = phrase
        self.field_boosts = field_boosts
        tokenized_query = set(tokenize_field(phrase))
        num_terms_in_query = len(tokenized_query)
        self.query_vector = get_query_vector(self.doc_count, self.inverted_index, tokenized_query)
        self.doc_vectors = get_doc_vectors(self.alldocs, self.doc_count, self.inverted_index, tokenized_query)
        self.ranking_list = get_ranking_list(self.alldocs, num_terms_in_query, self.query_vector, self.doc_vectors, num_results, self.field_boosts)
        return self.print()

    def print(self):    #printout module
        print('Query: ' + self.phrase)
        print('Search Results')
        print('------------------------------------------------')
        print('{0:<7} {1:<7} {2:<5} {3:<30}'.format('Ranking', 'Score', 'Index', 'Terms'))
        for ranking_positition, doc in enumerate(self.ranking_list, 1):
            print('{0:<7} {1:<7} {2:<5} {3:<30}'.format(ranking_positition, doc['ranking'], doc['doc_index'], doc['terms']))
            field_matches = '.\n'.join(['{} - {}'.format(key, value) for key, value in doc['field_matches'].items()])
            print(field_matches)
            print()
            print(doc['doc'])
            print('------------------------------------------------')

#json document, need to add ',' between '}' and '{' in assignment json style.
#add '[' at the beginning and ']' at the end.
#demjson for recognizing abnormal json files which use '' rather than "" to represent fieldects and attributes.
products1 = demjson.decode_file('Digital Music_200.json', encoding = 'utf-8')
products2 = demjson.decode_file('Musical Instruments_200.json', encoding = 'utf-8')
field_boosts = {'title': 1.1}
search_engine = SearchEngine(alldocs = products1, field_norm = False)
query1 = search_engine.query("tree, jazz, cd", field_boosts = field_boosts, num_results = 10)
search_engine = SearchEngine(alldocs = products2, field_norm = False)
query2 = search_engine.query("piano, guitar", field_boosts = field_boosts, num_results = 10)
#10 results together
