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

def matchRefAlt(dfdict):
	chrDict = dfdict
	for chrom in chrDict.keys():
		chrDict[chrom] = chrDict[chrom].loc[chrDict[chrom]['REF_x'] == chrDict[chrom]['REF_y']]
		chrDict[chrom] = chrDict[chrom].loc[chrDict[chrom]['ALT_x'] == chrDict[chrom]['ALT_y']]
	return chrDict

def setColumns(dfdict, merge=False, limit=True, cosmic=False):
	chrDict = dfdict
	columns = chrDict['1'].columns.values
	columns[0] = 'CHROM'
	columns[2] = 'ID'
	columns[3] = 'REF'
	columns[4] = 'ALT'
	if cosmic == True:
		columns[7] = 'CHROM_c'
	if(merge == True):
		columns[-1] = '__merge'
	for chrom in chrDict.keys():
		chrDict[chrom].columns = columns
		if limit == True:
			chrDict[chrom] = chrDict[chrom][['CHROM', 'POS', 'ID', 'REF', 'ALT']]
		elif cosmic == True:
			chrDict[chrom] = chrDict[chrom][['CHROM', 'POS', 'ID', 'REF', 'ALT', 'ID_y', 'REF_y', 'ALT_y', 'INFO']]
	return chrDict

## input data
germline = pd.read_csv("NGS/_Sequences/MS05germline.csv", sep=',')
germline.CHROM = germline.CHROM.apply(lambda x: x[3:])
tissue = pd.read_csv("NGS/_Sequences/MS05-Tissue_S3.smCounter.anno.vcf", sep='\t', skiprows=101)
columns = tissue.columns.values
columns[0] = 'CHROM'
tissue.columns = columns
tissue.CHROM = tissue.CHROM.apply(lambda x: x[3:])
organoid = pd.read_csv("NGS/_Sequences/MS05-Tumoroid-CellLine_S1.smCounter.anno.vcf", sep='\t', skiprows=101)
columns = organoid.columns.values
columns[0] = 'CHROM'
organoid.columns = columns
organoid.CHROM = organoid.CHROM.apply(lambda x: x[3:])

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
tissuedict = separateByChrom(tissue)
organoiddict = separateByChrom(organoid)
h2b2dict = separateByChrom(H2B_2)
ms053dict = separateByChrom(MS05_3)
cosmicdict = separateByChrom(cosmic)
ms053fdict = separateByChrom(MS053filtered)

## dash3 only
dash3only = leftJoinsOnly(h2b2dict, ms053dict)
dash3only = matchRefAlt(dash3only)
dash3only = setColumns(dash3only, merge=True, limit=True)
fdash3only = leftJoinsOnly(h2b2dict, ms053fdict)
fdash3only = matchRefAlt(fdash3only)
fdash3only = setColumns(fdash3only, merge=True, limit=True)
## remove germline
dash3onlynogl = leftJoinsOnly(dash3only, gldict)
fdash3nogl = leftJoinsOnly(fdash3only, gldict)
## cosmic
cosmicdash3 = createInnerJoins(dash3onlynogl, cosmicdict)
cosmicdash3 = matchRefAlt(cosmicdash3)

fcosmicdash3 = createInnerJoins(fdash3nogl, cosmicdict)
fcosmicdash3 = matchRefAlt(fcosmicdash3)
## concat and write to file
# cosmicd3concat = concatDFDict(cosmicdash3)
# fcosmicd3concat = concatDFDict(fcosmicdash3)
# cosmicd3concat.to_csv("cosmicd2.csv", sep='\t')
# fcosmicd3concat.to_csv("fcosmicd2.csv", sep='\t')

## dash2 only
dash2only = leftJoinsOnly(ms053dict, h2b2dict)
dash2only = matchRefAlt(dash2only)
dash2only = setColumns(dash2only, merge=True, limit=True)
fdash2only = leftJoinsOnly(ms053fdict, h2b2dict)
fdash2only = matchRefAlt(dash2only)
fdash2only = setColumns(fdash2only, merge=True, limit=True)
## remove germline
dash2onlynogl = leftJoinsOnly(dash2only, gldict)
fdash2nogl = leftJoinsOnly(fdash2only, gldict)
## cosmic
cosmicdash2 = createInnerJoins(dash2onlynogl, cosmicdict)
cosmicdash2 = matchRefAlt(cosmicdash2)

fcosmicdash2 = createInnerJoins(fdash2nogl, cosmicdict)
fcosmicdash2 = matchRefAlt(fcosmicdash2)
## concat and write to file
# cosmicd2concat = concatDFDict(cosmicdash2)
# fcosmicd2concat = concatDFDict(fcosmicdash2)

## both
both = createInnerJoins(h2b2dict, ms053dict)
both = matchRefAlt(both)
both = setColumns(both)
fboth = createInnerJoins(h2b2dict, ms053fdict)
fboth = matchRefAlt(fboth)
fboth = setColumns(fboth)

## remove germline
bothnogl = leftJoinsOnly(both, gldict)
fbothnogl = leftJoinsOnly(fboth, gldict)
