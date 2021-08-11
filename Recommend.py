#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 16:08:59 2017

@author: AYU
"""
import os
import numpy as np
import pandas as pd
import json
import numpy.random 

DFpath = '/Users/AYU/Desktop/MAE/Capstone/'
metadatapath = '/Users/AYU/Desktop/MAE/Capstone/econbiz/metadata'
articlepath = '/Users/AYU/Desktop/MAE/Capstone/econbiz'

def CosineSim(filename, DF):
    # Finds the n (set in function) closest files by cosine similarity within 
    # the document space. Takes Pandas DF doc space and string filename which 
    # designates the column for comparison in the Pandas DF. 
    
    # Note panda is imported as pd. 
    
    # filname only specifies ID 
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


os.chdir(DFpath)
docspacedf = pd.read_csv('econbizdf.csv', index_col = 0)

def ReadAndRecommend(DF):
    # This function runs the recommendation process, and prompts the user
    # Input is the dataframe of the S*V^t matrix created from SVD
    currentid = ''
    readinglist = []
    IDlist = list(DF.columns.values)
    print('Welcome to ReadAndRecommend')
    print('If there is a specific paper you would like to start with,')
    print('please input the ID.')
    print('If you have no paper, input rand to randomly start with one.')
    while True: 
        Input1 = input('ID or rand: \n')
        if Input1 == 'rand':
            randID = numpy.random.choice(IDlist)
            if randID != currentid:
                currentid = randID
                if currentid not in readinglist:
                    readinglist.append(currentid)
                break
        elif Input1 in IDlist: 
            currentid = Input1
            if currentid not in readinglist:
                    readinglist.append(currentid)
            break
        else: 
            print('error: input not valid \n')
    while True: 
        print('What would you like to do?')
        print('1. Read Abstract')
        print('2. Read Paper Information')
        print('3. Open Paper PDF')
        print('4. Suggest me a new paper based on the current paper')
        print('5. Open another Random paper')
        print('q. Quit')
        Input2 = input('Input a number or quit: \n')
        if Input2 == '1':
            os.chdir(metadatapath)
            tempfile = open(currentid + 'metadata.txt', 'r', encoding='utf-8')
            tempmetadata = json.load(tempfile)
            try:
                print(tempmetadata["record"]["abstract"])
                tempfile.close()
            except: 
                print('Has no abstract. \n')
        elif Input2 == '2':
            os.chdir(metadatapath)
            tempfile = open(currentid + 'metadata.txt', 'r', encoding='utf-8')
            tempmetadata = json.load(tempfile)
            try:
                print('title: {}'.format(tempmetadata["record"]["title"]))
            except: 
                print('No title')
            try:
                print('authors: {}'.format(tempmetadata["record"]["creator"]))
            except:
                print('No author data')
            try:
                print('tags: {} \n'.format(tempmetadata["record"]["subject"]))
            except: 
                print('No tags data \n')
            tempfile.close()
        elif Input2 == '3':
            os.system('open ' + articlepath + '/' + currentid + '.pdf')
        elif Input2 == '4':
            tempfivesuggest = CosineSim(currentid, DF)
            for i in range(len(tempfivesuggest)):
                os.chdir(metadatapath)
                tempfile = open(tempfivesuggest[i] + 
                                'metadata.txt', 'r', encoding='utf-8')
                tempmetadata = json.load(tempfile)
                print('{}. {}'.format(i+1, tempmetadata["record"]["title"]))
                tempfile.close()
            print('Which would you like to read? Input 0 to stay on current paper \n')
            Input3 = input('Number: ')
            if Input3 == '0':
                pass
            if Input3 == '1':
                currentid = tempfivesuggest[0]
                if currentid not in readinglist:
                    readinglist.append(currentid)
            if Input3 == '2':
                currentid = tempfivesuggest[1]
                if currentid not in readinglist:
                    readinglist.append(currentid)
            if Input3 == '3':
                currentid = tempfivesuggest[2]
                if currentid not in readinglist:
                    readinglist.append(currentid)
            if Input3 == '4':
                currentid = tempfivesuggest[3]
                if currentid not in readinglist:
                    readinglist.append(currentid)
            if Input3 == '5':
                currentid = tempfivesuggest[4]
                if currentid not in readinglist:
                    readinglist.append(currentid)
        elif Input2 == '5':
            while True:
                randID = numpy.random.choice(IDlist)
                if randID != currentid:
                    currentid = randID
                    if currentid not in readinglist:
                        readinglist.append(currentid)
                    break
        elif Input2 == 'q':
            break
        else: 
          print('error: input not valid \n')

ReadAndRecommend(docspacedf)   
    
                
        
        
    