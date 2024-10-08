# -*- coding: utf-8 -*-
"""Generalization-nomba-fsp

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YDg7blWwFfNKGFImBGjDszdIyMZS2K3H
"""

from google.colab import drive
drive.flush_and_unmount()
from google.colab import drive
drive.mount('/content/drive')
from unicodedata import numeric
from pathlib import Path
from google.colab import drive

import  pandas as pd
import re
import matplotlib.pyplot as plt

from unicodedata import numeric
from pathlib import Path
from google.colab import drive

import  pandas as pd
import re
import matplotlib.pyplot as plt

BASE_DIR=Path().resolve().parent
GDRIVE_MOUNT=BASE_DIR/"gdrive"
DATA_DIR = GDRIVE_MOUNT / "/gdrive/My Drive/Generalization-nomba-fsp/397"
drive.mount(GDRIVE_MOUNT.as_posix(), force_remount=True)

!ls /gdrive/MyDrive/Generalization-nomba-fsp

nomba_fsp = pd.read_csv(DATA_DIR/'nomba-397.csv')

""" CSV file must contain 'description', 'transaction_type', and 'label' columns, description, reporting-tag"""

nomba_fsp.columns

"""##Column adjustment
Add client id and account number
Select columns
"""

nomba_fsp['account_number'] = 397
nomba_fsp['client_id'] = 3
nomba_fsp = nomba_fsp[['client_id', 'account_number', 'description', 'reporting_tag', 'transaction_type']]
nomba_fsp.head()

"""###Getting unique reporting tags"""

unique_counts = nomba_fsp['reporting_tag'].value_counts()
num_unique = len(unique_counts)
print(f"Number of unique reporting_tag values: {num_unique}")
print("\nCount of each unique reporting_tag value:")
print(unique_counts)

unique_counts_fsp = unique_counts.reset_index()
unique_counts_fsp.columns = ['reporting_tag', 'count']
unique_counts_fsp

"""## Write to files in drive

"""

file_path = "/gdrive/My Drive/Generalization-nomba-fsp/397/output.xlsx"
nomba_fsp.to_excel(file_path, index=False)

#!pip install --upgrade gspread
#!pip install pandas

from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

gc = gspread.authorize(creds)

# Open the Google Sheet by name
sheet = gc.open('Nomba_FSP_generalizations').sheet1

# Convert the DataFrame to a list of lists
data = unique_counts_fsp.values.tolist()

# Append the data to the sheet
sheet.append_rows(data)

