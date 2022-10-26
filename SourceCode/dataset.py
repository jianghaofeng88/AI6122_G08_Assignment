#!/usr/bin/env python3

import json
import gzip
import wget
import random
import os

TYPES = ['Books','Electronics',
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
  '''
  Make the input type align with the offcial gz file name, and also enable using
  index of TYPES (i.e. an integer) to represent the corresponding product type.
  For example, as a function argument, 0, '0' and 'Books' refer to the same type.
  This funciton just intends to make life easier.
  '''
  
  if (type(typ)==int):
    typ = TYPES[typ]
  elif (typ.replace('-','',1).isdigit()):
    typ = TYPES[int(typ)]
  typ = typ.replace(' ','_')
  typ = typ.replace(',','')
  gz = "reviews_"+typ+"_5.json.gz"
  return typ,gz
  

def writefile(typ):
  '''
  Download and write the corresponding data for a certain type.
  Both the downloaded gz file and the txt file will be stored in the "data" folder.
  If the current directory does not have "data" folder, it will create one.
  '''
  
  typ,gz = regularize(typ)
  if (not os.path.isdir("data")):
    os.mkdir("data")
  if (os.path.isfile("data/"+gz)):
    print(f"gz file of type {typ} has been already downloaded")
  else:
    print(f"Dowloading data of Type {typ}......")
    URL = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/"+gz
    response = wget.download(URL, "./data")
    print(f"\ngz file of type {typ} is successfully downloaded")

  f = open("./data/"+typ+".txt", 'w')
  for l in parse("./data/"+gz):
    f.write(l + ',\n')
  f.close()
  print(f"Full Data in {typ} is written to a txt file")
    
    

def initialize_dataset(typ):
  '''
  Initialize the dataset.
  Use random seed = 1000 to sample 200 products. Generate the dataset, asin list
  and review text list.
  '''
  
  t,gz = regularize(typ)
  reviews = []
  asins = []
  for p in parse("./data/"+gz):
    d = json.loads(p)
    reviews.append(d)
    if d['asin'] not in asins:
      asins.append(d['asin'])
  length = len(asins)
  random.seed(1000)
  index = sorted(random.sample(range(0,length),200))
  global asin200
  asin200 = []
  for i in index:
    asin200.append(asins[i])
  global dataset200
  dataset200=[]
  global reviewText200
  reviewText200 = []
  
  for review in reviews:
    if review['asin'] in asin200:
      dataset200.append(review)
      reviewText200.append(review['reviewText'])


def writefile_200(typ):
  '''
  Write the sampled dataset to a txt file.
  '''
  
  typ,gz = regularize(typ)
  initialize_dataset(typ)
  f = open("./data/"+typ+"_200.txt", 'w')
  f.write('[')
  for l in parse("./data/"+gz):
    for i in asin200:
      if i in l:
        f.write(l + ',\n')
  f.write(']')
  f.close()  
    

def products_list():
  return dataset200

def product_id():
  return asin200

def review_text():
  return reviewText200

