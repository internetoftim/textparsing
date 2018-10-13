import os
import bs4
from bs4 import BeautifulSoup as soup
import pandas as pd
import spacy
import re
import en_core_web_sm
import keras
import tensorflow
from pathlib import Path
from pathlib import PureWindowsPath
from dateparser.search import search_dates
import arrow
import datetime
nlp = en_core_web_sm.load()


def extract_html(input_html):
    with open(input_html) as inf:
        txt = inf.read()
    soup_out = soup(txt, "html.parser")
#     print(input_html)
    return soup_out

def extract_firm(input_soup):
    temp = input_soup.find(id='article_participants')
    if temp.findAll('a')==[]:
        temp = input_soup.find(id='article_content')
    for element in temp.findAll('a'):
        if element.get('title') != None :
            return(str(element.get('title')))   
        
    return None

def extract_ticker(input_soup):
    temp = input_soup.find(id='article_participants')
    if temp.findAll('a')==[]:
        temp = input_soup.find(id='article_content')
    for element in temp.findAll('a'):
        if element.get('title') != None :
            return(str(element.contents[0].strip()))   
    return None

def extract_time(input_soup):
    temp = input_soup.find(id='article_participants')
    for element in temp.find_all('p'):
        temp_string=element.text.strip()
        try:
            temp_string = re.match(string=temp_string,pattern=\
                       '([a-zA-Z]+\s+[0-9]+,\s+[0-9]{4})[^ 0-9]?(\s+[0-9]{1,2}:[0-9]{2}\s+[APap]\.?[mM]\.?)')
            string1 = temp_string.group(1)
            string2 = temp_string.group(2)
            string3 = string1 + string2
            string3 = re.sub(string=string3,pattern='\.',repl='')
            string3 = re.sub(string=string3,pattern='\s+',repl=' ')
            date_out = arrow.get(string3,'MMMM D, YYYY H:mm A')
        except:
            date_out=None        
            
        if date_out is not None:
            return date_out.isoformat()
    temp = input_soup.find(id='article_content')
    
    for element in temp.find_all('a'):
        temp_string=element.text.strip()
        temp_string = re.sub(string=temp_string,pattern='\s+',repl=' ')
        try:
            while  (element):
                try:
                    date_out = arrow.get(temp_string,'MMMM D, YYYY H:mm A')
                except:
                    date_out=None       
                if date_out is not None:
                    return date_out.isoformat()


                element = element.next_sibling
                temp_string = element
                temp_string = re.sub(string=temp_string,pattern='\s+',repl=' ')  
        except:
            pass
    return None

def extract_quarter(input_soup):
    
    try:
        temp = input_soup.find(id='article_participants')
        for element in temp.findAll('p'):
            if (pd.notnull(element.text) and element.text!=''):
                if( re.search('q[1-4]\s*[0-9]{4}',element.contents[0],flags=re.IGNORECASE)):
                    print(element.contents[0])
                    temp_string = re.match(string=element.contents[0],\
                                           pattern='[^qQ]*([qQ][1-4])\s*[0-9]{4}.*')
                    print(temp_string.group(1))
                    call_title = element.contents[0].split()
                    return temp_string.group(1)
                
        temp = input_soup.find(id='article_source')        
        for element in temp.findAll('a'):
            if (pd.notnull(element.text) and element.text!=''):
                if( re.search('q[1-4]\s*[0-9]{4}',element.contents[0],flags=re.IGNORECASE)):
                    print(element.contents[0])
                    temp_string = re.match(string=element.contents[0],\
                                           pattern='[^qQ]*([qQ][1-4])\s*[0-9]{4}.*')
                    print(temp_string.group(1))
                    call_title = element.contents[0].split()
                    return temp_string.group(1)                
        return None
    except:

        return None
    
def extract_year(input_soup):
    
    try:
        temp = input_soup.find(id='article_participants')
        for element in temp.findAll('p'):
            if (pd.notnull(element.text) and element.text!=''):
                if( re.search('q[1-4]\s*[0-9]{4}',element.contents[0],flags=re.IGNORECASE)):
                    print(element.contents[0])
                    temp_string = re.match(string=element.contents[0],\
                                           pattern='[^qQ]*[qQ][1-4]\s*([0-9]{4}).*')
                    print(temp_string.group(1))
                    call_title = element.contents[0].split()
                    return temp_string.group(1)
                
        temp = input_soup.find(id='article_source')        
        for element in temp.findAll('a'):
            if (pd.notnull(element.text) and element.text!=''):
                if( re.search('q[1-4]\s*[0-9]{4}',element.contents[0],flags=re.IGNORECASE)):
                    print(element.contents[0])
                    temp_string = re.match(string=element.contents[0],\
                                           pattern='[^qQ]*[qQ][1-4]\s*([0-9]{4}).*')
                    print(temp_string.group(1))
                    call_title = element.contents[0].split()
                    return temp_string.group(1)                
        return None
    except:
        return None  
    
def extract_executives(input_soup):
    test_string = []
    temp = input_soup.find(id='article_participants')
    # print(soup_out)
    print_flag = False
    for element in temp.find_all('p'):
        if(re.search('executive',element.text,flags=re.IGNORECASE)):
            #print(element.text.strip(),'###')
            element = element.find_next()
            while  (1):
                element = element.find_next()
                # print(element.contents[0])
                # print(element.text.strip())
                if element.find('strong') or \
                element.find('div'):            
                #print('FOUND')
                    break
                test_string.append(element.text.strip())
        
            break
    return test_string

def extract_name (input_string,delim='-'):
    try:
        if not pd.isnull(input_string):
            name_search = re.search('(^[^-]*)-?[^-]*$', input_string, re.IGNORECASE)
            try:
                return name_search.group(1).strip()
            except:
                return None        
        else:
            return None
    except:
        return None
    
def extract_title (input_string,delim='-'):
    try:
        if not pd.isnull(input_string):
            title_search = re.search('^[^-]*-([^-]*)', input_string, re.IGNORECASE)
            try:
                return title_search.group(1).strip()
            except:
                return None           
            else:
                return None
        else:
            return None
    except:
        return None
def extract_content(input_soup,current_name):
    #     current_name = 'Panna Sharma'
    try:
        if not (pd.isnull(current_name) ):
            temp = input_soup.find(id='article_content')
            test_string = []
            # print(temp)
            for element in temp.find_all('strong'):
                if (re.search(current_name.strip().lower(),element.text,flags=re.IGNORECASE)):
                    while  (1):
                        element = element.find_next()
                        #           print(element.text.strip())
                        if element.find('strong') or \
                        element.find('div'):
                            break
                        test_string.append(element.text.strip())    
            return test_string
        else:
            return None
    except:
        return None

def extract_qanda(input_soup,current_name):
    #     current_name = 'Panna Sharma'
    try:
        if not (pd.isnull(current_name) ):
            temp = input_soup.find(id='article_qanda')
            test_string = []
            # print(temp)
            if temp.find_all('span'):
                for element in temp.find_all('span'):
                    if (re.search(current_name.strip().lower(),element.text,flags=re.IGNORECASE)):
                        while  (1):
                            element = element.find_next()
                            #           print(element.text.strip())
                            if element.find('strong') or \
                            element.find('div') or \
                            element.find('span'):
                                break
                            test_string.append(element.text.strip())    
            else:                
                for element in temp.find_all('strong'):
                    if (re.search(current_name.strip().lower(),element.text,flags=re.IGNORECASE)):
                        while  (1):
                            element = element.find_next()
                            #           print(element.text.strip())
                            if element.find('strong') or \
                            element.find('div') or \
                            element.find('span'):
                                break
                            test_string.append(element.text.strip())      

            return test_string
        else:
            return None
    except:
        return None


def basic_wc(input_text):
    try:
        nlp = en_core_web_sm.load()
        if not (input_text==[]):
            #         decoded_txt=input_text.decode('utf-8')
            sent =  " ".join(str(x) for x in input_text)
            sent = re.sub(pattern='[^a-zA-Z0-9 -]',repl='',string=sent)            
            doc = nlp(sent)
            return doc.__len__()
        else:
            return 0
    except:
        return None
def extract_chunks(input_text):
    try:
        sent =  " ".join(str(x) for x in input_text)
        #     doc = nlp(input_text)
        doc = nlp(sent)
        spans = list(doc.ents)  #+ list(doc.noun_chunks)
        out_list = []
        for span in spans:
            span.merge()
            out_list.append(span)
        return out_list    
    except:
        return None
def extract_name_pair(name, input_text):
    out_list = []
    if not (input_text==[]):
        #         s_out = extract_chunks(input_text)  
        sent =  " ".join(str(x) for x in input_text)
        #     doc = nlp(input_text)
        doc = nlp(sent)        
        #         doc = nlp(input_text)
        spans = list(doc.ents)  #+ list(doc.noun_chunks)

        for item in spans:
            try:
                item = re.sub(pattern='[^a-zA-Z0-9 -]',repl='',string=item.string)            
                if (re.search(item,name,flags=re.IGNORECASE)):
                    out_list.append(item)

            except:
                pass
            
    return out_list

def is_analyst_present(analyst_list):
    if analyst_list: 
        return True
    else: 
        return False
    
def test_analyst(input_soup):
    temp = input_soup.find(id='article_participants')
    for element in temp.findAll('strong'):
        if(re.search('analyst',element.contents[0],flags=re.IGNORECASE)):
            return(True)
    return(None)

def extract_analysts(input_soup):
    temp = input_soup.find(id='article_participants')
    test_string = []
    print_flag = False
    for element in temp.find_all('p'):
        if(re.search('analyst',element.text,flags=re.IGNORECASE)):
            #print(element.text.strip(),'###')
            element = element.find_next()
            while  (1):
                element = element.find_next()
                #print(element.contents[0].strip())
                #print(element.text.strip())
                if element.find('strong') or \
                element.find('div'):
                    #print('FOUND')
                    break
                if (pd.notnull(element.text) and element.text!=''):
                    test_string.append(element.contents[0].strip())    
            break
    return test_string    

import dateparser
def extract_time(input_soup):
    temp = input_soup.find(id='article_participants')
    for element in temp.find_all('p'):
        temp_string=element.text.strip()
        try:
#             December 2, 2014 11:15 AM ET
            temp_string = re.match(string=temp_string,pattern='([a-zA-Z]+\s+[0-9]+,\s+[0-9]{4})[^ 0-9]?(\s+[0-9]{1,2}:[0-9]{2}\s+[APap]\.?[mM]\.?)')
            string1 = temp_string.group(1)
            string2 = temp_string.group(2)
            #         name_search.group(1).strip()
            string3 = string1 + string2
            string3 = re.sub(string=string3,pattern='\.',repl='')
            string3 = re.sub(string=string3,pattern='\s+',repl=' ')
#             print(string1,'##',string2,'##',string3)
            date_out = arrow.get(string3,'MMMM D, YYYY H:mm A')
        except:
            date_out=None        
            
        if date_out is not None:
            return date_out.isoformat()
    temp = input_soup.find(id='article_content')
    
    for element in temp.find_all('a'):
        temp_string=element.text.strip()
        temp_string = re.sub(string=temp_string,pattern='\s+',repl=' ')
        try:
            while  (element):
                try:
                    date_out = arrow.get(temp_string,'MMMM D, YYYY H:mm A')
                except:
                    date_out=None       
                if date_out is not None:
    #                 return temp_string
                    return date_out.isoformat()


                element = element.next_sibling
                temp_string = element
                temp_string = re.sub(string=temp_string,pattern='\s+',repl=' ')  
    #             print(temp_string.find('div'))
    #             print(temp_string.find('strong'))
        except:
            pass
    return None

