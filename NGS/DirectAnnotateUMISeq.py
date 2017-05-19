#!/usr/bin/python3


# IMPORTANT
# This is still too slow as it has a few redundant steps with regards to the SeqIO rec objects
# Don't use this, use the FastAnnotateUMISeq.py script
import os
import sys
import Bio
from Bio import SeqIO
import math
import numpy as np
import pandas as pd
import argparse
import time
##########################################
## Sequence manipulation
##

def findBarcodes(reads, chopoff=True):
    """
    Finds the barcodes (the first 12 bp of R2)
    If chopoff = True, then just grab the first 12.
    """
    if chopoff is True:
        if len(reads) > 23:
            if 'N' not in reads[0:24]:
                barcode = reads[0:13]
                cutseq = reads[24:len(reads)]
            else:
                barcode = 'N/A'
                cutseq = ''
        else:
            barcode = 'N/A'
            cutseq = ''
    # print(barcode)
    return [barcode, cutseq]

def phredtoAscii(qualityScores):
    """
    The phred quality scores are reported in numbers after being read. This creates 
    """
    asciiScore = ''
    for score in qualityScores:
        asciiScore += str(chr(score+33))
    return asciiScore

def annotateSeq(reads, lane, filename1='_tempR1_L', filename2='_tempR2_L',path='', hardCode=True):
    """
    Annotates the sequences (as best as possible).
    annotates the adapters, sample index (which it removes), R1 and R2 primers
    Find's UMI and adds it to the headers.

    """
    print('Running annotateSeq on ' + reads[0] + ' and ' + reads[1])
    #to capture reads that do not pass this step and write to a csv
    nobarcodes = []

    R1headers = []
    R1seq = []
    R1qual = []

    R2headers = []
    R2seq = []
    R2qual = []

    # opens both files
    # print(reads)
    with open(reads[0], 'rU') as handleR1, open(reads[1], 'rU') as handleR2, open(path+filename1+str(lane)+'.fastq', 'w') as R1handle, open(path+filename2+str(lane)+'.fastq', 'w') as R2handle:
        for (R1record, R2record) in zip(SeqIO.parse(handleR1, 'fastq'), SeqIO.parse(handleR2, 'fastq')):
            # creates temp variables to hold the headers and sequences
            tempR1 = R1record.seq
            tempR2 = R2record.seq
            if hardCode==True:
                tempR2 = findBarcodes(tempR2, chopoff=True)
            else:
                tempR2 = findBarcodes(tempR2, chopoff=False)
            # make sure R2 passes quality
            if tempR2[0] == 'N/A':
                # print('No barcode found')
                nobarcodes.append(R2record.description)
            else:
                #appends quality scores
                tempR1score = R1record.letter_annotations
                tempR1score = phredtoAscii(tempR1score['phred_quality'])
                tempR2score = R2record.letter_annotations
                tempR2score = phredtoAscii(tempR2score['phred_quality'][24:len(tempR2score['phred_quality'])])
                # writes to respective files
                R1handle.write(str('@'+R1record.description.replace(' ', ':')+':'+tempR2[0])+'\n'+str(tempR1)+'\n+\n'+tempR1score+'\n')
                # Write to R2
                R2handle.write(str('@'+R2record.description.replace(' ', ':')+':'+tempR2[0])+'\n'+str(tempR2[1])+'\n+\n'+tempR2score+'\n')
        # create pandas dataframes
        # annotatedSeqs = pd.DataFrame({
                                     # 'R1header': R1headers,
                                     # 'R1seq': R1seq,
                                     # 'R1qual': R1qual,
                                     # 'R2header': R2headers,
                                     # 'R2seq': R2seq,
                                     # 'R2qual': R2qual,
                                     # })
        # optional poor sequence log and annotatedSeqs to csv
        # with open('_NoAnnotatedSeq.csv', 'w') as file:
        #     for head in nobarcodes:
        #         file.write(head + '\n')
    print(str(len(nobarcodes)) +' reads with no/unreadable barcodes')

if __name__ == '__main__':
    # start time for amount of time it takes to run this
    starttime = time.time()

    parser = argparse.ArgumentParser(description='Processes Illumina NGS sequences into super reads')
    parser.add_argument('-l', '--lanes', nargs=1, required=False, help='number of lanes', type=int)
    parser.add_argument('-R', '--R1reads', nargs='*', required=False, help='path to R1 reads', type=str)
    parser.add_argument('-L', '--R2reads', nargs='*', required=False, help='path to R2 reads', type=str)
    parser.add_argument('-p', '--path', nargs=1, required=False, help='path to save', type=str)
    # parser.add_argument('')
    args = parser.parse_args()

    # The input files names for easy testing
    print("Setting input files")
    lanesSeq = []
    if args.lanes != None:
        if args.R1reads is None or args.R2reads is None :
            print('Missing reads')
        else:
            R1readstemp = args.R1reads
            R2readstemp = args.R2reads
        for x in range(0, args.lanes[0]):
            lanesSeq.append([R1readstemp[x], R2readstemp[x]])
    else:
        print('No inputs, using defaults')
        lanesSeq = [['_Sequences/MSO5_001_L1_R1.fastq', '_Sequences/MSO5_001_L1_R2.fastq'],
                ['_Sequences/MSO5_001_L2_R1.fastq', '_Sequences/MSO5_001_L2_R2.fastq'],
                ['_Sequences/MSO5_001_L3_R1.fastq', '_Sequences/MSO5_001_L3_R2.fastq'],
                ['_Sequences/MSO5_001_L4_R1.fastq', '_Sequences/MSO5_001_L4_R2.fastq']]


    print(lanesSeq)

    # import files for each lane and add them to ngsReads object
    for i in range(0, len(lanesSeq)):
        print('processing lane '+str(i))
        annotateSeq([lanesSeq[i][0], lanesSeq[i][1]], i, path=args.path[0])
    # print("creating sequence csv")
    # data.toCsv()

    print("Total run time: %s" % (time.time() - starttime))