
# coding: utf-8

# In[1]:


import xml.etree.ElementTree as ET
import string,nltk,time,re,os
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import *
pattern = r'\w+'
tokenizer = RegexpTokenizer(pattern)
stop_words = set(stopwords.words('english')) 
stemmer = PorterStemmer()
path_to_XML = './wiki_dump.xml-p42567204p42663461'
fname = []


# In[2]:


infobox = {}
ref = {}
links = {}
cat = {}
title = {}
body = {}
Titles = []


# In[3]:


def inverted_index_step2(cnt_word,inverted_index,doc_id):
    for key in cnt_word:            
        if key not in inverted_index:
            inner_dict = {'Id':doc_id,'Cnt':cnt_word[key]}
            inverted_index[key] = []
            inverted_index[key].append(inner_dict)
        else:
            inner_dict = {'Id':cnt,'Cnt':cnt_word[key]}
            inverted_index[key].append(inner_dict)


# In[4]:


def inverted_index_step1(words,cnt_word):
    for key in words:
        if key not in cnt_word:
            cnt_word[key]=1
        else:
            cnt_word[key]+=1


# In[5]:


def word_processing(string):
    tokens = re.findall(r'\w+', string) 
    
    if string is not None:
        tokens = [w.lower() for w in tokens]#lower_case
        stopped_words = [w for w in tokens if not w in stop_words]#stop_words
        stemmed_words = [stemmer.stem(word) for word in stopped_words]
        
        return stemmed_words 


# In[6]:


def references(string,cnt):
    count_words = {}
    visited = {}
    search = "==References=="
    idx = string.find(search)
    if idx==-1:
        return
    vis = 0
    lines = string.splitlines()
    for val in lines:
        if vis:
            if len(val):
                if val[0]=='{' and val[1]=='{':
#                     print(val)
                    words = word_processing(val)
                    inverted_index_step1(words,count_words)

                else:
                    break
            else:
                break
        if val == search:
            vis = 1
    inverted_index_step2(count_words,ref,cnt)


# In[7]:


def external_links(string,cnt):
    count_words = {}
    search = "==External links=="
    idx = string.find(search)
    if idx==-1:
        return
    vis = 0
    lines = string.splitlines()
    for val in lines:
        if vis:
            if len(val):
                if val[0]=='*':
                    words = word_processing(val)
                    inverted_index_step1(words,count_words)
                else:
                    break
            else:
                break
        if val == search:
            vis = 1
    inverted_index_step2(count_words,links,cnt)


# In[8]:


def Infobox(string,cnt):
    count_words = {}
    search = "{{Infobox"
    idx = string.find(search)
    if idx==-1:
        return
    vis = 0
    lines = string.splitlines()
    for val in lines:
        sub = val[0:9]
        if vis:
            if len(val):
                if val[0]=='}' and val[1]=='}':
                    break
                else:
                    ind = val.find("=")
                    ind+=1
                    words = word_processing(val[ind:])
                    inverted_index_step1(words,count_words)
            else:
                break
        if sub == search:
            vis = 1
    inverted_index_step2(count_words,infobox,cnt)


# In[9]:


def category(string,cnt):
    count_words = {}
    categories = re.findall('\[\[Category:(.*?)[\]\]\|]', string)
    for val in categories:
        words = word_processing(val)
        inverted_index_step1(words,count_words)
    inverted_index_step2(count_words,cat,cnt)


# In[10]:


def Body(string,cnt):
    count_words = {}
    lines = string.splitlines()
    for val in lines:
        if len(val):
            words = word_processing(val)
            inverted_index_step1(words,count_words)
    inverted_index_step2(count_words,body,cnt)   


# In[11]:


def write_file(fptr,my_dict):
    for word in sorted(my_dict.keys()):
        fptr.write(word+os.linesep)
        for cur in my_dict[word]:
            id_cnt = str(cur["Id"])+':'+str(cur["Cnt"])
            fptr.write(id_cnt+os.linesep)
            


# In[12]:


def merge(filename,step,fd):
    cnt = 1
    new_file = []
    i = 0
    while True:
        ft = 0
        sd = 0
        if i == len(filename):
            break
        flag = 0
        fn = fd+"_mergestep_"+str(step)
        fn = fn+"_"+str(cnt)+".txt"
        new_file.append(fn)
        fname1 = filename[i]
        i+=1
        if i==len(filename):
            ptr1 = open(fname1,'r')
            ptr2 = open(fn,'w+')
            cnt1 = ptr1.readline()
            while cnt1:
                ptr2.write(cnt1)
                cnt1 = ptr1.readline()
            break
        fname2 = filename[i]
        i+=1
        ptr1 = open(fname1,'r')
        ptr2 = open(fname2,'r')
        ptr3 = open(fn,'w+')
        cnt1 = ptr1.readline()
        cnt2 = ptr2.readline()
        cnt+=1
        while cnt1 and cnt2:
            w1 = cnt1.find(':')
            w2 = cnt2.find(':')
            if w1==-1 and w2==-1:
                if cnt1<cnt2:
                    ptr3.write(cnt1)
                    cnt1 = ptr1.readline()
                    while cnt1.find(':')!=-1:
                        ptr3.write(cnt1)
                        cnt1 = ptr1.readline()
                        if not cnt1:
                            ft = 1
                            break
                elif cnt1>cnt2:
                    ptr3.write(cnt2)
                    cnt2 = ptr2.readline()
                    while cnt2.find(':')!=-1:
                        ptr3.write(cnt2)
                        cnt2 = ptr2.readline()
                        if not cnt2:
                            sd = 1
                            break
                else:
                    ptr3.write(cnt1)
                    cnt1 = ptr1.readline() 
                    while cnt1.find(':')!=-1:
                        ptr3.write(cnt1)
                        cnt1 = ptr1.readline()
                        if not cnt1:
                            ft = 1
                            break
                    cnt2 = ptr2.readline()
                    while cnt2.find(':')!=-1:
                        ptr3.write(cnt2)
                        cnt2 = ptr2.readline()
                        if not cnt2:
                            sd = 1
                            break
            if ft and  sd:
                break
            elif ft and not sd:
                while cnt2:
                    ptr3.write(cnt2)
                    cnt2 = ptr2.readline()
                    if not cnt2:
                        break
            elif sd and not ft:
                while cnt1:
                    ptr3.write(cnt1)
                    cnt1 = ptr1.readline()
                    if not cnt1:
                        break
                       
    return new_file


# In[13]:


start = time.time()
cnt = 0
doc_cnt = 100
block_no = 1
title_num = []
doc_num = []
body_num = []
total_words = 0
body_name = []
title_name = []
category_name = []
info_name = []
ref_name = []
link_name = []
docID = []
for event,elem in ET.iterparse(path_to_XML,events=("start","end"),parser=None):
    if event == 'end':
        tags = elem.tag
        index = tags.find('}')
        index+=1
        tags = tags[index:]
        if tags=='title':
            cnt+=1
#             print(tile)
            count_words = {}
            Titles.append(elem.text)
            words = word_processing(elem.text)
            inverted_index_step1(words,count_words)
            inverted_index_step2(count_words,title,cnt)
            docID.append(cnt)
        elif tags == 'text':
            string = elem.text
            if string is not None:
                 category(string,cnt)
                 references(string,cnt)
                 external_links(string,cnt)
                 Infobox(string,cnt)
                 Body(string,cnt)
        if cnt == block_no*doc_cnt:
#             print(cnt,block_no*doc_cnt)
            sorted(body.keys())
            fname = "./body_invidx_"+str(block_no)+'.txt'
            body_name.append(fname)
            fptr = open(fname,'w+')
            write_file(fptr,body)
            fptr.close()
            fname = "./title_invidx_"+str(block_no)+'.txt'
            title_name.append(fname)
            fptr = open(fname,'w+')
            write_file(fptr,title)
            fptr.close()
            fname = "./category_invidx_"+str(block_no)+'.txt'
            category_name.append(fname)
            fptr = open(fname,'w+')
            write_file(fptr,cat)
            fptr.close()
            fname = "./link_invidx_"+str(block_no)+'.txt'
            link_name.append(fname)
            fptr = open(fname,'w+')
            write_file(fptr,links)
            fptr.close()
            fname = "./ref_invidx_"+str(block_no)+'.txt'
            ref_name.append(fname)
            fptr = open(fname,'w+')
            write_file(fptr,ref)
            fptr.close()
            fname = "./info_invidx_"+str(block_no)+'.txt'
            info_name.append(fname)
            fptr = open(fname,'w+')
            write_file(fptr,infobox)
            fptr.close()
            file_name = './all_titles_'+str(block_no)+'.txt'
            fptr = open(file_name,'w+')
            for i in range(len(Titles)):
                string = str(docID[i])+'$?$'+Titles[i]+'$?$'
                fptr.write(string+os.linesep)
            fptr.close()
            infobox = {}
            ref = {}
            links = {}
            cat = {}
            title = {}
            body = {}
            Titles = []
            title_num = []
            body_num = []
            doc_num = []
            docID = []
            block_no = block_no+1
print(block_no)
if cnt!=block_no*doc_cnt:
    fname = "./body_invidx_"+str(block_no)+'.txt'
    body_name.append(fname)
    fptr = open(fname,'w+')
    write_file(fptr,body)
    fptr.close()
    fname = "./title_invidx_"+str(block_no)+'.txt'
    title_name.append(fname)
    fptr = open(fname,'w+')
    write_file(fptr,title)
    fptr.close()
    fname = "./category_invidx_"+str(block_no)+'.txt'
    category_name.append(fname)
    fptr = open(fname,'w+')
    write_file(fptr,cat)
    fptr.close()
    fname = "./link_invidx_"+str(block_no)+'.txt'
    link_name.append(fname)
    fptr = open(fname,'w+')
    write_file(fptr,links)
    fptr.close()
    fname = "./ref_invidx_"+str(block_no)+'.txt'
    ref_name.append(fname)
    fptr = open(fname,'w+')
    write_file(fptr,ref)
    fptr.close()
    fname = "./info_invidx_"+str(block_no)+'.txt'
    info_name.append(fname)
    fptr = open(fname,'w+')
    write_file(fptr,infobox)
    fptr.close()
    file_name = './all_titles_'+str(block_no)+'.txt'
    fptr = open(file_name,'w+')
    for i in range(len(Titles)):
        string = str(docID[i])+'$?$'+Titles[i]
        fptr.write(string+os.linesep)
    fptr.close()



print(cnt)
print(block_no*doc_cnt)


# In[15]:


def divide_final_index(file,fd):
    f = open(file,'r')
    fname = './'+fd+'_search_'
    block_no = 1
    x = f.readline()
    while x:
        cnt = 1
        fn = fname+str(block_no)+'.txt'
        ptr = open(fn,'w+')
        ans = 0
        fl = 0
        while cnt<=1000:
            if x.find(':')==-1:
                if cnt==1000:
                    scnd = word
                    break
                if fl:
                    ptr.write(word+'$#$'+str(ans)+'\n')
                else:
                    frst = x
                cnt+=1
                ptr.write(x)
                word = x
                ans = 0
                fl = 1
            else:
                ans+=1
                ptr.write(x)
            x = f.readline()
            if not x:
                scnd = word
                break
        ptr.write(frst)
        ptr.write(scnd)
        ptr.close()
        block_no+=1


# In[16]:


def intermediate_merge(file,fd):
    temp_files = []
    temp_files.append(file)
    step = 1
    while 1:
        file = merge(file,step,fd)
        step+=1
        if len(file)==1:
            break
        else:
            temp_files.append(file)
    divide_final_index(file[0],fd)
    for tmp_f in temp_files:
        for tmp in tmp_f:
            os.remove(tmp)
    
intermediate_merge(body_name,'body')
intermediate_merge(title_name,'title')
intermediate_merge(info_name,'infobox')
intermediate_merge(category_name,'category')
intermediate_merge(ref_name,'ref')
intermediate_merge(link_name,'links')

