import spacy
import nltk
import re
import numpy as np
import gensim
import pandas as pd
from tabula import read_pdf
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

nltk.download('stopwords')
stopwords1 = set(nltk.corpus.stopwords.words('english'))
ldamod = gensim.models.ldamodel.LdaModel.load('LDAModel/GeoTrackerLDA')

tagger_html= '''
<html>
<head>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<title> CAR WEB Application </title>
<h1> Web Application for CAR Analytics Capability Demo</h1>
<table>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr><td><h4> Upload Document</h4></td></tr>
<tr><td>
<form method="POST" enctype="multipart/form-data">
  <input type="file" id="myFile" name="file">
  <input type="submit">
</form>
</td></tr>

</table>
<!-- This is a comment -->
<div id="logo"> 
	<img src="{{ url_for('static', filename='ghd-logo.jpg') }}"> 
</div>
</html>
<div id="HOME"> 
<form method="post">
<input type="submit" value="HOME" name="home"/>
</form>
</div>
'''






def prepare_corpus_from_docs(doc_list):
  '''Method to clean text and generate Corpus for Topic Modelling
  Parameters
  doc_list : (list) List of Raw texts(Documents)
  Returns :
  Corpus : (list) List of Lists of Tokens(Keywords)'''

  if not(isinstance(doc_list,list)): # Handling Wrong Datatypes
    raise TypeError('Expecting List Type for doc_list but passes {}'.format(type(doc_list)))
    
  nlp = spacy.load('en_core_web_sm') # Loading Spacy NLP Model
  nlp.max_length = 3229999
    
  def get_doc_corpus(txt):
    '''Method to clean Raw Text based on SPACY NLP Pipeline
    Parameters:
    txt : (String) Raw Text
    Returns :
    corpus : (list) List of Token (Keywords)'''
    
    flags = ['CCONJ','PROPN','PUNCT','NUM','DET'] # Parts of Speech token to be filtered out
    doc = nlp(txt,disable=['ner']) # Creating Spacy Document Object
    corpus = [k.lemma_ for k in doc if (not(k.pos_ in flags) and (not(k.lemma_ in stopwords1)))] # POS Filter,Removing Stopwords & Lemmatizing Words
    corpus = [k for k in corpus if (k.isalpha() or k.isalnum())] # Filtering out Non-Alphabet and Non-Alphanumeric words 
    corpus = [k for k in corpus if (len(k)>=2)] # Filtering out Null Strings and Single letters
    return corpus
  Corpus = [] # List to store Corpus
  try:
    #==========Generating Corpus for each Document=========================#
    with ThreadPoolExecutor(max_workers=8) as f:
      Corpus = list(f.map(get_doc_corpus,doc_list))
    #=======================================================================#
    
    #=======N-Gram Tokenizaton of Documents==================================#
    bigram_model = gensim.models.Phrases(Corpus,min_count=5,threshold=100) # 
    with ThreadPoolExecutor(max_workers=8) as f:
      Corpus = list(f.map(lambda X : bigram_model[X] ,Corpus))
    #=========================================================================#
  except Exception as e:
    print(e.__str__())
  
  return Corpus


def get_topics(txt):
    corpus = prepare_corpus_from_docs([txt])
    bow = [ldamod.id2word.doc2bow(doc) for doc in corpus]
    topics = sorted(ldamod[bow[0]][0],key = lambda X : X[1],reverse=True)
    tnums = [t[0] for t in topics[:5]]
    twords = map(lambda X : ','.join([ldamod.id2word[x[0]] for x in ldamod.get_topic_terms(X)]),tnums)
    return pd.DataFrame(list(zip(tnums,twords)),columns=['Topic_Num','Topic Words'])


def readtables(path):
    
    '''Method to Extarct Monitoring well Tables'''
    def get_tag(st):
        tag = 'Generic'
        cols = st.to_string().lower()
      #pattern_old = '\(\w{1,2}/\w{1,2}\)'   
        units = re.findall('\(\w{1,2}/(Kg|kg|l|L|m3|cm3)\)',cols)
        if (len(units)!=0):
            tag = 'Analytical Results Table'
        if ('screen interval' in cols):
            tag = 'Screen Interval Assessment Table'
        if ('introduction' in cols):
            tag = 'Table of Contents'
        if (('database' in cols) and ('property' in cols)) :
            tag = 'Database Search Tables'
    #       elif (('drilling' in cols) and ('method' in cols) and ('graphic' in cols) and ('log' in cols)):
    #         tag = 'Boring Log'
        if ((re.search(r'graphic', cols, re.I)!=None) &\
      (re.search(r'\bblows?\b', cols, re.I)!=None) &\
      (re.search(r'Description|litholog', cols, re.I)!=None) &\
      (re.search(r'U\.?S\.?C\.?S\.?', cols, re.I)!=None) &\
      (re.search(r'\bclaye?y?\b|\bsilty?\b|\bgravel|\bsandy?\b', cols, re.I)!=None)):
            tag = 'Boring Log'
        if ((re.search(r'borehole', cols, re.I)!=None) &\
      (re.search(r'boring', cols, re.I)!=None)&\
      (re.search(r'installation', cols, re.I)!=None)&\
      (re.search(r'casing', cols, re.I)!=None)&
      (re.search(r'diameter', cols, re.I)!=None)&\
      (re.search(r'elevation', cols, re.I)!=None)&\
      (re.search(r'depth', cols, re.I)!=None)&\
      (re.search(r'screen', cols, re.I)!=None)):
            tag = 'Well Construction Details'
        if ((re.search(r'hourmeter', cols, re.I)!=None) &\
      (re.search(r'influent', cols, re.I)!=None)&\
      (re.search(r'FID', cols, re.I)!=None)&\
      (re.search(r'effluent', cols, re.I)!=None)&
      (re.search(r'vapor', cols, re.I)!=None)&\
      (re.search(r'efficiency', cols, re.I)!=None)&\
      (re.search(r'emission', cols, re.I)!=None)):
            tag = 'Soil Vapor Operating Data'
            
        if ((re.search(r'hourmeter', cols, re.I)!=None) &\
      (re.search(r'influent', cols, re.I)!=None)&\
      (re.search(r'FID', cols, re.I)!=None)&\
      (re.search(r'benzene', cols, re.I)!=None)&
      (re.search(r'toluene', cols, re.I)!=None)&\
      (re.search(r'Ethylbenzene', cols, re.I)!=None)&\
      (re.search(r'removal', cols, re.I)!=None)&\
      (re.search(r'GRO', cols, re.I)!=None)&\
      (re.search(r'ppmv', cols, re.I)!=None)):
            tag = 'Soil Vapor Analytical Data'
       
        if ((re.search(r'hourmeter', cols, re.I)!=None) &\
      (re.search(r'effluent', cols, re.I)!=None)&\
      (re.search(r'FID', cols, re.I)!=None)&\
      (re.search(r'benzene', cols, re.I)!=None)&
      (re.search(r'toluene', cols, re.I)!=None)&\
      (re.search(r'Ethylbenzene', cols, re.I)!=None)&\
      (re.search(r'emission', cols, re.I)!=None)&\
      (re.search(r'GRO', cols, re.I)!=None)&\
      (re.search(r'ppmv', cols, re.I)!=None)):
            tag = 'Soil Vapor Analytical Data'
            
        if ((re.search(r'sample', cols, re.I)!=None) &\
      (re.search(r'location', cols, re.I)!=None)&\
      (re.search(r'depth', cols, re.I)!=None)&\
      (re.search(r'diesel', cols, re.I)!=None)&\
      (re.search(r'purgeable', cols, re.I)!=None)&\
      (re.search(r'aromatics', cols, re.I)!=None)):
            tag = 'Soil Analytical Results'
        return tag

    tables = read_pdf(path, pages='all', guess=False, silent=True)
    tags = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        tags = list(executor.map(lambda X : get_tag(X),tables))
    tags = sorted(list(set(tags)))
    return pd.DataFrame({'Table Type':tags})

def get_TOC(pdfpath):
    '''Method to Retrive Table of Contents
    Parameters:
    self : Instance of ExtractFeatures Class (Implicitly Passed)
    Returns:
    toc : Table of Contents (Pandas DataFrame)
    hierarchy : TOC Hierarchy (Dictionary) '''
    #=====Inner Methods=============#
    def clean_str(X):
      '''Method to retrive Section,TOC, Page Number
        Parameters X: Pandas Series (Dataframe Row)
        returns :
        TOC : String
        SEC : Section
        PG : Page Number'''
      try:
        i1,i2 = None,None # Starting and ending indices for TOC String
        grps = re.findall('[a-z,A-Z]',X['TOC']) # Extracting Letters
        i1 = (X['TOC'].lower().index(grps[0].lower())) # Exatracting index of First Letter
        i2 = (X['TOC'].lower().rfind(grps[-1].lower()))# Exatracting index of Last Letter
        _toc,_sec,_pgnum = X['TOC'][i1:(i2+1)],X['TOC'][:i1].strip(),re.findall(r'\d+',X['TOC'][(i2+1):])[0] # TOC,Section,Page Number
        _ss = X['TOC'][:(i2+1)] # Search String
        return [_toc,_sec,_pgnum,_ss]
      except Exception as e:
        return [np.nan,np.nan,np.nan,np.nan]
 
    def group_toc(X):
      '''Method to Group Main Section with subsection'''
      X = X.copy(deep=True)
      X['Digits'] = X['SECTION'].apply(lambda x : x.split('.')[0])
      X = X.groupby('Digits').agg({'TOC':'unique'})
      X = {k[0]:k[1:] for k in list(X['TOC'].values)}
      return X
          
    #=====End of Inner Methods=============#
 
    toc = pd.DataFrame() # DataFrame Object to Strore Table of Contents TOC
    try:
      toc = read_pdf(pdfpath,pages=list(range(2,16)),pandas_options={'header':None},guess=False) # Reading pages 2 to 15 of PDF Document
      if len(toc)>1:
        toc = pd.concat(toc,axis=0,ignore_index=True,join='outer') # Concatenate Dataframes if Table of Contents Spans Multiple Pages
      elif len(toc)==1:
        toc = toc[0] # Selecting Table of contents that spans single page
      else:
        toc = pd.DataFrame() # Empty Dataframe if Table of Contents is not found or could not Parse
        
      toc['TOC'] = pd.Series(toc.fillna('').values.tolist()).map(lambda x: ''.join(map(str,x))) # Concatenating all Columns of Retrived Dataframes
      #toc = toc[toc.TOC.str.contains(r'^\d')] # Regex to Filter Rows that Starts with Digit
      toc = toc[toc.TOC.str.contains(r'\d+$')] # Regex to Flter Rows that Ends with Digit
      #toc = toc[~toc.TOC.str.contains(r'^\d(\d){2,5}')] # Regex to Filter Rows with More that 3 Digits at beginning of String
      toc = toc[['TOC']]
      toc = toc.apply(clean_str,axis=1) # Calling clean_str method for all rows to clean string 
      toc = pd.DataFrame(list(toc),columns=['TOC','SECTION','PAGE NUMBER','SEARCH STRING'])
      toc = toc.drop_duplicates('TOC') # Drop Duplicate Rows
      toc = toc.dropna()
      toc = toc[toc['TOC'].apply(lambda X : X[0].isupper())]
      start,hierarchy=None,None
      try:
        start = (np.min(np.where(toc.TOC.str.contains(r'introduction|summary',regex=True,flags=re.IGNORECASE))))
        toc = toc.iloc[start:,:]
        toc = toc[toc['PAGE NUMBER'].astype(int)<100]
        hierarchy = group_toc(toc)
      except:
        toc = pd.DataFrame()
          
    except Exception as e:
      return pd.DataFrame(),{}
    return toc,hierarchy
