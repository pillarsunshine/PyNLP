import pickle as pkl
# import tensorflow as tf
import copy
import jieba
import numpy as np
import collections
from Proj.THUNewsClassify.util import read_text, \
    rm_words,pick_valid_word,pick_valid_word_chisquare,gen_balance_samples
import TextDeal
import math
from pprint import pprint
import matplotlib.pyplot as plt
import random
from collections import Counter
import pickle as pkl
from sklearn.ensemble import  AdaBoostClassifier,GradientBoostingClassifier,ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier


if __name__=='__main__':
    # dict_size = 50000
    # valid_chi_size = 5000 ;
    # with open('word_list_path_with_docfreq.pkl','rb') as f:
    #     word_info_list = pkl.load(f)
    #     # word2id,id2word = pick_valid_word(word_info_list,50000)
    #     full_word2id = dict(zip([x['word'] for x in word_info_list],[x['id'] for x in word_info_list]))
    #     word2id,id2word = pick_valid_word_chisquare(word_info_list,dict_size=valid_chi_size,s1_size=dict_size)
    # with open('THUCNews.pkl','rb') as f:
    #     embedding = pkl.load(f)
    # with open('file_info_list.pkl','rb') as f:
    #     file_info_list = pkl.load(f)
    #     file_full_nums = len(file_info_list)
    # label_list = []
    # for info in file_info_list:
    #     label = info['label']
    #     if label not in label_list:
    #         label_list.append(label)
    #
    # # 根据 单词的 tf 和 idf 来计算每个单词的权重
    # weights = np.zeros([dict_size])
    # for word in word2id:
    #     word_info = word_info_list[full_word2id[word]]
    #     part_tf = 1.0/word_info['count']
    #     if 'doc_freq' in word_info:
    #         part_idf =  math.log(file_full_nums/word_info['doc_freq'])
    #     else:
    #         part_idf = math.log(file_full_nums/word_info['count'])
    #     weights[word2id[word]] = part_tf * part_idf
    #
    # balanced_info_list = gen_balance_samples(file_info_list,label_list,balance_index=5)
    # file_info_list = balanced_info_list
    #
    # file_info_num = len(file_info_list)
    #
    # file_vec_list = []
    # label_name_list = []
    #
    # for i,sample in enumerate(balanced_info_list):
    #     lines = read_text(sample['path'])
    #     context = "".join(lines)
    #     words = jieba.cut(context,cut_all=False)
    #     words = rm_words(words)
    #     word_embed_list = []
    #     valid_count = 0
    #     weight_sum = 0
    #     for word in words:
    #         # if (word in word2id):
    #         if (word in word2id) and (not TextDeal.isStopWord(word)):
    #             word_embed_list.append(embedding[word2id[word]])
    #             # w = weights[word2id[word]]
    #             # weight_sum += w
    #             # word_embed_list.append(w*embedding[word2id[word]])
    #             valid_count += 1
    #     if valid_count>0:
    #         context_embed = np.mean(np.array(word_embed_list),axis=0)
    #         # context_embed = np.sum(np.array(word_embed_list),axis=0)/weight_sum
    #         file_vec_list.append(context_embed)
    #         label_name_list.append(sample['label'])
    #     if i%1000==0:
    #         print(i)
    #
    # # print(file_vec_list)
    #
    # label_set = list(set(label_name_list))
    # label_id_list = [label_set.index(x) for x in label_name_list]
    # # label_dict = np.diag(np.ones(len(label_set)))
    # # label_vec_list = np.array([label_dict[i] for i in label_id_list])
    # file_vec_list = np.array(file_vec_list)
    # print(file_vec_list.shape)
    #
    # file = open('adaboost_data.pkl','wb')
    # pkl.dump([file_vec_list,label_id_list],file)
    # file.close()
    # # # #-------------------

    file = open('adaboost_data.pkl','rb')
    [file_vec_list,label_id_list] = pkl.load(file)
    file.close()
    sample_num = len(file_vec_list)
    train_num = round(sample_num*0.8)
    print(sample_num)
    print(train_num)
    train_set = file_vec_list[:train_num]
    train_label = label_id_list[:train_num]

    test_set = file_vec_list[train_num:]
    test_label = label_id_list[train_num:]

    label_counter = Counter(train_label)

    # # # # AdaBoost
    # classifier = AdaBoostClassifier(
    #                                 base_estimator=DecisionTreeClassifier(criterion='entropy',
    #                                                                       max_depth=5,
    #                                                                       min_samples_split=20,
    #                                                                       min_samples_leaf=5),
    #                                 n_estimators=200,
    #                                 learning_rate=0.3,
    #                                 )

    # # # extra tree
    classifier = ExtraTreesClassifier(n_estimators=200,
                                      criterion='gini',
                                      max_depth=25,
                                      bootstrap=False,
                                      n_jobs=6,
                                      class_weight=label_counter
                                      )

    classifier.fit(np.array(train_set),np.array(train_label))
    print(classifier.score(np.array(train_set),np.array(train_label)))
    print(classifier.score(np.array(test_set),np.array(test_label)))
    predict_res = classifier.predict(np.array(test_set))