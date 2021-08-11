# This code is to pull magic number records from EconBiz by their record IDs
# Their IDS are not sequential. Some don't exist. Some don't list language
# And most aren't free. Feelsbadman  

import urllib.request
import json
import os

topdir = '/Users/AYU/Desktop/Capstone/econbiz'


# Start with 20k 
StartingID = 10011574334
EndingID = 10011590000

#Placeholder and Counter. Tells us about error rates, 
# and if we get locked out, where to start

# Counter is number of successful links per run
# Placeholder is current ID 

placeholder = 0
counter = 0

for i in range(StartingID, EndingID):
    recordURL = 'http://api.econbiz.de/v1/record/{}'.format(i)
    try:
        recordmetadata = urllib.request.urlopen(recordURL)
        jsonmetadata = json.loads(recordmetadata.read())
        # Check status, english, access, and links
        if jsonmetadata["status"] == 200:
            try:
                if (jsonmetadata["record"]["language"] == ['eng'] and
                    jsonmetadata["record"]["accessRights"]== 'free'):
                    # Now to select the pdf link
                    urllist = jsonmetadata["record"]["identifier_url"]
                    pdflink = ''
                    for link in urllist:
                        if link[-4:] == '.pdf':
                            pdflink = link
                            break
                    if len(pdflink) > 0:
                        ## need to make new directory here
                        #folder = topdir + '/{}'.format(i)
                        #os.makedirs(folder, exist_ok=True)
                        os.chdir(topdir)
                        urllib.request.urlretrieve(pdflink, "{}.pdf".format(i))
                        urllib.request.urlretrieve(recordURL, "{}metadata.txt".format(i))
                        counter += 1
                        placeholder = i 
                        os.chdir(topdir)
                        tempfile = open('placeholder.txt', 'w')
                        tempfile.write('placeholder: {0}, counter:{1}'.format(placeholder, counter))
                        #print("success {}".format(i))
                        print(counter) 
                    else:
                        pass
                        #print("no link {}".format(i))
                else:
                    pass
                    #print("not english not free {}".format(i))
            except:
                pass
                
                #print("something went wrong with {}".format(i)
    except: 
        pass
        #print("{} does not exist".format(i))
        
        