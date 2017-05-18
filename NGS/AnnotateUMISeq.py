#!/usr/bin/python3
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

def annotateSeq(reads, hardCode=True):
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
    with open(reads[0], 'rU') as handleR1, open(reads[1], 'rU') as handleR2:
        for (R1record, R2record) in zip(SeqIO.parse(handleR1, 'fastq'), SeqIO.parse(handleR2, 'fastq')):
            # creates temp variables to hold the headers and sequences
            # sends to trimAdapters to remove adapters + common sequences
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
                # appends the sequences seq array
                R1seq.append(str(tempR1))
                R2seq.append(str(tempR2[1]))
                # print(R2record.description)

                # appends headers
                R2headers.append(str('@'+R2record.description.replace(' ', ':')+':'+tempR2[0]))
                R1headers.append(str('@'+R1record.description.replace(' ', ':')+':'+tempR2[0]))
                # print(R2record.description + ':' + tempR2[0])

                #appends quality scores
                tempR1score = R1record.letter_annotations
                tempR1score = phredtoAscii(tempR1score['phred_quality'])
                tempR2score = R2record.letter_annotations
                tempR2score = phredtoAscii(tempR2score['phred_quality'][24:len(tempR2score['phred_quality'])])
                R1qual.append(tempR1score)
                R2qual.append(tempR2score)

        # create pandas dataframes
        annotatedSeqs = pd.DataFrame({
                                     'R1header': R1headers,
                                     'R1seq': R1seq,
                                     'R1qual': R1qual,
                                     'R2header': R2headers,
                                     'R2seq': R2seq,
                                     'R2qual': R2qual,
                                     })
        # optional poor sequence log and annotatedSeqs to csv
        with open('_NoAnnotatedSeq.csv', 'w') as file:
            for head in nobarcodes:
                file.write(head + '\n')

    return annotatedSeqs


##########################################
## ngsReads class
##

class ngsReads:
    def __init__(self):
        self.read_dict = {}
    def toCsv(self):
        """
        Concats all the reads and creates a csv
        """
        concat = pd.concat(self.read_dict)
        concat.to_csv('_ngsReads.csv', sep='\t')
        return
    def addLane(self, lane, lane_dict):
        """
        Adds lane to read_dict object
        """
        self.read_dict[lane] = lane_dict
    def toFastq(self, filename1='_tempR1.fastq', filename2='_tempR2.fastq', path=''):
        """
        Creates a fastq file out of the read dictionary.
        Concatenates the files into a large R1 and R2 files respectively
        """
        with open(path+filename1, 'w') as R1handle, open(path+filename2, 'w') as R2handle:
            for frame in self.read_dict:
                for row in self.read_dict[frame].itertuples():
                    # print(row)
                    # Write to R1
                    R1handle.write(str(row[1])+'\n'+str(row[3])+'\n+\n'+str(row[2])+'\n')
                    # Write to R2
                    R2handle.write(str(row[4])+'\n'+str(row[6])+'\n+\n'+str(row[5])+'\n')

        # with open(filename1, 'w') as R1handle:
        #     for frame in self.read_dict:
        #         for row in self.read_dict[frame].itertuples():
        #             # print(row)
        #             # Write to R1
        #             R1handle.write(str(row[1])+'\n'+str(row[3])+'\n+\n'+str(row[2])+'\n')

        # with open(filename2, 'w') as R2handle:
        #     for frame in self.read_dict:
        #         for row in self.read_dict[frame].itertuples():
        #             # print(row)
        #             # Write to R2
        #             R2handle.write(str(row[4])+'\n'+str(row[6])+'\n+\n'+str(row[5])+'\n')




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

    # Generate ngsReads object
    print("Creating ngsReads object")
    data = ngsReads()

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
    try:
        for i in range(0, len(lanesSeq)):
            print('adding lane '+str(i))
            data.addLane(i + 1, annotateSeq([lanesSeq[i][0], lanesSeq[i][1]]))
    except:
        print('Problem with inputs')
    print("creating fastq")
    data.toFastq(path=args.path[0])

    # print("creating sequence csv")
    # data.toCsv()

    print("Total run time: %s" % (time.time() - starttime))