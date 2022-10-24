# AI6122_G08_Assignment
This is the AI6122 assignment by Group G08.

## 3. Review Summarizer 
### Developed by Jiang Haofeng
There are two files regarding review summarizer, each of which can be run by command line "python [filename].py". (No other arguments, make sure `dataset.py` is in the same directory)

```sh
python summarizer.py
   ```
```sh
python summarizerUI.py
   ```

* `summarizer.py` contains all functions used in review summarizer. The main body will output the example summaries of the 2 products chosen in the report.
* `summarizerUI.py` is an interactive UI for you to play with. You can view review summary of the sampled product in any category you want. You will have 3 input prompts: 
1. The first prompt is the type index. If this is the first time you visit this type, the program will download and initialize dataset for you. Then it will memorize the dataset and you will not have to wait for the dataset initialization for this type afterwards; 
2. The second prompt is the asin number. The program will show the available asin number for you to choose.
3. The third prompt is choosing whether to continue to view other products will exit. Remember once you exit, all the memorized datasets will lost and you have to initialize again when you rerun.

Third party library used:
* NLTK [https://www.nltk.org/index.html]
* NumPy [https://numpy.org/]
