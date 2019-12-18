
# coding: utf-8

# In[111]:
from pprint import pprint

import string,nltk,time,re,os,glob,math,operator,sys
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import *
pattern = r'\w+'
tokenizer = RegexpTokenizer(pattern)
stop_words = set(stopwords.words('english')) 
from Stemmer import Stemmer
stemmer = Stemmer("english")
start = time.time()
block_size = 10000

wts = {'b':40,'t':225,'c':20,'i':30,'r':20,'e':20}
def word_processing(query):
    tokens = re.split(r'[^A-Za-z0-9]+', query) 
    words = [stemmer.stemWord(word) for word in tokens]
    stopped_words = [w for w in words if not w in stop_words]#stop_words
    return stopped_words






search_file = './index/inv_idx/'
fptr = open('./index/other_files/words.txt','r')
search_lines = fptr.readlines()
fptr.close()
fptr = open('./index/other_files/total_count_of_documents.txt','r')
total_docs = fptr.readlines()
fptr.close()
def binary_search(word):
    low = 0;
    high = len(search_lines)-1
    idx = 1
    while low<=high:
        mid = (low+high)//2
        if word>=search_lines[mid]:
            low = mid+1;
        elif word<search_lines[mid]:
            high = mid-1
    fptr.close()
    return low
mapping = ['b','c','e','i','r','t']
fields = ['body:','category:','ext:','infobox:','ref:','title:']
def tf_idf_calculate(word,docs,df,file,tf_idf,proqu,field_type):
    # print(word,field_type)
    flag = 0
    ptr = open(file,'r')
    x = ptr.readline()
    while x:
        w = x.strip().split(' ')
        if w[0]==word:
            # print(len(w))
            idx = -1
            for i in range(1,len(w)):
                if w[i][0]==field_type:
                    idx = i
                    break
            if idx==-1:
                return
            # print(idx)
            docs = w[idx].split(',')
            # print(docs)
            docs[0] = docs[0][2:]
            # print(docs)
            df[word] = len(docs)
            for d in docs:
                doc_cnt = d.split(':')
                doc_id = int(doc_cnt[0])
                cnt_id = int(doc_cnt[1])
                # print(doc_id,cnt_id)
                tf = math.log(cnt_id)+1
                cnt_docs = total_docs[0]
                # print(cnt_docs)
                idf = math.log(int(cnt_docs)/(1+df[word]))
                tf_idf_num = tf*idf
                if not doc_id in tf_idf:
                    tf_idf[doc_id] = {}
                    for j in range(len(proqu)):
                        tf_idf[doc_id][proqu[j]]=0
                tf_idf[doc_id][word]+=tf_idf_num   
            return

        x = ptr.readline()
def execute_query(word,fd,tf_idf,proqu):
    body_mid = binary_search(word)
    docs = []
    df = {}
    file = search_file+str(body_mid)+'.txt'
    tf_idf_calculate(word,docs,df,file,tf_idf,proqu,fd)
def search(type_q,fd1,proqu):
    # print(type_q,fd1,proqu)
    tf_idf = {}#body
    tf_idf1 = {}#title
    tf_idf2 = {}
    tf_idf2['b'] = {}
    tf_idf2['t'] = {}
    tf_idf2['c'] = {}
    tf_idf2['e'] = {}
    tf_idf2['r'] = {}
    tf_idf2['i'] = {}
    cnt = 0
    if type_q==0:
        for word in proqu:
            cnt+=1
            execute_query(word,'b',tf_idf,proqu)
            execute_query(word,'t',tf_idf1,proqu)  


        for x in tf_idf1.keys():#title
            for w in proqu:
                if x in tf_idf.keys():#body
                    if w in tf_idf[x] and w in tf_idf1[x]:
                        # print(w,x,tf_idf[x][w],tf_idf1[x][w])
                        tf_idf[x][w] = wts['b']*tf_idf[x][w]+wts['t']*tf_idf1[x][w]
                    elif w in tf_idf[x]:
                        tf_idf[x][w] = wts['b']*tf_idf[x][w]
                    elif w in tf_idf1[x]:

                        tf_idf[x][w] = wts['t']*tf_idf1[x][w]

        # pprint(tf_idf)
                
        my_dict = {}
        cnt_dict = {}
        for j in tf_idf.keys():
            for q in proqu:
                if j not in my_dict:
                    if q in tf_idf[j]:
                        my_dict[j] = tf_idf[j][q]
                        cnt_dict[j] = 1
                else:
                    if q in tf_idf[j]:
                        cnt_dict[j]+=1
                        my_dict[j] += (tf_idf[j][q])
    else:
        for b in range(len(fd1)):
            cnt=1
            for word in proqu[b]:
                if not word:
                    continue
                execute_query(word,fd1[b],tf_idf2[fd1[b]],proqu[b])
        # pprint(tf_idf2)
        my_dict = {}
        cnt_dict = {}
        for b in range(len(fd1)):
            for j in tf_idf2[fd1[b]].keys():
                for q in proqu[b]:
                    if j not in my_dict:
                        # print(j,wts[fd1[b]])
                        if q in tf_idf2[fd1[b]][j]:
                            my_dict[j] = wts[fd1[b]]*tf_idf2[fd1[b]][j][q]
                            cnt_dict[j] = 1
                    else:
                        if q in tf_idf2[fd1[b]][j]:
                            cnt_dict[j]+=1
                            my_dict[j] += wts[fd1[b]]*tf_idf2[fd1[b]][j][q]

    for key in my_dict:
        my_dict[key]*=(1+cnt_dict[key])
    ans = sorted(my_dict.items(), key=operator.itemgetter(1),reverse = True)
    titles = []
    nu = 0
    for a in ans:
        title_idx = a[0]
        idx = math.ceil(title_idx/block_size)
        file = './index/titles/'+str(idx)+'.txt'
        fptr = open(file,'r')
        x = fptr.readline()
        f = (idx-1)*block_size
        while x:
            f+=1
            if f==title_idx+1:
                title = x.split(' ')
                title = ' '.join(title[:-1])
                print(title)
                nu+=1
                break
            x = fptr.readline()
        if nu == 10:
            break
        fptr.close()
   
while 1:
    print('Enter your query: '+'\n')
    query = input()
    name = []
    field = []
    word = []
    type_q = 0
    start = time.time()
    query = query.lower()
    for j in fields:
        idx = query.find(j)
        if idx!=-1:
            type_q = 1
            q = query.strip().split(j)
            q = q[1].strip().split(' ')
            # print(q)
            string = ""
            for x in q:

                if x in fields:
                    break
                string+=x
                string+=' '
            # print(string)
            words = word_processing(string)
            x = j.split(':')
            field.append(x[0][0])
            word.append(words)
    if type_q==0:
        words = word_processing(query)
        # print(words)
        search(0,'b',words)
    else:
        search(1,field,word)
    end = time.time()
    print(end-start)
    print("\n")


