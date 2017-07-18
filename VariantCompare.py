#!/usr/bin/python3
import sys
import pandas as pd
import numpy as np
import math
import argparse

def separateByChrom(df, germline=False):
	chrDict = {}
	for chrom in df['Chromosome'].unique():
		tempDF = df.loc[df['Chromosome'] == chrom]
		if germline == True:
			tempDF.Chromosome = tempDF.Chromosome.apply(lambda x: x[3:])
			chrDict[chrom] = tempDF
		else:
			chrDict[chrom] = tempDF.loc[tempDF['Frequency'] < .5]
	return chrDict

def createInnerJoins(dfdict, dfdictR):
	chrDict = {}
	for chrom in dfdict.keys():
		chrDict[chrom] = dfdict[chrom].merge(dfdict[chrom], how='inner', on='Region')
	return chrDict

def compareToGermline(dfdict, germline):
	chrDict = {}
	for chrom in dfdict.keys():
		chrDict[chrom] = dfdict[chrom].merge(germline[chrom], how='left', on='Region', indicator='_merge')
		chrDict[chrom] = chrDict[chrom].loc[chrDict[chrom]['_merge'] == 'left_only']
	return chrDict

def compareToReport(dfdict, report):
	return

def concatDFDict(dfdict):
	concatDF = pd.concat([dfdict[chrom] for chrom in dfdict.keys()])
	return concatDF

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='compares variants between two variant files in CSV format')
	parser.add_argument('-l', '--left', help='Left frame file locaton', nargs=1, required=True, type=str)
	parser.add_argument('-r', '--right', help='Right frame file locaton', nargs=1, required=True, type=str)
	args = parser.parse_args()

	colheaders = [
		'Chromosome',
		'Region',
		'Type',
		'Reference',
		'Allele',
		'Count',
		'Coverage',
		'Frequency',
		'Probability',
		'Average Quality',
	]

	left = pd.read_csv(args.left[0], sep=',')
	right = pd.read_csv(args.right[0], sep=',', low_memory=True)
	germline = pd.read_csv("NGS/_Sequences/MS05germline.csv", sep=',')
	germline.columns = ['Chromosome', 'Region']
	germline.to_csv('testGL.csv', sep='\t')
	print('Creating germline dictionary')
	germlinedict = separateByChrom(germline, True)
	print('Generating left dictionary')
	leftDict = separateByChrom(left)
	print('Generating right dictionary')
	rightDict = separateByChrom(right)
	print('Merging dictionaries')
	mergeDict = createInnerJoins(leftDict, rightDict)
	print('Concatenating dictionaries and writing to file')
	concatDFDict(mergeDict).to_csv('NGS/_Sequences/varConcat.csv', sep='\t')
	print('Removing germline variants')
	noGLvar = compareToGermline(mergeDict, germlinedict)
	print('Concatenating dictionary')
	noGLvarConcat = concatDFDict(noGLvar)
	print('Writing to file')
	noGLvarConcat.to_csv('/DataAnalytics/NGS/_Sequences/noGLvarConcat.csv', sep='\t')