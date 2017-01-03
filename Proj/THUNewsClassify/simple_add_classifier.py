import pickle as pkl
import tensorflow as tf
import copy
import jieba
import numpy as np
import collections
from Proj.THUNewsClassify.THUNews_word2vec import read_text,rm_words
import TextDeal
import math

# 该分类器比较简单，即将单词的embedding相加以后放入神经网络进行线性分类(即单层神经网络)

class SimpleClassifier():
    def __init__(self,
                 label_size,
                 batch_size = None,
                 embed_size = 200,
                 ):
        self.label_size = label_size
        self.batch_size = batch_size
        self.embed_size = embed_size

        self.buildGraph()

        self.sess = tf.Session(graph=self.graph)
        self.sess.run(self.init_op)

    def buildGraph(self):
        self.graph = tf.Graph()
        with self.graph.as_default():
            # train_input , [batch_size * embed_size] 一个batch有多条
            self.train_input = tf.placeholder(tf.float32,shape=[self.batch_size,self.embed_size],name='train_input')
            self.train_label = tf.placeholder(tf.int32,shape=[self.batch_size],name='train_label')
            label_float = tf.cast(self.train_label,tf.float32)

            label_matrix = tf.diag(tf.ones(self.label_size))
            embed_label = tf.nn.embedding_lookup(label_matrix,self.train_label)

            self.weight = tf.Variable(tf.random_normal(shape=[self.label_size,self.embed_size],stddev=1.0/math.sqrt(self.embed_size)))
            self.biase = tf.Variable(tf.zeros([self.label_size]))

            tmp_y = tf.matmul(self.train_input,self.weight,transpose_b=True) + self.biase

            tmp_g = tf.sigmoid(tmp_y) # batch_size * label_size

            self.predict = tf.cast(tf.argmax(tmp_g,axis=1),tf.float32)
            self.error_num = tf.count_nonzero(label_float-self.predict)
            
            self.loss = tf.reduce_mean(-tf.reduce_sum(embed_label*tf.log(tmp_g),axis=1))

            # self.train_op = tf.train.GradientDescentOptimizer(learning_rate=1.0).minimize(self.loss)
            self.train_op = tf.train.AdagradOptimizer(learning_rate=1).minimize(self.loss)
            self.init_op = tf.global_variables_initializer()

def pick_valid_word(word_info_list, dict_size):
    word_info_list.sort(key=lambda x:x['count'],reverse=True)
    word_info_list = word_info_list[:dict_size]
    word2id = {}
    id2word = {}
    for line in word_info_list:
        word = line['word']
        id = line['id']
        word2id[word] = id
        id2word[id] = word
    return word2id,id2word


if __name__=='__main__':
    with open('word_list_path.pkl','rb') as f:
        word_info_list = pkl.load(f)
        word2id,id2word = pick_valid_word(word_info_list,100)
    with open('THUCNews.pkl','rb') as f:
        embedding = pkl.load(f)
    with open('file_info_list.pkl','rb') as f:
        file_info_list = pkl.load(f)
    label_list = []
    for info in file_info_list:
        label = info['label']
        if label not in label_list:
            label_list.append(label)

    label_size = label_list.__len__()
    embed_size = embedding[0].__len__()
    model = SimpleClassifier(label_size=label_size,embed_size=embed_size)
    count = 0
    loss_deque = collections.deque(maxlen=100)
    error_deque = collections.deque(maxlen=100)
    len_deque = collections.deque(maxlen=100)
    print('times\tavg loss\tavg err\tavg len')
    for file_info in file_info_list:
        file_path = file_info['path']
        file_label = file_info['label']
        lines = read_text(file_path)
        context = "".join(lines)
        words = jieba.cut(context,cut_all=False)
        words = rm_words(words)
        word_embed_list = []
        valid_word_list =[]
        for word in words:
            # if (word in word2id):
            if (word in word2id) and (not TextDeal.isStopWord(word)):
                valid_word_list.append(word)
                word_embed_list.append(embedding[word2id[word]])
        print(valid_word_list)
        label_id = label_list.index(file_label)
        context_embed = np.mean(np.array(word_embed_list),axis=0)

        feed_dict = {}
        if np.array([context_embed]).shape.__len__()<2:
            continue
        feed_dict[model.train_input] = np.array([context_embed])
        feed_dict[model.train_label] = np.array([label_id])
        _,loss,err_num = model.sess.run([model.train_op,model.loss,model.error_num],feed_dict=feed_dict)
        loss_deque.append(loss)
        error_deque.append(err_num)
        len_deque.append(word_embed_list.__len__())

        if count%100==0:
            avg_loss = np.mean(loss_deque)
            avg_err = np.mean(error_deque)
            avg_len = np.mean(len_deque)
            print('{a}\t{b}\t{c}\t{d}'.format(a=count,b=avg_loss,c=avg_err,d=avg_len))

        count += 1