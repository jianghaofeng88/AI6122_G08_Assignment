0. System setup
We have used a bunch of third party libraries. Make sure these libraries are installed in your environment:
* NLTK [https://www.nltk.org/index.html]
* NumPy [https://numpy.org/]
* pandas [https://pandas.pydata.org/]
* demjson [https://pypi.org/project/demjson/]

How to run:
In CMD or Terminal, all python files can be run by command line "python [filename]" or "python3 [filename]" (No other arguments), depends on devices.

Our core environment file in "dataset.py". Make sure this file is in the same directory as you run any other python files.  You do not need to predownload any data, since every section would automatically download the necessary data for you, and would output the downloading process.
You may see some output regarding [nltk_data], that is to ensure some NLTK functions or data are working, in case they have not been downloaded before.
-----------------------------------------------------------------------

1. Dataset Analysis
Developers: Yang Shunping (coding part) and Chen Zhelong (analysis part)
File: Dataset_Analysis.py

We choose the type Digital_Music and Musical_Instruments as our datasets. The program will output the sentence segmentation, tokenization and top 10 indicative words of each type. You will see some two-row tables. The first row is the number of sentences or tokens in one review; the second row is how many reviews have that many sentences or tokens. 
The outputs yield 6 plots in total. You can find the plots stored in "images" folder after running.
-----------------------------------------------------------------------

2. Simple Search Engine
Developers: Wu Dongjun (function part) and Jiang Haofeng (UI part).
Files: SimpleSearchEngine.py and SimpleSearchEngineUI.py
"SimpleSearchEngine.py" contains all functions used in search engine. The main body will output 2 example queries, one from each dataset.
"SimpleSearchEngineUI.py" is an interactive UI for you to play with. You can search for any queries in our 2 datasets. You will have 4 input prompts: 
1. The first prompt is the query. You can enter anything that you want to search for.
2. The second prompt is the type index. The input should be either 1 or 2.
3. The third prompt is the number of top results you want to view. The input should be a positive integer. After that, the search result will show up shortly.
4. The fourth prompt is choosing whether to continue to produce other searches or exit. Remember once you exit, all the memorized datasets will lost and you have to initialize again when you rerun.
-----------------------------------------------------------------------

3. Review Summarizer 
Developer: Jiang Haofeng
Files: summarizer.py and summarizerUI.py

"summarizer.py" contains all functions used in review summarizer. The main body will output the example summaries of the 2 products chosen in the report.
"summarizerUI.py" is an interactive UI for you to play with. You can view review summary of the sampled product in any category you want. You will have 3 input prompts: 
1. The first prompt is the type index. If this is the first time you visit this type, the program will download and initialize dataset for you. Then it will memorize the dataset and you will not have to wait for the dataset initialization for this type afterwards. Notice that if you want to view the products in the datasets chosen by our group, please enter 21 or 22. 
2. The second prompt is the asin number. The program will show the available asin number for you to choose. After chosing, the review summary will show up shortly.
3. The third prompt is choosing whether to continue to view other products or exit. Remember once you exit, all the memorized datasets will lost and you have to initialize again when you rerun.
-----------------------------------------------------------------------

4. Application