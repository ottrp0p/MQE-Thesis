import os
import re
import numpy as np
import pandas as pd
from langdetect import detect 
from nltk.stem.porter import *
from nltk.corpus import words

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

importpath = '/Users/AYU/Desktop/Capstone/econbiz'
exportpath = '/Users/AYU/Desktop/Capstone/econbiz/cleanfiles'
os.chdir(importpath)
filelist = os.listdir()
for document in filelist:
    if document.endswith(".txt"):
        try:
            os.chdir(importpath)
            f = open(document, 'r', encoding = "utf-8", errors='ignore')
            textstring = f.read()
        except: 
            print('error reading {}'.format(document))
    
        try:
    # Removal of non-letter characters
            nonolist = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '?', '"', 
                        ',', '.', '(', ')', '!', '@', '#', '$', '%', '^', '&', '*',
                        "'",'<', '>', '/', '[', ']', ';', '=', '+', '_', '`', '~', 
                        ':', '-', '|', '{', '}', '$']
            onlyletter = ''
            for l in textstring:
                try: 
                    if l in nonolist:
                        onlyletter = onlyletter + ' '
                    else:
                        onlyletter = onlyletter + l
                except:
                    print('error parsing1 {}'.format(document))
        except:
            print('error parsing {}'.format(document))
#            if detect(onlyletter) == 'en':            
            # Write it out 
        try:
            os.chdir(exportpath)
            g = open('clean{}'.format(document), 'w', encoding = "utf-8", errors = 'ignore')
            g.write(onlyletter)
            f.close()
            g.close()
        except:
            print('error writing {}'.format(document))
            
os.chdir(exportpath)
#filelist2 = os.listdir()
#cleanlist = list(set(filelist2) - set(filelist))
MasterDict = {}
#IndexDict = {}
os.chdir(exportpath)
for cleanfile in os.listdir():
    if cleanfile.startswith("clean"):
        file = open(cleanfile, 'r', encoding = "utf -8", errors = 'ignore')
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
            cleantext = open(txtfile, 'r', encoding = 'utf-8')
            tempstring = cleantext.read()
            tempfrequencyvector = frequencyvector(tempstring, StemDict)
            TDmatrix.append(tempfrequencyvector)
            fileindex.append(txtfile[5:-4])
        except:
            pass
            #print("freq error with {}".format(txtfile))
        

idf = []
for i in range(0, len(StemDict.keys())):
    counter = 0
    for vector in TDmatrix: 
        if vector[i] > 0: 
            counter = counter + 1
    try:
        idf.append(np.log(len(TDmatrix)/counter)) 
    except:
        pass
        #print(i)
    
    
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
    print(highest)
    return list(highest.index.values)
    
            
                    
            
            
            
            
    
    
    
    
    
    






            
        


        
        
