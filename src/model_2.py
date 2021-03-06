# -*- coding: utf-8 -*-
"""model_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VOV0w-U3R23Nl35MknT-xNZGWB_P6C8G

#PRE-REQUISITES
"""

import numpy as np
import os
import pandas as pd
import re

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

import tensorflow as tf
tf.__version__

import keras
new_model = tf.keras.models.load_model('/content/drive/MyDrive/Colab Notebooks/trained/model_2')

"""#LOAD DATASET"""

data = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Dataset csv/train.csv")

d_articles=pd.DataFrame(data.iloc[:15000,[0,1]])
print(d_articles)
d_highlights=pd.DataFrame(data.iloc[:15000,[0,2]])

"""#DATA PREPROCESSING"""

num_words = 30000
oov_token = '<UNK>'
pad_type = 'post'
trunc_type = 'post'
MAX_LEN=600
MAX_LEN_S=100

"""##CLEAN TEXT"""

from contractions import contractions_dict

for key, value in list(contractions_dict.items())[:20]:
    print(f'{key} == {value}')

def cleantext(text,contraction_map=contractions_dict):
    contractions_keys = '|'.join(contraction_map.keys())
    contractions_pattern = re.compile(f'({contractions_keys})', flags=re.DOTALL)

    def expand_match(contraction):
        # Getting entire matched sub-string
        match = contraction.group(0)
        expanded_contraction = contraction_map.get(match)
        if not cleantext:
            print(match)
            return match
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text

def applyCleantext():
  d_articles["article"]= d_articles["article"].apply(cleantext)
  d_highlights["highlights"]= d_highlights["highlights"].apply(cleantext)
applyCleantext()

"""##ADD START AND END TOKENS"""

def addEOF():
  d_highlights["highlights"] = d_highlights["highlights"].apply(lambda x : '_sostok_'+ x + '_eostok_')
addEOF()

print(d_highlights['highlights'])

"""##SPLIT DATASET"""

from sklearn.model_selection import train_test_split
x_tr,x_val,y_tr,y_val=train_test_split(d_articles['article'],d_highlights['highlights'],test_size=0.2,random_state=0,shuffle=True)

print(x_tr)

from numpy.lib.function_base import average
import matplotlib.pyplot as plt
text_word_count = []
summary_word_count = []

def pltWordCount():
# populate the lists with sentence lengths
  for i in d_articles['article']:
        text_word_count.append(len(i.split()))

  for i in d_highlights['highlights']:
        summary_word_count.append(len(i.split()))
  print("AVERAGE COUNT:",average(text_word_count),average(summary_word_count))

  length_df = pd.DataFrame({'text':text_word_count, 'summary':summary_word_count})

  length_df.hist(bins = 50,figsize=(40,10),xlabelsize=20,ylabelsize=20)
  plt.ylabel('no. of samples',fontsize=25)
  plt.xlabel('no. of words',fontsize=25)
  plt.show()  
pltWordCount()

"""##TOKENIZE AND CREATE WORDtoID DICTIONARY"""

VOCAB_SIZE = 29999

def tokenizeX(x_tr,x_val):
  x_tokenizer = Tokenizer()
  x_tokenizer.fit_on_texts(list(x_tr))
  article_sequences = x_tokenizer.texts_to_sequences(x_tr)
  test_article=x_tokenizer.texts_to_sequences(x_val)
  art_word_index = x_tokenizer.word_index
  x_voc=len(x_tokenizer.word_index)+1
  return x_tokenizer,article_sequences,test_article,art_word_index,x_voc

x_tokenizer,article_sequences,test_article,art_word_index,x_voc=tokenizeX(x_tr,x_val)

def tokenizeY(y_tr,y_val):
  y_tokenizer=Tokenizer()
  y_tokenizer.fit_on_texts(list(y_tr))
  summary_sequences = y_tokenizer.texts_to_sequences(y_tr)
  test_summary=y_tokenizer.texts_to_sequences(y_val)
  sum_word_index = y_tokenizer.word_index
  y_voc=len(y_tokenizer.word_index)+1
  return y_tokenizer,summary_sequences,test_summary,sum_word_index,y_voc

y_tokenizer,summary_sequences,test_summary,sum_word_index,y_voc=tokenizeY(y_tr,y_val)

print((art_word_index))

def buildVocab(art_word_index,sum_word_index):
  art_vocab = {}
  counter = 0
  for word in art_word_index.keys():
      if art_word_index[word] == 0:
          print("found 0!")
          break
      if art_word_index[word] > VOCAB_SIZE:
          continue
      else:
          art_vocab[word] = art_word_index[word]
          counter += 1
  sum_vocab = {}
  counter = 0
  for word in sum_word_index.keys():
      if sum_word_index[word] == 0:
          print("found 0!")
          break
      if sum_word_index[word] > VOCAB_SIZE:
          continue
      else:
          sum_vocab[word] = sum_word_index[word]
          counter += 1
  return art_vocab,sum_vocab

art_vocab,sum_vocab=buildVocab(art_word_index,sum_word_index)

print(art_vocab)

"""##PAD ARTICLES AND SUMMARIES"""

def padText(article_sequences,test_article,summary_sequences,test_summary):  
  pad_article = pad_sequences(article_sequences, maxlen=MAX_LEN, padding='post', truncating='post')
  pad_article_test = pad_sequences(test_article, maxlen=MAX_LEN, padding='post', truncating='post')
  pad_highlight = pad_sequences(summary_sequences, maxlen=MAX_LEN_S, padding='post', truncating='post')
  pad_highlight_test = pad_sequences(test_summary, maxlen=MAX_LEN_S, padding='post', truncating='post')
  return pad_article,pad_article_test,pad_highlight,pad_highlight_test

pad_article,pad_article_test,pad_highlight,pad_highlight_test=padText(article_sequences,test_article,summary_sequences,test_summary)

print(pad_article.shape)
print(pad_highlight)

"""##LOAD PRETRAINED EMBEDDINGS OF 200D"""

def loadGlove():
  embeddings_index = {}
  with open('/content/drive/MyDrive/Colab Notebooks/glove.6B.200d.txt', encoding='utf-8') as f:
      for line in f:
          values = line.split()
          word = values[0]
          coefs = np.asarray(values[1:], dtype='float32')
          embeddings_index[word] = coefs
      f.close()
  return embeddings_index

embeddings_index=loadGlove()

# all_embeddings = np.array(embeddings_index)
# np.save('embeddings.npy', all_embeddings)

"""##INITIALIZE WORD EMBEDDINGS """

def embedding_matrix_creater(embedding_dimension, word_index):
    embedding_matrix = np.zeros((len(word_index) + 1, embedding_dimension))
    for word, i in word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
          # words not found in embedding index will be all-zeros.
            embedding_matrix[i] = embedding_vector
    return embedding_matrix

def initialize_emb(art_word_index,pad_article,pad_highlight):
  art_embedding_matrix = embedding_matrix_creater(200, word_index=art_word_index)
  doc_emb=np.zeros((12000,600,200))
  sum_embedding_matrix = embedding_matrix_creater(200, word_index=sum_word_index)
  sum_emb=np.zeros((12000,100,200))
  for i in range(12000):
    doc_emb[i]=[art_embedding_matrix[j] for j in pad_article[i]]
    sum_emb[i]=[sum_embedding_matrix[j] for j in pad_highlight[i]]
  return doc_emb,art_embedding_matrix,sum_emb,sum_embedding_matrix

doc_emb,art_embedding_matrix,sum_emb,sum_embedding_matrix=initialize_emb(art_word_index,pad_article,pad_highlight)
print(art_embedding_matrix)

def embedding_layer_creater(VOCAB_SIZE, EMBEDDING_DIM, MAX_LEN, embedding_matrix):
  embedding_layer = tf.keras.layers.Embedding(input_dim = VOCAB_SIZE, 
                                    output_dim = EMBEDDING_DIM,
                                    input_length = MAX_LEN,
                                    weights = [embedding_matrix],
                                    trainable = False)
  
  return embedding_layer

if not os.path.exists("/content/drive/MyDrive/Colab Notebooks/trained"):
    os.makedirs("/content/drive/MyDrive/Colab Notebooks/trained")


"""#BUILD MODEL"""

from numpy.random import seed
seed(1)
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import warnings
import tensorflow as tf
from sklearn.model_selection import train_test_split
import logging
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import pandas as pd
import pydot
import keras
import numpy as np
from keras import backend as K
K.set_learning_phase(1)
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras import initializers
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed, Bidirectional
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.callbacks import EarlyStopping
from keras.layers.advanced_activations import LeakyReLU,PReLU
from keras.callbacks import ModelCheckpoint
from keras.models import load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.python.keras.layers import Layer

#Hyperparams
#LSTM ENCODER
MAX_LEN = 600
MAX_LEN_S=100
VOCAB_SIZE=VOCAB_SIZE+1
EMBEDDING_DIM = 200
HIDDEN_UNITS = 256
LEARNING_RATE = 0.0002
input_len=MAX_LEN

#Customized attention layer
class AttentionLayer(Layer):
    """
    This class implements Bahdanau attention (https://arxiv.org/pdf/1409.0473.pdf).
    There are three sets of weights introduced W_a, U_a, and V_a
     """

    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        assert isinstance(input_shape, list)
        # Create a trainable weight variable for this layer.

        self.W_a = self.add_weight(name='W_a',
                                   shape=tf.TensorShape((input_shape[0][2], input_shape[0][2])),
                                   initializer='random_normal',
                                   trainable=True)
        self.U_a = self.add_weight(name='U_a',
                                   shape=tf.TensorShape((input_shape[1][2], input_shape[0][2])),
                                   initializer='random_normal',
                                   trainable=True)
        self.V_a = self.add_weight(name='V_a',
                                   shape=tf.TensorShape((input_shape[0][2], 1)),
                                   initializer='uniform',
                                   trainable=True)

        super(AttentionLayer, self).build(input_shape)  # Be sure to call this at the end

    def call(self, inputs, verbose=False):
        """
        inputs: [encoder_output_sequence, decoder_output_sequence]
        """
        assert type(inputs) == list
        encoder_out_seq, decoder_out_seq = inputs
        if verbose:
            print('encoder_out_seq>', encoder_out_seq.shape)
            print('decoder_out_seq>', decoder_out_seq.shape)

        def energy_step(inputs, states):
            """ Step function for computing energy for a single decoder state """

            assert_msg = "States must be a list. However states {} is of type {}".format(states, type(states))
            assert isinstance(states, list) or isinstance(states, tuple), assert_msg

            """ Some parameters required for shaping tensors"""
            en_seq_len, en_hidden = encoder_out_seq.shape[1], encoder_out_seq.shape[2]
            de_hidden = inputs.shape[-1]

            """ Computing S.Wa where S=[s0, s1, ..., si]"""
            # <= batch_size*en_seq_len, latent_dim
            reshaped_enc_outputs = K.reshape(encoder_out_seq, (-1, en_hidden))
            # <= batch_size*en_seq_len, latent_dim
            W_a_dot_s = K.reshape(K.dot(reshaped_enc_outputs, self.W_a), (-1, en_seq_len, en_hidden))
            if verbose:
                print('wa.s>',W_a_dot_s.shape)

            """ Computing hj.Ua """
            U_a_dot_h = K.expand_dims(K.dot(inputs, self.U_a), 1)  # <= batch_size, 1, latent_dim
            if verbose:
                print('Ua.h>',U_a_dot_h.shape)

            """ tanh(S.Wa + hj.Ua) """
            # <= batch_size*en_seq_len, latent_dim
            reshaped_Ws_plus_Uh = K.tanh(K.reshape(W_a_dot_s + U_a_dot_h, (-1, en_hidden)))
            if verbose:
                print('Ws+Uh>', reshaped_Ws_plus_Uh.shape)

            """ softmax(va.tanh(S.Wa + hj.Ua)) """
            # <= batch_size, en_seq_len
            e_i = K.reshape(K.dot(reshaped_Ws_plus_Uh, self.V_a), (-1, en_seq_len))
            # <= batch_size, en_seq_len
            e_i = K.softmax(e_i)

            if verbose:
                print('ei>', e_i.shape)

            return e_i, [e_i]

        def context_step(inputs, states):
            """ Step function for computing ci using ei """
            # <= batch_size, hidden_size
            c_i = K.sum(encoder_out_seq * K.expand_dims(inputs, -1), axis=1)
            if verbose:
                print('ci>', c_i.shape)
            return c_i, [c_i]

        def create_inital_state(inputs, hidden_size):
            # We are not using initial states, but need to pass something to K.rnn funciton
            fake_state = K.zeros_like(inputs)  # <= (batch_size, enc_seq_len, latent_dim
            fake_state = K.sum(fake_state, axis=[1, 2])  # <= (batch_size)
            fake_state = K.expand_dims(fake_state)  # <= (batch_size, 1)
            fake_state = K.tile(fake_state, [1, hidden_size])  # <= (batch_size, latent_dim
            return fake_state

        fake_state_c = create_inital_state(encoder_out_seq, encoder_out_seq.shape[-1])
        fake_state_e = create_inital_state(encoder_out_seq, encoder_out_seq.shape[1])  # <= (batch_size, enc_seq_len, latent_dim

        """ Computing energy outputs """
        # e_outputs => (batch_size, de_seq_len, en_seq_len)
        last_out, e_outputs, _ = K.rnn(
            energy_step, decoder_out_seq, [fake_state_e],
        )

        """ Computing context vectors """
        last_out, c_outputs, _ = K.rnn(
            context_step, e_outputs, [fake_state_c],
        )

        return c_outputs, e_outputs
    def get_config(self):
      config = super(AttentionLayer, self).get_config()
      
      return config

    def compute_output_shape(self, input_shape):
        """ Outputs produced by the layer """
        return [
            tf.TensorShape((input_shape[1][0], input_shape[1][1], input_shape[1][2])),
            tf.TensorShape((input_shape[1][0], input_shape[1][1], input_shape[0][1]))
        ]

K.clear_session() 

def defineModel(max_len_text,max_len_summary,latent_dim,x_voc,y_voc,art_embedding_matrix,sum_embedding_matrix):
  max_len_text=600
  max_len_summary=100
  # Encoder 
  encoder_inputs = Input(shape=(max_len_text,)) 
  enc_emb = Embedding(x_voc, 200, embeddings_initializer=tf.keras.initializers.Constant(art_embedding_matrix),input_length=max_len_text, trainable=False)(encoder_inputs) 

  #LSTM 1 
  encoder_lstm1 = LSTM(latent_dim,return_sequences=True,return_state=True) 
  encoder_output1, state_h1, state_c1 = encoder_lstm1(enc_emb) 

  #LSTM 2 
  encoder_lstm2 = LSTM(latent_dim,return_sequences=True,return_state=True) 
  encoder_output2, state_h2, state_c2 = encoder_lstm2(encoder_output1) 

  #LSTM 3 
  encoder_lstm3=LSTM(latent_dim, return_state=True, return_sequences=True) 
  encoder_outputs, *encoder_final_states= encoder_lstm3(encoder_output2) 

  # Set up the decoder. 
  decoder_inputs = Input(shape=(None,)) 
  dec_emb_layer = Embedding(y_voc, 200, embeddings_initializer=tf.keras.initializers.Constant(sum_embedding_matrix),input_length=max_len_summary, trainable=False) 
  dec_emb = dec_emb_layer(decoder_inputs) 

  #LSTM using encoder_states as initial state
  decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True) 
  decoder_outputs,*decoder_final_states = decoder_lstm(dec_emb,initial_state=encoder_final_states) 

  #Attention Layer
  attn_layer = AttentionLayer(name='attention_layer') 
  attn_out, attn_states = attn_layer([encoder_outputs, decoder_outputs]) 

  # Concat attention output and decoder LSTM output 
  decoder_concat_input = Concatenate(axis=-1, name='concat_layer')([decoder_outputs, attn_out])

  #Dense layer
  decoder_dense = TimeDistributed(Dense(y_voc, activation='softmax')) 
  decoder_outputs = decoder_dense(decoder_concat_input) 

  # Define the model
  model = Model([encoder_inputs, decoder_inputs], decoder_outputs) 
  model.summary()

  return {
            'model': model,
            'inputs': {
                'encoder': encoder_inputs,
                'decoder': decoder_inputs
            },
            'outputs': {
                'encoder': encoder_outputs,
                'decoder': decoder_outputs,
                'attention':attn_out
            },
            'states': {
                'encoder': encoder_final_states,
                'decoder': decoder_final_states,
                'attention':attn_states
            },
            'layers': {
                'decoder': {
                    'embedding': dec_emb_layer,
                    'last_decoder_lstm': decoder_lstm,
                    'dense': decoder_dense
                },
                'attention':{
                    'layer':attn_layer
                }
            }
        }

model_info=defineModel(MAX_LEN,MAX_LEN_S,HIDDEN_UNITS,x_voc,y_voc,art_embedding_matrix,sum_embedding_matrix)

# At loading time, register the custom objects with a `custom_object_scope`:

# custom_objects = {"AttentionLayer": AttentionLayer}
# with keras.utils.custom_object_scope(custom_objects):
#     new_model = keras.Model.from_config(config)
# with keras.utils.custom_object_scope(custom_objects):
#     new_model = keras.models.clone_model(model)

model = model_info['model']

encoder_input = model_info['inputs']['encoder']
decoder_input = model_info['inputs']['decoder']

encoder_output =model_info['outputs']['encoder']
decoder_output = model_info['outputs']['decoder']
attention_output=model_info['outputs']['attention']

encoder_final_states =model_info['states']['encoder']
decoder_final_states =model_info['states']['decoder']
attn_final_states=model_info['states']['attention']

decoder_embedding_layer = model_info['layers']['decoder']['embedding']
last_decoder_lstm = model_info['layers']['decoder']['last_decoder_lstm']
decoder_dense = model_info['layers']['decoder']['dense']

attention_layer=model_info['layers']['attention']['layer']

model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1)

history=model.fit([pad_article,pad_highlight[:,:-1]], pad_highlight.reshape(pad_highlight.shape[0],pad_highlight.shape[1], 1)[:,1:] ,epochs=30,callbacks=[es],batch_size=32, validation_data=([pad_article_test,pad_highlight_test[:,:-1]], pad_highlight_test.reshape(pad_highlight_test.shape[0],pad_highlight_test.shape[1], 1)[:,1:]))

from keras.models import load_model
model.save("/content/drive/MyDrive/Colab Notebooks/trained/model_3")

from matplotlib import pyplot
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

reverse_target_word_index=y_tokenizer.index_word
reverse_source_word_index=x_tokenizer.index_word
target_word_index=y_tokenizer.word_index

def inference(encoder_inputs,encoder_outputs,encoder_final_states,latent_dim,dec_emb_layer,decoder_inputs,decoder_lstm,attn_layer):
  state_h=encoder_final_states[0]
  state_c=encoder_final_states[1]

  encoder_model = Model(inputs=encoder_inputs,outputs=[encoder_outputs, state_h, state_c])
  # Decoder setup
  # Below tensors will hold the states of the previous time step
  decoder_state_input_h = Input(shape=(latent_dim,))
  decoder_state_input_c = Input(shape=(latent_dim,))
  decoder_hidden_state_input = Input(shape=(MAX_LEN,latent_dim))

  # Get the embeddings of the decoder sequence
  dec_emb2= dec_emb_layer(decoder_inputs) 
  # To predict the next word in the sequence, set the initial states to the states from the previous time step
  decoder_outputs2, state_h2, state_c2 = decoder_lstm(dec_emb2, initial_state=[decoder_state_input_h, decoder_state_input_c])

  #attention inference
  attn_out_inf, attn_states_inf = attn_layer([decoder_hidden_state_input, decoder_outputs2])
  decoder_inf_concat = Concatenate(axis=-1, name='concat')([decoder_outputs2, attn_out_inf])

  # A dense softmax layer to generate prob dist. over the target vocabulary
  decoder_outputs2 = decoder_dense(decoder_inf_concat) 

  # Final decoder model
  decoder_model = Model(
      [decoder_inputs] + [decoder_hidden_state_input,decoder_state_input_h, decoder_state_input_c],
      [decoder_outputs2] + [state_h2, state_c2])
  return (encoder_model,decoder_model)

encoder_model,decoder_model=inference(encoder_input,encoder_output,encoder_final_states,HIDDEN_UNITS,decoder_embedding_layer,decoder_input,last_decoder_lstm,attention_layer)

def decode_sequence(input_seq,encoder_model,decoder_model):
    # Encode the input as state vectors.
    e_out, e_h, e_c = encoder_model.predict(input_seq)
    
    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1,1))
    
    # Populate the first word of target sequence with the start word.
    target_seq[0, 0] = target_word_index['sostok']

    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
      
        output_tokens, h, c = decoder_model.predict([target_seq] + [e_out, e_h, e_c])

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_token = reverse_target_word_index[sampled_token_index]
        
        if(sampled_token!='sostok'):
            decoded_sentence += ' '+sampled_token

        # Exit condition: either hit max length or find stop word.
        if (sampled_token == 'eostok'  or len(decoded_sentence.split()) >= (MAX_LEN_S-1)):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1,1))
        target_seq[0, 0] = sampled_token_index

        # Update internal states
        e_h, e_c = h, c

    return decoded_sentence

len(target_word_index)

def seq2summary(input_seq):
    newString=''
    for i in input_seq:
        if((i!=0 and i!=target_word_index['sostok']) and i!=target_word_index['eostok']):
            newString=newString+reverse_target_word_index[i]+' '
    return newString

def seq2text(input_seq):
    newString=''
    for i in input_seq:
        if(i!=0):
            newString=newString+reverse_source_word_index[i]+' '
    return newString

predicted=pd.DataFrame(columns=['article','original','output'])
for i in range(0,30):
    print("Article:",x_val.iloc[i])
    print("Original summary:",y_val.iloc[i])
    p=decode_sequence(pad_article_test[i].reshape(1,MAX_LEN),encoder_model,decoder_model)
    print("Predicted summary:",p)
    print("\n")
    
    data=[x_val.iloc[i],y_val.iloc[i],' '.join(p.split())]
    predicted=pd.concat([predicted,pd.DataFrame([data],columns=predicted.columns)],ignore_index=True)

#predicted.to_csv("/content/drive/MyDrive/Colab Notebooks/trained/predicted_2.csv")
#predicted=pd.read_csv('/content/drive/MyDrive/Colab Notebooks/trained/predicted.csv')

from rouge import Rouge
ROUGE = Rouge()

candidate,reference=predicted['output'],predicted['original']

print(ROUGE.get_scores(candidate, reference,avg=True))
#predicted


#KNOWLEDGE BASE EMBEDDINGS
"""

import pandas
entity_file= pandas.read_csv('/content/drive/MyDrive/Colab Notebooks/Dataset csv/entity_embeddings.tsv',sep='\t',header=None)
entity_file[:].shape

X=entity_file.iloc[:,0]
Y=entity_file.iloc[:,1:201]

doc_emb[0]

"""##VISUALIZE KB AND DATASET EMBEDDINGS"""

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.decomposition import PCA as sklearnPCA
pca = sklearnPCA(n_components=2) #2-dimensional PCA
transformed = pd.DataFrame(pca.fit_transform(Y))
plt.scatter(transformed[:20][0], transformed[:20][1],c='red')
t=pd.DataFrame(pca.fit_transform(doc_emb[0]))
plt.scatter(t[:10][0], t[:10][1],c='blue')
word_list=list(art_word_index.keys())
for i in range(10):
  plt.annotate(str(word_list[pad_article[0][i]-1])+str(i),(t[0][i],t[1][i]))
for i in range(20):
  plt.annotate(str(X[i]),(transformed[0][i],transformed[1][i]))
plt.xlim(-1,1)
plt.show()

from sklearn.metrics.pairwise import cosine_similarity 
import numpy as np

def similar_documents(text, df, n=5):
    df=pd.DataFrame(columns=['text','entity','similarity'])
    for doc in text:
      arr=cosine_similarity(doc,Y)
      arr = -np.sort(-arr, axis=1)[:,5]
      data=[]
    #return (df.sort_values(by='similarity', ascending=False)[['text', 'similarity']].head(n))
      pd.concat()
    return arr[:,:5]

#user_input = """Nah I don't think he goes to usf, he lives around here though"""

similar_documents(doc_emb, Y, 5).shape
print(similar_documents(doc_emb[0], Y, 5))