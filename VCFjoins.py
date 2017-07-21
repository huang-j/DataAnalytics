# coding: utf-8
import pandas as pd
import numpy as np
import math
def separateByChrom(df):
	chrDict = {}
	for chrom in df['CHROM'].unique():
		tempDF = df.loc[df['CHROM'] == chrom]
		chrDict[chrom] = tempDF
	return chrDict

def createInnerJoins(dfdict, dfdictR):
	chrDict = {}
	for chrom in dfdict.keys():
		chrDict[chrom] = dfdict[chrom].merge(dfdictR[chrom], how='inner', on='POS')
	return chrDict

def leftJoinsOnly(dfdictL, dfdictR):
	chrDict = {}
	for chrom in dfdictL.keys():
		chrDict[chrom] = dfdictL[chrom].merge(dfdictR[chrom], how='left', on='POS', indicator='_merge')
		chrDict[chrom] = chrDict[chrom].loc[chrDict[chrom]['_merge'] == 'left_only']
	return chrDict

def concatDFDict(dfdict):
	concatDF = pd.concat([dfdict[chrom] for chrom in dfdict.keys()])
	return concatDF

germline = pd.read_csv("NGS/_Sequences/MS05germline.csv", sep='\t')
germline = pd.read_csv("NGS/_Sequences/MS05germline.csv", sep=',')
germline.CHROM = germline.CHROM.apply(lambda x: x[3:])
H2B_2 = pd.read_csv("NGS/_Sequences/MS05_H2B_exoDNA-42887042/SuperReads(Variants).vcf", sep='\t', skiprows=13)
columns = H2B_2.columns.values
columns[0] = 'CHROM'
H2B_2.columns = columns
MS05_3 = pd.read_csv("NGS/_Sequences/MS05_3/MS05_3_H2B-47900064/UnfilteredVariants.vcf", sep='\t', skiprows=13)
columns = MS05_3.columns.values
columns[0] = 'CHROM'
MS05_3.columns = columns
MS053filtered = pd.read_csv("NGS/_Sequences/MS05_3/MS05_3_H2B-47900064/Variants.vcf", sep='\t', skiprows=13)
columns = MS053filtered.columns.values
columns[0] = 'CHROM'
MS053filtered.columns = columns
cosmic = pd.read_csv("CosmicCodingMuts37.vcf", sep='\t', skiprows=13, low_memory=False)
columns = cosmic.columns.values
columns[0] = 'CHROM'
cosmic.columns = columns

## generate dictionaries
gldict = separateByChrom(germline)
h2b2dict = separateByChrom(H2B_2)
ms053dict = separateByChrom(MS05_3)
cosmicdict = separateByChrom(cosmic)
ms053fdict = separateByChrom(MS053filtered)

## dash3 only (change the order to switch)
dash3only = leftJoinsOnly(h2b2dict, ms053dict)
fdash3only = leftJoinsOnly(h2b2dict, ms053fdict)
columns = dash3only['1'].columns.values
columns[0] = 'CHROM'
columns[2] = 'ID'
columns[3] = 'REF'
columns[4] = 'ALT'
columns[-1] = '__merge'
for chrom in dash3only.keys():
    dash3only[chrom].columns = columns
    dash3only[chrom] = dash3only[chrom][['CHROM', 'POS', 'ID', 'REF', 'ALT']]
    fdash3only[chrom].columns = columns
    fdash3only[chrom] = fdash3only[chrom][['CHROM', 'POS', 'ID', 'REF', 'ALT']]

dash3onlynogl = leftJoinsOnly(dash3only, gldict)
fdash3nogl = leftJoinsOnly(fdash3only, gldict)

cosmicdash3 = createInnerJoins(dash3onlynogl, cosmicdict)

for chrom in cosmicdash3.keys():
	cosmicdash3[chrom] = cosmicdash3[chrom].loc[cosmicdash3[chrom]['REF_x'] == cosmicdash3[chrom]['REF_y']]
	cosmicdash3[chrom] = cosmicdash3[chrom].loc[cosmicdash3[chrom]['ALT_x'] == cosmicdash3[chrom]['ALT_y']]

fcosmicdash3 = createInnerJoins(fdash3nogl, cosmicdict)

for chrom in fcosmicdash3.keys():
	fcosmicdash3[chrom] = fcosmicdash3[chrom].loc[fcosmicdash3[chrom]['REF_x'] == fcosmicdash3[chrom]['REF_y']]
	fcosmicdash3[chrom] = fcosmicdash3[chrom].loc[fcosmicdash3[chrom]['ALT_x'] == fcosmicdash3[chrom]['ALT_y']]

cosmicd3concat = concatDFDict(cosmicdash3)
fcosmicd3concat = concatDFDict(fcosmicdash3)
cosmicd3concat.to_csv("cosmicd2.csv", sep='\t')
fcosmicd3concat.to_csv("fcosmicd2.csv", sep='\t')

## both
# both = createInnerJoins(h2b2dict, ms053dict)
# fboth = createInnerJoins(h2b2dict, ms053fdict)