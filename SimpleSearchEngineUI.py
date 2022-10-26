#!/usr/bin/env python3

from SimpleSearchEngine import *
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    if (len(sys.argv) != 1):
        print("Usage: \npython SimpleSearchEngineUI.py\n")
        exit(1)
    print("Section 3.3 Simple Search Engine")
    print("Developed by Wu Dongjun and Jiang Haofeng\n2022/10/24\n--------------------------------------------\n")       
    
    next_or_exit = ""
    while (next_or_exit != "exit"):
        qu = input("Please enter the search query:")
        print("We use the following types as dataset:\n1. Digital_Music\n2. Musical_Instruments")
        typ = input("Please enter 1 or 2 to indicate the dataset you want to search in:")
        while (typ != '1' and typ != '2'):
            print("The input must be 1 or 2.")
            typ = input("Please enter 1 or 2 to indicate the dataset you want to search in:")    
        N = input("Please enter the number of top results you want to view:")
        while not (N.isdigit() and int(N)>=1):
            print("The input must be a positive integer.")
            N = input("Please enter the number of top results you want to view:")
            
        if typ == '1':
            search_engine = SearchEngine(alldocs = products1, field_norm = False)
            query1 = search_engine.query(qu, field_boosts = field_boosts, num_results = int(N))     
        elif typ == '2':
            search_engine = SearchEngine(alldocs = products2, field_norm = False)
            query2 = search_engine.query(qu, field_boosts = field_boosts, num_results = int(N))        
            
        next_or_exit = ""
        while (next_or_exit != "next" and next_or_exit != "exit"):
            next_or_exit = input("Enter 'next' to produce a new search, or enter 'exit' to exit:")       
    print("\nThanks for using!")
    exit(0)        