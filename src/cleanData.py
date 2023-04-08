import numpy as np
import pandas as pd
# For visualizations
import matplotlib.pyplot as plt
# For regular expressions
import re
import csv


import spacy

contractions = { "ain't": "are not","'s":" is","aren't": "are not",
                     "can't": "cannot","can't've": "cannot have",
                     "'cause": "because","could've": "could have","couldn't": "could not",
                     "couldn't've": "could not have", "didn't": "did not","doesn't": "does not",
                     "don't": "do not","hadn't": "had not","hadn't've": "had not have",
                     "hasn't": "has not","haven't": "have not","he'd": "he would",
                     "he'd've": "he would have","he'll": "he will", "he'll've": "he will have",
                     "how'd": "how did","how'd'y": "how do you","how'll": "how will",
                     "I'd": "I would", "I'd've": "I would have","I'll": "I will",
                     "I'll've": "I will have","I'm": "I am","I've": "I have", "isn't": "is not",
                     "it'd": "it would","it'd've": "it would have","it'll": "it will",
                     "it'll've": "it will have", "let's": "let us","ma'am": "madam",
                     "mayn't": "may not","might've": "might have","mightn't": "might not", 
                     "mightn't've": "might not have","must've": "must have","mustn't": "must not",
                     "mustn't've": "must not have", "needn't": "need not",
                     "needn't've": "need not have","o'clock": "of the clock","oughtn't": "ought not",
                     "oughtn't've": "ought not have","shan't": "shall not","sha'n't": "shall not",
                     "shan't've": "shall not have","she'd": "she would","she'd've": "she would have",
                     "she'll": "she will", "she'll've": "she will have","should've": "should have",
                     "shouldn't": "should not", "shouldn't've": "should not have","so've": "so have",
                     "that'd": "that would","that'd've": "that would have", "there'd": "there would",
                     "there'd've": "there would have", "they'd": "they would",
                     "they'd've": "they would have","they'll": "they will",
                     "they'll've": "they will have", "they're": "they are","they've": "they have",
                     "to've": "to have","wasn't": "was not","we'd": "we would",
                     "we'd've": "we would have","we'll": "we will","we'll've": "we will have",
                     "we're": "we are","we've": "we have", "weren't": "were not","what'll": "what will",
                     "what'll've": "what will have","what're": "what are", "what've": "what have",
                     "when've": "when have","where'd": "where did", "where've": "where have",
                     "who'll": "who will","who'll've": "who will have","who've": "who have",
                     "why've": "why have","will've": "will have","won't": "will not",
                     "won't've": "will not have", "would've": "would have","wouldn't": "would not",
                     "wouldn't've": "would not have","y'all": "you all", "y'all'd": "you all would",
                     "y'all'd've": "you all would have","y'all're": "you all are",
                     "y'all've": "you all have", "you'd": "you would","you'd've": "you would have",
                     "you'll": "you will","you'll've": "you will have", "you're": "you are",
                     "you've": "you have"}

def containsVerb(sentence):
    nlp = spacy.load("en_core_web_sm")
    # Process the sentence with spaCy
    doc = nlp(sentence)
    tokens =[token.pos_ for token in doc]
    # Check if any token is a verb
    has_verb = any(token.pos_ == 'VERB' for token in doc)
    return has_verb
   

def expand_contractions(text):
    """
    This function takes a sentence and expands any contractions it finds
    using the contractions dictionary defined above.
    """
    pattern = re.compile("({})".format("|".join(contractions.keys())), re.IGNORECASE)
    def replace(match):
        return contractions[match.group(0).lower()]
    return pattern.sub(replace, text)

# Importing dataset

#two criteria to be experience 


pd.set_option('display.max_colwidth', None)


df=pd.read_csv('../res/experiences.csv') 
print("Shape of data=>",df.shape)

# print(df.head())


newEntries =[]

print(df.columns)


#rules for finding experiences
#longer than 4 words
#contains verb
#dont include if beggining contains same start as first entry in experience

x="I like to go to the stroe"
y= x.split()
print(len(y))
for index, row in df.iterrows():
    experienceList=[]
    skills=""
    experienceList.append("ss")
    entry = row[1]
    entryList= entry.split("\n")
    thisRole = entryList[0]
    for i, x in enumerate(entryList):
        currEntry = entryList[i]
        #prevent the back to back by ensuring its not == to most recent
        if(currEntry != experienceList[len(experienceList)-1]):
            tempString = currEntry.split(" ")
            #experience longer than 4 words
            if(currEntry[0:7]=="Skills:"):
                skills=currEntry
            if(len(tempString)>4):

                #if containsVerb
                if(containsVerb(currEntry)):
                    #if the starts aren't the same

                    if((len(experienceList)>0) and (currEntry[0:len(experienceList[len(experienceList)-1])] != experienceList[0])):
                        experienceList.append(currEntry)
    #lowercase
    newList = [sentence.lower() for sentence in experienceList]
    #punctiation and number
    pattern = re.compile(r'[^\w\s]+|\d+')
    sentences_cleaned = [pattern.sub('', sentence) for sentence in newList]

    sentence_expand = [expand_contractions(sentence) for sentence in sentences_cleaned]
    newPerson = {
        "index":index,
        "role":thisRole,
        "skills":skills,
        "experience":sentence_expand
    }
    print(newPerson)
    newEntries.append(newPerson)
        
print(newEntries)
    

            


# Convert the object to a Pandas DataFrame
df = pd.DataFrame(newEntries)

# Specify the order of columns
columns = ["index", "role","experience"]

# Write the DataFrame to a CSV file
with open("output.csv", mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    for row in df.to_dict(orient="records"):
        writer.writerow(row)
    

