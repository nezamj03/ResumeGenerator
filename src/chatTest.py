import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import *
from sklearn.model_selection import train_test_split

import pandas as pd
import numpy as np

df = pd.read_csv('../res/data.csv')
experiences = list(df.experience)

input_sentences, output_sentences = train_test_split(experiences, test_size=0.5, random_state=18)
output_sentences = ['<sos> ' + sentence + ' <eos>' for sentence in output_sentences]

# Define model parameters
input_length = 15  # Adjust this based on your dataset
output_length = 6  # Adjust this based on your dataset
embedding_dim = 100
lstm_units = 256

# Build the encoder

tokenizer = Tokenizer(filters='')
tokenizer.fit_on_texts(input_sentences + output_sentences)
vocab_size = len(tokenizer.word_index) + 1

print("Word index:", tokenizer.word_index)
print("Vocabulary size:", vocab_size)

# Tokenize and pad input sentences
input_data = tokenizer.texts_to_sequences(input_sentences)
input_data = pad_sequences(input_data, maxlen=input_length, padding='post')

# Tokenize and pad output sentences
output_data = tokenizer.texts_to_sequences(output_sentences)
output_data = pad_sequences(output_data, maxlen=output_length, padding='post')

# Convert output sentences to one-hot encoded vectors
target_data = to_categorical(output_data, num_classes=vocab_size)


encoder_inputs = Input(shape=(input_length,))
encoder_embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)(encoder_inputs)
encoder_lstm = LSTM(lstm_units, return_state=True)
_, state_h, state_c = encoder_lstm(encoder_embedding)
encoder_states = [state_h, state_c]

# Build the decoder
decoder_inputs = Input(shape=(output_length,))
decoder_embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)(decoder_inputs)
decoder_lstm = LSTM(lstm_units, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = Dense(vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# Compile the model
seq2seq = Model([encoder_inputs, decoder_inputs], decoder_outputs)
seq2seq.compile(optimizer='adam', loss='categorical_crossentropy')

# Train the model on your dataset
seq2seq.fit([input_data, output_data], target_data, epochs=45, batch_size=64, validation_split=0.2)

# Define the inference model
encoder_model = Model(encoder_inputs, encoder_states)

decoder_state_input_h = Input(shape=(lstm_units,))
decoder_state_input_c = Input(shape=(lstm_units,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
decoder_outputs, state_h, state_c = decoder_lstm(decoder_embedding, initial_state=decoder_states_inputs)
decoder_states = [state_h, state_c]
decoder_outputs = decoder_dense(decoder_outputs)
decoder_model = Model([decoder_inputs] + decoder_states_inputs, [decoder_outputs] + decoder_states)

# Function to generate a similar sentence
def generate_similar_sentence(input_sentence):
    # Tokenize and pad the input sentence
    input_tokens = tokenizer.texts_to_sequences([input_sentence])
    input_tokens = tf.keras.preprocessing.sequence.pad_sequences(input_tokens, maxlen=input_length, padding='post')

    # Encode the input sentence using the encoder model
    states_value = encoder_model.predict(input_tokens)

    # Initialize the target sequence with the start-of-sequence token
    target_seq = np.zeros((1, output_length))
    target_seq[0, 0] = tokenizer.word_index['<sos>']

    # Generate the output sentence, one word at a time
    output_sentence = []
    stop_condition = False
    current_token_idx = 0
    while not stop_condition:
        # Get the next word's probabilities and states from the decoder model
        output_tokens, h, c = decoder_model.predict([target_seq] + states_value)

        # Sample the next word using the predicted probabilities
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_word = tokenizer.index_word.get(sampled_token_index, '<unk>')

        # Append the sampled word to the output sentence
        output_sentence.append(sampled_word)

        # Update the target sequence and states for the next iteration
        target_seq = np.zeros((1, output_length))
        target_seq[0, 0] = sampled_token_index
        states_value = [h, c]

        # Check for stop conditions: end-of-sequence token or maximum output length
        current_token_idx += 1
        if sampled_word == '<eos>' or current_token_idx >= output_length:
            stop_condition = True

    # Remove any special tokens like <sos>, <eos>, or <unk>
    output_sentence = [word for word in output_sentence
    ]

    # Join the output words to form the generated sentence
    output_sentence = ' '.join(output_sentence)

    return output_sentence

input_sentence = "web"
similar_sentence = generate_similar_sentence(input_sentence)
print(similar_sentence)
