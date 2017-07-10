#!/usr/bin/env/python
import sys
import pandas as pd
import numpy as np
import math
import argparse

def separateByChrom(df):
	chrDict = {}
	for chrom in df.Chromosome.unique:
		chrDict.chrom = df.loc[df['Chromosome'] == chrom]
	return chrDict

def createInnerJoins(dfdict, dfdictR):
	chrDict = {}
	for chrom in dfdict.keys():
		chrDict.chrom = dfdict.chrom.merge(dfdict.chrom, how='inner', on='Region') 
	return chrDict

def compareToGermline(dfdict, germline):
	chrDict = {}
	for chrom in dfdict.keys():
		chrDict.chrom = dfdict.chrom.merge(germline.chrom, how='left', on='Region', indicator=True)
		chrDict.chrom = chrDict.chrom.loc[chrDict.chrom['_merge'] == 'left_only']
	return chrDict

def compareToReport(dfdict, report):
	return

def concatDFDict(dfdict):
	concatDF = pd.concat([dfdict.chrom for chrom in dfdict.keys()])
	return concatDF

if __name__ = '__main__':
	parse = argparse.ArgumentParser(description='compares variants between two variant files in CSV format')
    parser.add_argument('-l', '--left', description='Left frame file locaton', nargs=1, required=True, type=str)
    parser.add_argument('-r', '--right', description='Right frame file locaton', nargs=1, required=True, type=str)
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

    left = pd.read_csv(args.left[0], sep=',', names=colheaders, low_memory=False)
    right = pd.read_csv(args.right[0], sep='\t', names=colheaders, low_memory=False)
    germline = pd.read_csv('/DataAnalytics/NGS/_Sequences/MS05germline.csv', sep=',')
    germline.columns = ['Chromosome', 'Region']
    germlinedict = separateByChrom(germline)

    leftDict = separateByChrom(left)
    rightDict = separateByChrom(right)
    mergeDict = createInnerJoins(leftDict, rightDict)
    noGLvar = compareToGermline(mergeDict, germlinedict)
    noGLvarConcat = concatDFDict(noGLvar)
    
    noGLvarConcat.to_csv('/DataAnalytics/NGS/_Sequences/noGLvarConcat.csv', sep='\t')