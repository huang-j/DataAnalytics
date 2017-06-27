#!/usr/bin/python3
# Instead of going through an iterative Seq.IO record formula, this will go through plaintext with biopython handling some other issues
import os
import sys
import Bio
from Bio import SeqIO
from Bio.SeqIO.QualityIO import FastqGeneralIterator
import time
import argparse


def findBarcodes(reads, chopoff=True):
    """
    Finds the barcodes (the first 12 bp of R2)
    If chopoff = True, then just grab the first 12.
    """
    if chopoff is True:
        if len(reads) > 23:
            if 'N' not in reads[0:24]:
                barcode = reads[0:13]
            else:
                barcode = 'N/A'
        else:
            barcode = 'N/A'
    # print(barcode)
    return barcode

# Annotate Seqs

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
        for (R1record, R2record) in zip(FastqGeneralIterator(handleR1), FastqGeneralIterator(handleR2)):
            barcode = findBarcodes(R2record[1], chopoff=hardCode)
            # make sure R2 passes quality
            if barcode== 'N/A':
                # print('No barcode found')
                nobarcodes.append(R2record[0])
            else:
                # writes to respective files
                R1handle.write(str('@'+R1record[0].replace(' ', ':')+':'+barcode)+'\n'+R1record[1]+'\n+\n'+R1record[2]+'\n')
                # Write to R2
                R2handle.write(str('@'+R1record[0].replace(' ', ':')+':'+barcode)+'\n'+R2record[1][24:]+'\n+\n'+R2record[2][24:]+'\n')





##############################
## Init

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

    print("Start time: %s" % starttime)
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
        print("lane processing time: %s" % (time.time() - starttime))
    # print("creating sequence csv")
    # data.toCsv()

    print("Total run time: %s" % (time.time() - starttime))