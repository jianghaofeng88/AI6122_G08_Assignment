#!/usr/bin/env python3

from sentiment import *
import sys
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    if (len(sys.argv) != 1):
        print("Usage: \npython sentimentUI.py\n")
        exit(1)
    print("--------------------------------------------\nSection 3.5 Application - Sentiment Analysis")
    print("Developed by Cao Yifei and Jiang Haofeng\n2022/10/25\n--------------------------------------------\n")       
    
    next_or_exit = ""
    known_types = [0]*3
    while (next_or_exit != "exit"):
        print("We use the following types as dataset:\n1. Digital_Music\n2. Musical_Instruments")
        t = input("Please enter 1 or 2 to indicate the dataset you want to use:")
        while (t != '1' and t != '2'):
            print("The input must be 1 or 2.")
            t = input("Please enter 1 or 2 to indicate the dataset you want to use:")
        typ = int(t)+20
        if known_types[int(t)] == 0:
            writefile(typ)
            print(f"Initializing dataset for {regularize(typ)[0]}......")
            initialize_dataset(typ)
            print(f"Initializing dataset for {regularize(typ)[0]} is successful.\n--------------------------------------------\n")
            get_global_values()
            rank = ranking_of_products()
            known_types[int(t)] = (products_list(), product_id(), review_text(), rank)
        else:
            set_global_values(known_types[int(t)][0], known_types[int(t)][1], known_types[int(t)][2])        
        print(f"The sentiment analysis rank in type {regularize(typ)[0]} is as follows:")
        for i in known_types[int(t)][3]:
            print(i[0],'%.4f'%i[1])      
        print("------------------------------------")  
        
        
        l=known_types[int(t)][1]
        i = input(f"Please choose the product id that you want to view the positive and negative words (e.g. {l[0]}, {l[1]}):")
        while not (i in l):
            print("The asin must be in the above list")
            i = input(f"Please choose the product id that you want to view the positive and negative words (e.g. {l[0]}, {l[1]}):")        
        
        texts = get_review_by_id(i)
        v = []
        all_phrase_pos = []
        all_phrase_neg = []
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
        print("\n")
        
        
        
        
               
            
        next_or_exit = ""
        while (next_or_exit != "next" and next_or_exit != "exit"):
            next_or_exit = input("Enter 'next' to view other products, or enter 'exit' to exit:")       
    print("\nThanks for using!")
    exit(0)        