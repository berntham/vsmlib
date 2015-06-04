from vsmlib.vocabulary import Vocabulary_cooccurrence,Vocabulary_simple,Vocabulary
import vsmlib.matrix
import numpy as np
import scipy
from scipy import sparse
from scipy.spatial.distance import cosine
import scipy.sparse.linalg
import math
import matplotlib as mpl
from matplotlib import pyplot as plt
import os 
import gzip
import brewer2mpl

class Model(object):
    provenance=""
    name = ""
    def load_from_dir(path):
        #try if there is vector.bin
        #if 
        pass

    def get_x_label(self,i):
        return self.vocabulary.get_word_by_id(i)
    def get_most_informative_columns(self,rows,width):
        xdim=rows.shape[1]
        scores=np.zeros(xdim)
        for i in range(rows.shape[0]):
            row = rows[i]/np.linalg.norm(rows[i])
            for j in range(len(row)):
                scores[j]+=row[j]
        scores=abs(scores)
        tops = np.argsort(scores)
        return list(reversed(tops[-width:]))        
    def filter_rows(self,ids_of_interest):
        #return (cooccurrence[1].todense()[:width])
        xdim=self.matrix.shape[1]
        dense=np.empty([0,xdim])
        #dense=np.empty([0,width])
        for i in ids_of_interest:
            if i<0: continue
            if sparse.issparse(self.matrix):
                row=self.matrix[i].todense()
            else:
                row=self.matrix[i]
            row = np.asarray(row)
            row = np.reshape(row,(xdim))
            #dense=np.vstack([dense,row[:width]])
            dense=np.vstack([dense,row])
        return (dense)
    def filter_submatrix(self,lst_words_initial,width):
        words_of_interest=[w for w in lst_words_initial if self.vocabulary.get_id(w)>=0]
        ids_of_interest=[self.vocabulary.get_id(w) for w in words_of_interest]
        rows = self.filter_rows(ids_of_interest)
        xdim=rows.shape[1]
        #max_width = 25
        #width=min(xdim,max_width)
        vert = None # np.empty((rows.shape[0],0))
        cols = self.get_most_informative_columns(rows,width)
        #print (cols)
        for i in cols:
            if vert is None:
                vert = (rows[:,i])
            else:
                vert=np.vstack([vert,rows[:,i]])
        labels=[self.get_x_label(i) for i in cols]
        return rows,vert.T,labels    
    def get_most_similar_vectors(self,u):
        scores=[]
        for i in range(self.matrix.shape[0]):
            scores.append([self.cmp_vectors(u,self.matrix[i]),i])
        scores.sort()
        result=[]
        for q in reversed(scores[-10:]):
            if q[0]>0:
                result.append([q[1],q[0]])
        return result
    def get_most_similar_words(self,w):
        if isinstance(w, str):
            vec= self.matrix[self.vocabulary.get_id(w)]
        else:
            vec=w
        rows = self.get_most_similar_vectors(vec)
        results=[]
        for i in rows:
            results.append([self.vocabulary.get_word_by_id(i[0]),i[1]])
        return results
    def get_row(self,w):
        i = self.vocabulary.get_id(w)
        if i<0: 
            raise Exception('word do not exist', w)
            #return None
        row = self.matrix[i]
        return row
    def cmp_vectors(self,r1,r2):
        if sparse.issparse(r1):
            c= r1.dot(r2.T)/(np.linalg.norm(r1.data)*np.linalg.norm(r2.data))
            c= c[0,0]
            if math.isnan(c): return 0
            return c
        else:
            c= scipy.spatial.distance.cosine(r1,r2)
            if math.isnan(c): return 0
            return 1-c    
    def cmp_rows(self,id1,id2):
        r1=self.matrix[id1]
        r2=self.matrix[id2]
        return self.cmp_vectors(r1,r2)
    def cmp_words(self,w1,w2):
        id1=self.vocabulary.get_id(w1)
        id2=self.vocabulary.get_id(w2)
        if (id1<0) or (id2<0): return 0;
        return self.cmp_rows(id1,id2)
    def load_provenance(self,path):
        try:
            with open (os.path.join(path,"provenance.txt"), "r") as myfile:
                self.provenance = myfile.read() 
        except:
            print("provenance not found")

def normalize(m):
    for i in (range(m.shape[0]-1)):
        norm = np.linalg.norm(m.data[m.indptr[i]:m.indptr[i+1]])
        m.data[m.indptr[i]:m.indptr[i+1]]/=norm

class Model_explicit(Model):
    def __init__(self):
        self.name+="explicit_"
    def load(self,path):
        self.vocabulary = Vocabulary_cooccurrence()
        self.vocabulary.load(path)
        self.name+=os.path.basename(os.path.normpath(path))
        self.matrix = vsmlib.matrix.load_matrix_csr(path,verbose=True)
        try:
            with open (os.path.join(path,"provenance.txt"), "r") as myfile:
                self.provenance = myfile.read()
        except:
            print("warning: provenance not found")
    def clip_negatives(self):
        self.matrix.data.clip(0,out=self.matrix.data)
        self.matrix.eliminate_zeros()
        self.name+="_pos"
        self.provenance+="\ntransform : clip negative"
    def normalize(self):
        normalize(self.matrix)
        self.name+="_normalized"
        self.provenance+="\ntransform : normalize"


class Model_dense(Model):
    def save_to_dir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        #self.matrix.tofile(os.path.join(path,"vectors.bin"))
        np.save(os.path.join(path,"vectors.npy"),self.matrix)
        text_file = open(os.path.join(path,"provenance.txt"), "w")
        text_file.write(self.provenance)
        text_file.close()
        text_file = open(os.path.join(path,"ids"), "w")
        for  i in range(len(self.vocabulary.lst_words)):
            text_file.write("{}\t{}\n".format(self.vocabulary.lst_words[i],i))
        text_file.close()
    def load_from_dir(self,path):
#        self.matrix = np.fromfile(open(os.path.join(path,"vectors.bin")),dtype=np.float32)
        self.matrix = np.load(os.path.join(path,"vectors.npy"))
        self.vocabulary = Vocabulary_simple()
        self.vocabulary.load(path)
        self.name+=os.path.basename(os.path.normpath(path))
    def normalize(self):
        nrm= np.linalg.norm(self.matrix, axis=1)
        self.matrix/=nrm[:, np.newaxis]
        self.name+="_normalized"
        self.provenance+="\ntransform : normalized"


class Model_numbered(Model_dense):
    def get_x_label(self,i):
        return i
    def viz_wordlist(self,wl,colored=False,show_legend=False):
        colors = brewer2mpl.get_map('Set2', 'qualitative', 8).mpl_colors
        cnt=0;
        for i in wl:
            row = self.get_row(i)
            row = row / np.linalg.norm(row)
            if colored:
                plt.bar(range(0,len(row)), row, color = colors[cnt], linewidth  = 0, alpha = 0.6,  label=i)   
            else:
                plt.bar(range(0,len(row)), row, color = "black", linewidth  = 0, alpha = 1/len(wl),  label=i)   
            cnt+=1;
        if show_legend:
            plt.legend()
           
class Model_svd_scipy(Model_numbered):
    def __init__(self,original,cnt_singular_vectors,power):
        ut, s_ev, vt = scipy.sparse.linalg.svds(original.matrix,k=cnt_singular_vectors,which='LM') # LM SM LA SA BE
        self.sigma = s_ev
        sigma_p=np.power(s_ev, power)
        self.matrix =  np.dot(ut,np.diag(sigma_p))    
        self.vocabulary = original.vocabulary
        self.provenance = original.provenance+"\napplied scipy.linal.svd, {} singular vectors, sigma in the power of {}".format(cnt_singular_vectors,power)
        self.name = original.name+"_svd_{}_C{}".format(cnt_singular_vectors,power)

class Model_w2v(Model_numbered):
    @staticmethod
    def load_word(f):
        result=b''
        w=b''
        while w!=b' ':
            w = f.read(1)
            result=result+w
        return result[:-1]
    def load_from_file(self,filename):
        self.vocabulary = Vocabulary()
        f=  open(filename,"rb")
        header = f.readline().split()
        cnt_rows=int(header[0])
        size_row=int(header[1])
        self.name += "w2v_{}".format(size_row)
        self.matrix = np.zeros((cnt_rows,size_row),dtype=np.float32)
        print ("cnt rows = {}, size row = {}".format(cnt_rows,size_row))
        for i in range(cnt_rows):
            word = Model_w2v.load_word(f).decode('ascii',errors="ignore").strip()
            #print (word)
            self.vocabulary.dic_words_ids[word]=i;
            self.vocabulary.lst_words.append(word)
            s_row = f.read(size_row*4)
            row = np.fromstring(s_row, dtype=np.float32)
            #row = row / np.linalg.norm(row)
            self.matrix[i]=row
        f.close()
    def load_from_dir(self,path):
        self.load_from_file(os.path.join(path,"vectors.bin"))
        load_provenance()

class Model_glove(Model_numbered):
    def __init__(self):
        self.name="glove"
    def load_from_file(self,path):
        i=0;
        matr = None
        self.vocabulary = vsmlib.Vocabulary()
        rows=[]
        with gzip.open(path) as f:
            for line in f:
                tokens  = line.split()
                word = tokens[0].decode('ascii',errors="ignore")
                self.vocabulary.dic_words_ids[word]=i;
                self.vocabulary.lst_words.append(word)
                str_vec=tokens[1:]
                #print (str_vec)
                row = np.zeros(len(str_vec),dtype=np.float32)
                for j in range(len(str_vec)) :
                    row[j]=float(str_vec[j])
                rows.append(row)
                i+=1
        self.matrix=np.zeros((len(rows),len(rows[0])),dtype=np.float32)
        self.name+="_{}".format(len(rows[0]))
        for i in (range(len(rows))):
            self.matrix[i]=rows[i]

def load_from_dir(path):
    if os.path.isfile(os.path.join(path,"bigrams.data.bin")):
        print ("this is sparse explicit")
        m =  vsmlib.Model_explicit()
        m.load(path)
        return m
    if os.path.isfile(os.path.join(path,"vectors.bin")):
        print ("this is w2v")
        m =  vsmlib.Model_w2v()
        m.load_from_dir(path)
        return m
    if os.path.isfile(os.path.join(path,"vectors.npy")):
        m =  vsmlib.Model_numbered()
        m.load_from_dir(path)
        print ("this is dense ")
        return m
    files = os.listdir(path)
    for f in files:
        if f.endswith(".gz"):
            m=Model_glove()
            m.load_from_file(os.path.join(path,f))
            m.load_provenance(path)
        print ("this is Glove")
    return m


    print("Ahtung!! can not load anything!")