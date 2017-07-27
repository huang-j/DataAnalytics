# coding: utf-8
import pandas as pd
import numpy as np
import math
import time
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

def setColumns(dfdict, merge=False, limit=True, cosmic=False, addValues=[]):
	chrDict = dfdict
	columns = chrDict['1'].columns.values
	columns[1] = 'POS'
	columns[3] = 'REF'
	columns[4] = 'ALT'
	if cosmic == False:
		columns[0] = 'CHROM'
		columns[2] = 'ID'
	if(merge == True):
		columns[-1] = '__merge'
	for chrom in chrDict.keys():
		chrDict[chrom].columns = columns
		if limit == True:
			chrDict[chrom] = chrDict[chrom][['CHROM', 'POS', 'ID', 'REF', 'ALT']]
		elif cosmic == True:
			chrDict[chrom] = chrDict[chrom][['CHROM', 'POS', 'ID_y', 'REF', 'ALT', 'INFO']]
		elif addValues != []:
			chrDict[chrom] = chrDict[chrom][['CHROM', 'POS', 'ID', 'REF', 'ALT'] + addValues]
	return chrDict

def writeTo(dfdict, location, name):
	for chrom in dfdict.keys():
		if dfdict[chrom].empty == False:
			dfdict[chrom].to_csv("VariantAnalysis/"+location+name+chrom+".csv", sep='\t')

starttime = time.time()
print('Starting')

print('Loading Data')
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
cosmic = pd.read_csv("VariantAnalysis/CosmicCodingMuts37.vcf", sep='\t', skiprows=13, low_memory=False)
columns = cosmic.columns.values
columns[0] = 'CHROM'
cosmic.columns = columns

print("--- %s seconds ---" % (time.time() - starttime))
print('Creating Dictionaries')
## generate dictionaries
gldict = separateByChrom(germline)
tissuedict = separateByChrom(tissue)
organoiddict = separateByChrom(organoid)
h2b2dict = separateByChrom(H2B_2)
ms053dict = separateByChrom(MS05_3)
cosmicdict = separateByChrom(cosmic)
ms053fdict = separateByChrom(MS053filtered)

print("--- %s seconds ---" % (time.time() - starttime))
print('Finding variants in Dash3 only')
## dash3 only
dash3only = leftJoinsOnly(ms053dict, h2b2dict)
# dash3only = matchRefAlt(dash3only)
dash3only = setColumns(dash3only, merge=True, limit=True)
fdash3only = leftJoinsOnly(ms053fdict, h2b2dict)

# fdash3only = matchRefAlt(fdash3only)
fdash3only = setColumns(fdash3only, merge=True, limit=True)
## remove germline
dash3onlynogl = leftJoinsOnly(dash3only, gldict)
fdash3nogl = leftJoinsOnly(fdash3only, gldict)
## cosmic
cosmicdash3 = createInnerJoins(dash3onlynogl, cosmicdict)
cosmicdash3 = matchRefAlt(cosmicdash3)
cosmicdash3 = setColumns(cosmicdash3, limit=False, cosmic=True)

fcosmicdash3 = createInnerJoins(fdash3nogl, cosmicdict)
fcosmicdash3 = matchRefAlt(fcosmicdash3)
fcosmicdash3 = setColumns(fcosmicdash3, limit=False, cosmic=True)

## concat and write to file
print('Writing to disk')
concatDFDict(cosmicdash3).to_csv("VariantAnalysis/Dash3/cosmicd3.csv", sep='\t')
concatDFDict(fcosmicdash3).to_csv("VariantAnalysis/Dash3/fcosmicd3.csv", sep='\t')

print("--- %s seconds ---" % (time.time() - starttime))
print('Finding variants in Dash2 only')

## dash2 only
dash2only = leftJoinsOnly(h2b2dict, ms053dict)
# dash2only = matchRefAlt(dash2only)
dash2only = setColumns(dash2only, merge=True, limit=True)
fdash2only = leftJoinsOnly(h2b2dict, ms053fdict)
# fdash2only = matchRefAlt(dash2only)
fdash2only = setColumns(fdash2only, merge=True, limit=True)
## remove germline
dash2onlynogl = leftJoinsOnly(dash2only, gldict)
fdash2nogl = leftJoinsOnly(fdash2only, gldict)
## cosmic
cosmicdash2 = createInnerJoins(dash2onlynogl, cosmicdict)
cosmicdash2 = matchRefAlt(cosmicdash2)
cosmicdash2 = setColumns(cosmicdash2, limit=False, cosmic=True)

fcosmicdash2 = createInnerJoins(fdash2nogl, cosmicdict)
fcosmicdash2 = matchRefAlt(fcosmicdash2)
fcosmicdash2 = setColumns(cosmicdash2, limit=False, cosmic=True)

## concat and write to file
print('Writing to disk')
concatDFDict(cosmicdash2).to_csv("VariantAnalysis/Dash2/cosmicd2.csv", sep='\t')
concatDFDict(fcosmicdash2).to_csv("VariantAnalysis/Dash2/fcosmicd2.csv", sep='\t')

print("--- %s seconds ---" % (time.time() - starttime))
print('Finding variants in both')
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

## cosmic
bothcosmic = createInnerJoins(bothnogl, cosmicdict)
fbothcosmic = createInnerJoins(fbothnogl, cosmicdict)

## concat
print('Writing to disk')
concatDFDict(bothcosmic).to_csv("VariantAnalysis/Both/bothcosmic.csv", sep='\t')
concatDFDict(fbothcosmic).to_csv("VariantAnalysis/Both/fbothcosmic.csv", sep='\t')

## compare all these to Tissue and Organoids
## not sure if I should run matchRefAlt given that there will be 3 sets provided

print("--- %s seconds ---" % (time.time() - starttime))
print('Comparing to tissue')
# Tissue:
# D3 only
tissueD3 = createInnerJoins(cosmicdash3, tissuedict)
ftissueD3 = createInnerJoins(fcosmicdash3, tissuedict)
writeTo(tissueD3, "Dash3/Tissue/Unfiltered/", "tissue")
writeTo(ftissueD3, "Dash3/Tissue/Filtered/", "ftissue")

# D2 only
tissueD2 = createInnerJoins(cosmicdash2, tissuedict)
ftissueD2 = createInnerJoins(fcosmicdash2, tissuedict)
writeTo(tissueD2, "Dash2/Tissue/Unfiltered/", "tissue")
writeTo(ftissueD2, "Dash2/Tissue/Filtered/", "ftissue")

# Both
tissueboth = createInnerJoins(bothcosmic, tissuedict)
ftissueboth = createInnerJoins(fbothcosmic, tissuedict)
writeTo(tissueboth, "Both/Tissue/Unfiltered/", "tissue")
writeTo(ftissueboth, "Both/Tissue/Filtered/", "ftissue")

print("--- %s seconds ---" % (time.time() - starttime))
print('Comparing to organoids')
# Organoids
# D3 only
organoidD3 = createInnerJoins(cosmicdash3, organoiddict)
forganoidD3 = createInnerJoins(fcosmicdash3, organoiddict)
writeTo(organoidD3, "Dash3/Organoid/Unfiltered/", "organoid")
writeTo(forganoidD3, "Dash3/Organoid/Filtered/", "organoid")

# D2 only
organoidD2 = createInnerJoins(cosmicdash2, organoiddict)
forganoidD2 = createInnerJoins(fcosmicdash2, organoiddict)
writeTo(organoidD2, "Dash2/Organoid/Unfiltered/", "organoid")
writeTo(forganoidD2, "Dash2/Organoid/Filtered/", "organoid")

# Both
organoidboth = createInnerJoins(bothcosmic, organoiddict)
forganoidboth = createInnerJoins(fbothcosmic, organoiddict)
writeTo(organoidboth, "Both/Organoid/Unfiltered/", "organoid")
writeTo(forganoidboth, "Both/Organoid/Filtered/", "organoid")

print('Total runtime')
print("--- %s seconds ---" % (time.time() - starttime))