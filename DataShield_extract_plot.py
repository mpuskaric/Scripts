'''
Script that takes output from R Datashield and translates
the vocabulary codes into labels and plots
'''

import pandas as pd
import os
import re
import matplotlib.pyplot as plt

#Working directory: Input required
working_dir = ""
# For translating variable codes into labels
pattern     = working_dir+"pattern.csv"
replacement = working_dir+"replacement.csv"
# Files
from_R      = working_dir+"result.txt"
result_tmp  = working_dir+"result_tmp.txt"
result      = working_dir+"result_final.txt"
# Keywords for navigation and deleting
keyword     = "$output.list$TABLE"
delete      = "$output.list"

# Read content from the text file
with open(from_R, 'r') as file:
    content = file.read()

# Read old text from a file
with open(pattern, 'r') as old_text_file:
    old_text_list = old_text_file.readlines()
    old_text_list = [line.strip() for line in old_text_list]

# Read new text from a file
with open(replacement, 'r', encoding="utf-8") as new_text_file:
    new_text_list = new_text_file.readlines()
    new_text_list = [line.strip() for line in new_text_list]

# Replace old text with new text
for old_text, new_text in zip(old_text_list, new_text_list):
    content = content.replace(old_text, new_text)

# Delete unnecessary content for the easier postprocessing extraction
content = re.sub("(?:(?!\n)\s)+", ",", content, flags=re.MULTILINE)
content = re.sub(r"^,", "", content, flags=re.MULTILINE)
content = re.sub(r"^\$validity.*\n?", "", content, flags=re.MULTILINE)
content = re.sub(r"^\[.*\n?", "", content, flags=re.MULTILINE)

# Write modified content back to the text file
with open(result_tmp, 'w') as file:
    file.write(content)

# Extraction and plotting
titles = []

# Extract title names
with open(result_tmp, 'r', newline='') as file:
    for line in file:
        if line.startswith(keyword):
            titles.append(next(file,'').strip())

# Delete lines containing output list
with open(result_tmp, 'r', newline='') as file:
    content = file.read()
    content = re.sub(r"^\$output\.list.*\n?", "", content, flags=re.MULTILINE)
with open(result, 'w') as file:
    file.write(content)

os.remove(result_tmp)

# Find column size
cols = content.splitlines()[2-1].count(",")

df = pd.read_csv(result,header=None, names=range(cols+1)) #columns
groups = df[0].isin(titles).cumsum()

# Extracting data frames from the result file
table = {}
for k,g in df.groupby(groups):
    table[k] = g.iloc[2:, 1:]
    table[k].index = g.iloc[2:, 0]
    table[k].columns = g.iloc[1, 1:]

# Data frame containing TABLES.COMBINED_all.sources_counts
pd.set_option('display.expand_frame_repr', False)

t_no = len(table) # Table number
print(table[t_no])
# Plotting
table[t_no]=table[t_no].astype(float)
plot = table[t_no].plot(kind='bar')
plt.show()
