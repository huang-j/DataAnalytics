#!/usr/bin/env python3
from pathlib import Path
import json
import pandas as pd
import numpy as np
import re
from functools import reduce
'''
This script takes runs all .counts files in directory recursively and creates a dataframe of them.
The files are compared to a the TCGA file database to connect the IDs of each samples
Requires the clinical file, and files file as jsons.
'''

## import json files
with open("files.json", "r") as jsonfile:
    files = json.load(jsonfile)
with open("clinical.cases_selection.json", "r") as jsonfile:
    clinical = json.load(jsonfile)

## list of dataframes (to merge)
dfs = []

## list of paths to files pre-unzipped
countfiles = list(Path(".").rglob("*.counts"))

for file in files:
    try:
        ## Already gzipped everything
        filename = re.sub(".gz", "", file["file_name"])
        file_id = file["file_id"]
        i = countfiles.index(Path(file_id + "/" + filename))
        dfs.append(pd.read_csv(countfiles[i], sep="\t", names=["Gene", file["cases"][0]["case_id"] + "." + filename ]))
    except Exception as e:
        print(file["file_name"] + " Not Found")
        pass


## brute force loop (inefficient but whatever)
## NOTE: Can't call individual
# for file in countfiles:
#     ## make sure that file is in list
#     # print(str(file) + ".gz")
#     # print(files["file_name" == str(file) + ".gz"]["cases"])
#     try:
#         case_id = files["file_name" == (str(file) + ".gz")]["cases"][0]["case_id"]
#         # sampname = clinical["case_id" == case_id]["demographic"]["submitter_id"]
#         # sampname = re.sub("_demographic", "", sampname)
#         dfs.append(pd.read_csv(file, sep="\t", names=["Gene", case_id]))
#     except Exception as e:
#         print("File not found")
#         pass

mergedf = reduce(lambda left,right: pd.merge(left, right, on="Gene", how="outer"), dfs)
mergedf.to_csv("TCGAPAAD.counts.tsv", sep="\t", index=False)
