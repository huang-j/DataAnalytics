# coding: utf-8
import pandas as pd
import numpy as np
df = pd.read_csv('resecttest.csv', sep=',')
df['duplicate'] = df.duplicated('Patient ID', keep='first')
df = df.loc[df['duplicate'] == False]
df['t'] = df['t'].apply(lambda x: x[1:] if len(x) > 2 else x)
df['n'] = df['n'].apply(lambda x: x[1:] if len(x) > 2 else x)
df['m'] = df['m'].apply(lambda x: x[1:] if len(x) > 2 else x)
df['Regimen'] = df['Regimen'].fillna('')
df['Regimen'] = df['Regimen'].apply(lambda x: '5-FU' if 'FOL' in x else ('GEM' if 'GEM' in x else ''))
df['exo5'] = df['exoDNA'].apply(lambda x: 1 if (x >= 5) & (x != '') else 0)
df['exo1'] = df['exoDNA'].apply(lambda x: 1 if (x >= 1) & (x != '') else 0)
df['exo'] = df['exoDNA'].apply(lambda x: 1 if (x>0) & (x != '')  else 0)
df['cf'] = df['cfDNA'].apply(lambda x: 1 if (x>0)  & (x != '') else 0)
df['cf1'] = df['cfDNA'].apply(lambda x: 1 if (x >= 1) & (x != '') else 0)
df['cf.5'] = df['cfDNA'].apply(lambda x: 1 if (x >= .5)  & (x != '') else 0)
df['exoorcf'] = np.where( (df['exoDNA'] > 5) | (df['cfDNA'] > 0), 1, 0);
df['exoandcf'] = np.where( (df['exoDNA'] > 5) & (df['cfDNA'] > 0), 1, 0);
df['CA19-9'] = pd.to_numeric(df['CA19-9'], errors='coerce')
df['CA19.300'] = df['CA19-9'].apply(lambda x: 1 if (x >= 300)  & (x != '') else 0) 
df['tumorhead'] = df['tumor location'].apply(lambda x: 1 if 'Head' in x else 0)
df.to_csv('genericfilename.csv', sep=',')
