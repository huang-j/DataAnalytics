# coding: utf-8
import pandas as pd
import numpy as np
df = pd.read_csv('acetpm.csv', sep=',')
ecogs = pd.read_csv('nokarnofsky_updates.csv', sep=',')
nummets = pd.read_csv('nummet.csv', sep=',')
df['duplicate'] = df.duplicated('Patient ID', keep='first')
df = df.loc[df['duplicate'] == False]
df['ecog'] = df['Karnofsky'].apply(lambda x: 0 if x == 100 else
											(1 if x == 90 or x == 80 else 
											(2 if x == 70 or x == 60 else 
											(3 if x == 50 or x == 40 else 
											(4 if x == 30 or x == 20 or x == 10 else np.NaN)))))
df = pd.merge(df, ecogs, on='Patient ID', how='left')
df = pd.merge(df, nummets, on='Patient ID', how='left')
df['t'] = df['t'].apply(lambda x: x[1:] if len(x) > 2 else x)
df['n'] = df['n'].apply(lambda x: x[1:] if len(x) > 2 else x)
df['m'] = df['m'].apply(lambda x: x[1:] if len(x) > 2 else x)
df['Regimen'] = df['Regimen'].fillna('')
df['Regimen'] = df['Regimen'].apply(lambda x: '5-FU' if 'FOL' in x else ('GEM' if 'GEM' in x else ''))
df['Metastasis'] = df['Metastasis'].fillna('None')
df['Metastasis'] = df['Metastasis'].apply(lambda x: x.replace(' Metastasis', ''))
df['Metastasis'] = df['Metastasis'].apply(lambda x: x.replace(' metastasis', ''))
df['Metastasis'] = df['Metastasis'].apply(lambda x: 'Peritoneal' if 'Peritoneal' in x else (
														'Peritoneal' if 'Jejunal' in x else (
														'Lung' if 'Pleural' in x else (
														'Peritoneal' if 'Omental' in x else (
														'Peritoneal' if 'Ovarian' in x else x )))))
df['Met'] = df['Metastasis'].apply(lambda x: 0 if 'None' in x else 1)
df['metLivervAll'] = df['Metastasis'].apply(lambda x: 1 if 'Liver' in x else ('' if 'None' in x else 0))
df['metLivervLung'] = df['Metastasis'].apply(lambda x: 1 if 'Liver' in x else (0 if 'Lung' in x else ''))
df['metLivervPeri'] = df['Metastasis'].apply(lambda x: 1 if 'Liver' in x else (0 if 'Peritoneal' in x else ''))
df['factorMet'] = df['Metastasis'].apply(lambda x: 3 if 'Peritoneal' in x else (4 if 'Lymph' in x else (2 if 'Lung' in x else (1 if 'Liver' in x else (3 if 'Ovarian' in x else 5)))))

df['ecog'] = df['ecog'].fillna(df['ecog2'])
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
df.to_csv('genericfilenametest.csv', sep=',')
met = df.loc[df['clinical stage'] == 'Stage IV']
met.to_csv('genericfilename1test.csv', sep=',')
metspec = met.loc[(met['Metastasis'] != 'Ovarian') & (met['Metastasis'] != 'Lymph Node')]
metspec.to_csv('genericfilename1v2.csv', sep=',')
la = df.loc[df['clinical stage'] != 'Stage IV']
la.to_csv('genericfilename2test.csv', sep=',')
