import os
import re
import numpy as np
import pandas as pd
from langdetect import detect 
from nltk.stem.porter import *
from nltk.corpus import words


# this file attempts to turn latex physics files into clean text format 
# requiring the removal of many latex code elements ($$, {}, /commands) from the latex text to produce 
# a usable text file for NLP

### Hashing an english dictionary for laterchecks
engdict = dict.fromkeys(words.words(), None)
def is_english(word):
    # creation of this dictionary would be done outside of 
    #     the function because you only need to do it once.
    try:
        x = engdict[word]
        return True
    except KeyError:
        return False

### Part 1, make the dictionary among files ###

importpath = '/Users/AYU/Desktop/Capstone/TestBatch1'
exportpath = '/Users/AYU/Desktop/Capstone/TestBatch1/output'
os.chdir(importpath)
filelist = os.listdir()
for m in filelist:
    try:
        os.chdir(importpath)
        f = open(m, 'r', encoding = "utf-8")
        textstring = f.read()
    

# Ok we're gonna manually pair up all of the shit


# Removal of paired dollar signs
        nomath = ''
        areweinmath = False
        for i in range(len(textstring)):
            if textstring[i] == '$':
                if areweinmath == False :
                    areweinmath = True
                elif areweinmath == True:
                    areweinmath = False
            elif areweinmath == False:
                nomath = nomath + textstring[i]

# Removal of Curly Brace contents.
        nomathnocurl = ''
        areweinbrace = False
        for j in range(len(nomath)):
            if nomath[j] == '{':
                areweinbrace = True
            elif nomath[j] == '}':
                    areweinbrace = False
            elif areweinbrace == False:
                nomathnocurl = nomathnocurl + nomath[j]

# Removal of slash commands

        nomathnocurlnoslash = ''
        areweinslash = False
        for k in range(len(nomathnocurl)):
            if nomathnocurl[k] == '\\':
                areweinslash = True
            elif nomathnocurl[k] == '\n':
                areweinslash = False
                nomathnocurlnoslash = nomathnocurlnoslash + ' '
            elif areweinslash == False:
                nomathnocurlnoslash = nomathnocurlnoslash + nomathnocurl[k]


# Removal of non-letter characters
        nonolist = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '?', '"', 
                    ',', '.', '(', ')', '!', '@', '#', '$', '%', '^', '&', '*',
                    "'",'<', '>', '/', '[', ']', ';', '=', '+', '_', '`', '~', 
                    ':', '-', '|']
        onlyletter = ''
        for l in range(len(nomathnocurlnoslash)):
            if nomathnocurlnoslash[l] in nonolist:
                onlyletter = onlyletter + ' '
            else:
                onlyletter = onlyletter + nomathnocurlnoslash[l]
        if detect(onlyletter) == 'en':            
        # Write it out 
                os.chdir(exportpath)
                g = open('clean{}'.format(m), 'w', encoding = "utf-8")
                g.write(onlyletter)
                f.close()
                g.close()
    except:
        print('error with {}'.format(m))
            
os.chdir(exportpath)
#filelist2 = os.listdir()
#cleanlist = list(set(filelist2) - set(filelist))
MasterDict = {}
#IndexDict = {}
os.chdir(exportpath)
for cleanfile in os.listdir():
    if cleanfile.startswith("clean"):
        file = open(cleanfile, 'r')
        filetext = file.read()
        tempstringlist = filetext.split()
        for word in tempstringlist:
            if len(word) > 3 and is_english(word) == True:
                MasterDict[word.lower()] = 0
        file.close()
    
    
wordlist = MasterDict.keys()

stemmer = PorterStemmer()
singles = [stemmer.stem(word) for word in wordlist]
print(len(wordlist))
print(len(list(set(singles))))

StemDict = {}
for word in list(set(singles)):
    StemDict[word] = 0    
        
### Part 2, make td-idf matrices ###

def dictstring(string):
    # This function makes a dictionary of stemmed words for a given string. 
    # Assume that the data has already been cleaned of unwanted symbols and 
    # such. Makes the value of the key the frequency within the document. 
    wordlist = string.split()
    dictionary = {}
    shorterwordlist = []
    for word in wordlist:
        if len(word) > 3 and is_english(word) == True:
            shorterwordlist.append(word.lower())
    stemmer = PorterStemmer()
    stems = [stemmer.stem(word) for word in shorterwordlist]
    for stem in stems:
        if stem.lower() in dictionary:
            dictionary[stem.lower()] = dictionary[stem.lower()] + 1
        else: 
            dictionary[stem.lower()] = 1
    # Keep getting '' string in the dictionary. Just delete it
    return dictionary

def frequencyvector(string, dictionary):
    # Makes a frequency vector of all the words in a string based off of a dictionary 
    # that designates order of the words frequencies in the vector. 
    wordlist = dictstring(string) 
    frequency = []
    # this looping condition is superfluous, but just in case to preserve correct key
    # order. 
    for i in dictionary:
        if i in wordlist: 
            frequency.append(wordlist[i])
        else:
            frequency.append(0)
    return frequency

os.chdir(exportpath)
TDmatrix = []
wordindex = []
fileindex = []
for i in StemDict: 
    wordindex.append(i)
    
for txtfile in os.listdir(): 
    if txtfile.startswith('clean'):
        try:
            cleantext = open(txtfile, 'r')
            tempstring = cleantext.read()
            tempfrequencyvector = frequencyvector(tempstring, StemDict)
            TDmatrix.append(tempfrequencyvector)
            fileindex.append(txtfile[5:])
        except:
            print("freq error with {}".format(txtfile))
        

idf = []
for i in range(0, len(StemDict.keys())):
    counter = 0
    for vector in TDmatrix: 
        if vector[i] > 0: 
            counter = counter + 1
    try:
        idf.append(np.log(len(TDmatrix)/counter)) 
    except:
        print(i)
    
    
tdidf = TDmatrix
for i in range(0, len(StemDict.keys())):
    for j in range(0, len(TDmatrix)):
                   tdidf[j][i] = TDmatrix[j][i] * idf[i]   
# tdidf is written doc x terms, need opposite. 

DocsxTerms  = np.array(tdidf)  
TermsxDocs  = np.transpose(DocsxTerms)             

Umat, smat, Vmat = np.linalg.svd(TermsxDocs)

approxdocumentspace = np.matmul(np.diag(smat), Vmat)
docspaceDF = pd.DataFrame(data = approxdocumentspace, 
                                     columns = fileindex)

def CosineSim(filename, DF):
    # Finds the n (set in function) closest files by cosine similarity within 
    # the document space. Takes Pandas DF doc space and string filename which 
    # designates the column for comparison in the Pandas DF. 
    
    # Note panda is imported as pd. 
    n = 5
    SimDF = pd.DataFrame(columns = ['sim'])
    filelist = list(DF)
    docvector = DF[filename].as_matrix()
    for file in filelist:
        if file != filename: 
            tempvector = DF[file].as_matrix()
            cosinesim = np.dot(docvector, tempvector)\
                            /np.linalg.norm(docvector)\
                            /np.linalg.norm(tempvector)
            SimDF.loc[file] = [cosinesim]
    highest = SimDF.nlargest(n, 'sim')
    return list(highest.index.values)
    
            
                    
            
            
            
            
    
    
    
    
    
    






            
        


        
        
