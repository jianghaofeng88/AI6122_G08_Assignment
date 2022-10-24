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
    f.write(l + '\n')
  f.close()
  print(f"Data in {typ} is written to a txt file")
  

def products_list(typ):
  '''
  Output a list of dictionaries of a certain product type.
  '''
  
  t,gz = regularize(typ)
  result = []
  for p in parse("./data/"+gz):
    result.append(json.loads(p))
  return result

def product_id(typ):
  '''
  List all the product ids (asin) in this type.
  '''
  l = products_list(typ)
  result = []
  for item in l:
    if item['asin'] not in result:
      result.append(item['asin'])
  return result

def reviewText(typ):
  '''
  List all the rewviews (reviewText) in this type.
  '''
  l = products_list(typ)
  result = []
  for item in l:
    if item['reviewText'] not in result:
      result.append(item['reviewText'])
  return result

def random_200(typ):
  typ,gz = regularize(typ)
  text = products_list(typ)
  random.seed(1000)
  lens = len(text)
  index = random.sample(range(0,lens),200)
  index = sorted(index)
  result = []
  for i in index:
    result.append(text[i])
  # return result
  fileName="./data/"+typ+"_200.txt"
  # f = open("./data/"+typ+"_200.txt", 'w')
  # for i in result:
  #     f.write(i + '\n')
  # f.close()
  with open(fileName,'w') as file:
    for i in result:
      file.write(str(i) + '\n')
  return result
