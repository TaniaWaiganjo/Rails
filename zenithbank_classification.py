# -*- coding: utf-8 -*-
"""ZenithBank_Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LTtnL0HnUf5zlJR-r8tl0HxyB7xHHgKw

# Transaction Classification

1. With  sample labeled data, we build a classification model that learns to predict the labels for the rest of the data.
2. If specific transaction amounts determine classification,we use rule-based logic combined with the model output:
"""

# @title Loading required Packages
from pathlib import Path
from google.colab import drive
import pandas as pd
import numpy as np
import json
import ast
import re
from typing import Callable

import os
import pickle
import pandas as pd
import logging
import numpy as np
from optparse import OptionParser
import sys
from time import time
import matplotlib.pyplot as plt

import seaborn as sns
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix,accuracy_score, classification_report

# @title Loading Zenith transaction data
drive.mount('/content/gdrive',force_remount=True)
file_path ="/content/gdrive/MyDrive/Zennith_Classification/fwbankreconciliationautomationdocuments/Account_Statement _with Reference_Number.xlsx"
Fw_bank=pd.read_excel(file_path,skiprows=13)

# @title Pre-selecting columns required for classification
def columns_select(df) -> pd.DataFrame:
  df=df[['DATE POSTED','VALUE DATE', 'REFERENCE ID','DESCRIPTION',  'DEBIT', 'CREDIT','BALANCE']]
  return df
Fw_bank_data=columns_select(Fw_bank)
Fw_bank_data.head(5)

"""# Trainig Data:

* Create simple rules based on the transaction amount. For instance, if the amount is below or above a certain threshold, use the rule-based classification.
* Sample provided in the bank naration can be used to train ML to provide classifications for Zenith transaction data.
* Sample data must contain all variations/patterns possible to learn from existing sample.
* Sample data Augmentation: By using these augmentation techniques, we can generate a more diverse set of text patterns from a limited sample, which can help in improving the robustness of the ML
"""

# @title Loading labelled data
drive.mount('/content/gdrive',force_remount=True)
file_path ="/content/gdrive/MyDrive/Zennith_Classification/fwbankreconciliationautomationdocuments/Bank_Narration_Samples.xlsx"
sample1=pd.read_excel(file_path,sheet_name='SAMPLE 1',skiprows=1)
sample2=pd.read_excel(file_path,sheet_name='SAMPLE 2',skiprows=2)
sample3=pd.read_excel(file_path,sheet_name='SAMPLE 3',skiprows=0)

"""# Data Preprocessing
* This entails preprocessing data labels and transaction description column i.e commissions and various wallet funds are classified together
* Two sample sets are concatenated
"""

# @title Preprocessing training set
def preselect(df) -> pd.DataFrame:
  df=df.rename(columns={'BANK STATEMENT NARRATION': 'Narration',"BANK NARRATION" : "Narration",\
                        'AUTOMATION CATEGORY' : 'Category'})
  print(df.columns)
  df=df[['Narration','Category']]
  df['Narration']=df['Narration'].str.lower()
  df['Category'] = df['Category'].ffill()
  return df

def concatenate(df1,df2) -> pd.DataFrame:
  df=pd.concat([df1,df2])
  df=df.dropna()
  return df

def category_cleanup(x):
  a=["DSTV COMMISSION - INFLOW","BEDC COMMISSION - INFLOW"]
  b=["PTSP","PTSP SETTLEMENT"]
  c=["MPOS SALES","POS SALES"]
  d=["WALLET"]
  if x in a:
    return "COMMISSIONS"
  elif x in b:
    return "PTSP"
  elif x in c:
    return "POS/MPOS"
  elif any(sub in x for sub in d):
    return "WALLET FUNDING"
  else:
    return x

# @title Apply helper functions
sample1=preselect(sample1)
sample2=preselect(sample2)
Training_set=pd.concat([sample1,sample2,sample3],ignore_index=True)
Training_set['Category']=Training_set['Category'].apply(category_cleanup)
Training_set['Category'].value_counts()



# @title Helper functions
def clean_col_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.lower()
        .str.replace(r"[^\w|^\s]", "", regex=True)
        .str.replace(r"\s{2,}", " ", regex=True)
        .str.replace(r"\s", "_", regex=True)
    )
    return df


def transform_cols(
    df: pd.DataFrame, cols: list[str], func: Callable[[pd.Series], pd.Series]
) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        df[col] = func(df[col])
    return df

# @title Clean the bank statement
Fw_bank_data_clean = (
    Fw_bank_data.filter(regex=r"^((?!unnamed).*)$")
    # Clean date cols
    .pipe(
        lambda df: transform_cols(
            df=df,
            cols=df.filter(regex="(?i)date").columns.to_list(),
            func=lambda s: pd.to_datetime(s, errors="coerce", format="%d%m%Y").fillna(
                pd.to_datetime(s, errors="coerce")
            )
        )
    )
    .assign(

        debit=lambda df: df["DEBIT"] * -1,
        amount=lambda df: df["DEBIT"].fillna(df["CREDIT"]),
        outstanding=False,
    )
    .drop(columns=[ "DEBIT", "CREDIT"])
    .dropna(subset=["DATE POSTED"])
    .reset_index(drop=True)
)

Fw_bank_data_clean.head(5)

# @title Model Training
x_train,x_test,y_train,y_test=train_test_split(Training_set['Narration'],Training_set['Category'],test_size=0.3,random_state=42)

# Feature extraction using TF-IDF Vectorizer
vectorizer=TfidfVectorizer()
x_train_tfidf=vectorizer.fit_transform(x_train)
x_test_tfidf=vectorizer.transform(x_test)

# Use SMOTE to oversample the underrepresented classes in the training set
#smote = SMOTE(random_state=42)
#x_train_resampled, y_train_resampled = smote.fit_resample(x_train_tfidf, y_train)

# Train Naive Bayes Model
nb=MultinomialNB()
nb.fit(x_train_tfidf,y_train)

# Make prediction
y_pred=nb.predict(x_test_tfidf)

# Evaluate the model
accuracy=accuracy_score(y_test,y_pred)
report=classification_report(y_test,y_pred)

#ouptut results

print("Accuracy",accuracy)
print("classification Report:\n",report)

# @title Generate the confusion matrix
labels = np.unique(np.concatenate((y_test, y_pred)))

plt.figure(figsize=(10,5))
matrix=confusion_matrix(y_test,y_pred,labels=labels)
sns.heatmap(matrix,annot=True,fmt='d',xticklabels=labels,yticklabels=labels)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

#@title Apply classification to new data
classied_data=nb.predict(vectorizer.transform(Fw_bank_data_clean['DESCRIPTION']))
Fw_bank_data_clean['Category']=classied_data

Fw_bank_data_clean.sample(5)

#Fw_bank_data_clean.to_csv("/content/drive/MyDrive/Zennith_Classification/fwbankreconciliationautomationdocuments/output/Fw_bank_data_clean.csv",index=False)

pd.set_option('display.max_colwidth',None)
Training_set.loc[Training_set['Category']=='WALLET FUNDING']

Training_set.loc[(Training_set['Category']=='ISW CHARGES') | (Training_set['Category']=='Bank Charges')]

#Training_set.to_csv("/content/drive/MyDrive/Zennith_Classification/fwbankreconciliationautomationdocuments/output/Training_set.csv",index=False)

# @title Uploading New data

# Step 1: Mount Google Drive
from google.colab import drive
import os
import pandas as pd

# Mount Google Drive
#drive.mount('/content/drive')

# Step 2: Specify the directory path where CSV files are stored
jan_csv_folder = '/content/drive/MyDrive/Zennith_Classification/fwbankreconciliationautomationdocuments/Zenith and Monnify 3 months/Monnify - 6013432839/Jan'

# @title functions to load csv files
# Step 3: List all CSV files in the folder
from google.colab import drive # imports drive
drive.mount('/content/drive') # mounts the drive
excel_files = [f for f in os.listdir(jan_csv_folder) if f.endswith('.xlsx')]

# Step 4: Initialize an empty DataFrame to concatenate data
df_concat = pd.DataFrame()

# Step 5: Loop through each CSV file and concatenate them
for file in excel_files:
    file_path = os.path.join(jan_csv_folder, file)
    df = pd.read_excel(file_path)

    # Concatenate the current CSV with the previously read CSVs
    df_concat = pd.concat([df_concat, df], ignore_index=True)

# Step 6: Output the concatenated DataFrame
print("Concatenated DataFrame:")
print(df_concat.shape)

df_concat.sample(5)

# @title Extract transaction narration with money transfer
def extract_money_fund(df):

  # Define the pattern for money transfer
  monify_pattern = re.compile(r'Monnify Fund Transfer', re.IGNORECASE)
  wallet_pattern=re.compile(r'WALLET top up', re.IGNORECASE)
  combined_pattern = f'{monify_pattern}|{wallet_pattern}'

  # Check if the pattern exists and extract the money transfer
  #df['NARRATION']=df['NARRATION'].fillna("none")
  df['extracted_pattern']=np.where(df['NARRATION'].str.contains(monify_pattern), 'FUND TRANSFER',
                              np.where(df['NARRATION'].str.contains(wallet_pattern), 'WALLET FUNDING', 'None'))
  df['contains_pattern'] = df['NARRATION'].str.contains(monify_pattern)
  #df['extracted_pattern'] = df['NARRATION'].str.extract(f'{monify_pattern}')
  return df

Jan01_31_2024=extract_money_fund(df)

pd.set_option('display.max_colwidth',None)
Jan01_31_2024.loc[Jan01_31_2024['contains_pattern']==False]

# @title load Feb csv files
# Step 3: List all CSV files in the folder
from google.colab import drive # imports drive
drive.mount('/content/drive') # mounts the drive

feb_csv_folder = '/content/drive/MyDrive/Zennith_Classification/fwbankreconciliationautomationdocuments/Zenith and Monnify 3 months/Monnify - 6013432839/Feb'
excel_files = [f for f in os.listdir(feb_csv_folder) if f.endswith('.xlsx')]

# Step 4: Initialize an empty DataFrame to concatenate data
feb_data = pd.DataFrame()

# Step 5: Loop through each CSV file and concatenate them
for file in excel_files:
    file_path = os.path.join(feb_csv_folder, file)
    df = pd.read_excel(file_path)

    # Concatenate the current CSV with the previously read CSVs
    feb_data = pd.concat([feb_data, df], ignore_index=True)

# Step 6: Output the concatenated DataFrame
print("Concatenated DataFrame:")
print(feb_data.shape)

feb_data_labeled=extract_money_fund(feb_data)
feb_data_labeled.loc[feb_data_labeled['contains_pattern']==False]

# @title load March csv files
Mar_csv_folder = '/content/drive/MyDrive/Zennith_Classification/fwbankreconciliationautomationdocuments/Zenith and Monnify 3 months/Monnify - 6013432839/Mar'
excel_files = [f for f in os.listdir(Mar_csv_folder) if f.endswith('.xlsx')]

# Step 4: Initialize an empty DataFrame to concatenate data
March_data = pd.DataFrame()

# Step 5: Loop through each CSV file and concatenate them
for file in excel_files:
    file_path = os.path.join(Mar_csv_folder, file)
    df = pd.read_excel(file_path)

    # Concatenate the current CSV with the previously read CSVs
    March_data = pd.concat([March_data, df], ignore_index=True)

# Step 6: Output the concatenated DataFrame
print("Concatenated DataFrame:")
print(March_data.shape)

March_data_labeled=extract_money_fund(March_data)

pd.set_option('display.max_colwidth',None)
March_data_labeled.loc[(March_data_labeled['contains_pattern']==False) & (March_data_labeled['extracted_pattern']!='WALLET FUNDING')].sample(50)