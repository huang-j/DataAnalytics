import os
import sys
import Bio
from Bio import SeqIO
import math
import numpy as np
import pandas as pd
import argparse

##########################################
## Sequence manipulation
##

def findBarcodes(reads, chopoff=True):
    """
    Finds the barcodes (the first 12 bp of R2)
    If chopoff = True, then just grab the first 12.
    """
    if chopoff is True:
        if 'N' not in reads and len(reads) > 23:
            barcode = reads[0:13]
            cutseq = reads[24:len(reads)]
        else:
            barcode = 'N/A'
            cutseq = ''
    # print(barcode)
    return [barcode, cutseq]

def phredtoAscii(qualityScores):
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
    reads = reads
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
    print(reads)
    with open(reads[0], 'rU') as handleR1, open(reads[1], 'rU') as handleR2:
        for (R1record, R2record) in zip(SeqIO.parse(handleR1, 'fastq'), SeqIO.parse(handleR2, 'fastq')):
            # creates temp variables to hold the headers and sequences
            # sends to trimAdapters to remove adapters + common sequences
            print('records')
            print(R1record)
            print(R2record)
            print('\n')
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
                continue
            else:
                # appends the sequences seq array
                R1seq.append(str(tempR1))
                R2seq.append(str(tempR2[1]))
                # print(R2record.description)

                # appends headers
                R2headers.append(str(R2record.description+':'+tempR2[0]))
                R1headers.append(str(R1record.description+':'+tempR2[0]))
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
        with open('NoAnnotatedSeq.csv', 'w') as file:
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
        concat = pd.concat(self.read_dict)
        concat.to_csv('ngsReads.csv', sep='\t')
        return
    def addLane(self, lane, lane_dict):
        self.read_dict[lane] = lane_dict
    def toFastq(self, filename1='tempR1.fastq', filename2='tempR2.fastq'):
        """
        Creates a fastq file out of the read dictionary.
        Concatenates the files into a large R1 and R2 files respectively
        """
        # with open(filename1, 'w') as R1handle, open(filename2, 'w') as R2handle:
        #     for frame in self.read_dict:
        #         for row in self.read_dict[frame].itertuples():
        #             print(row)
        #             # Write to R1
        #             R1handle.write(str(row[1])+'\n'+str(row[3])+'\n+\n'+str(row[2])+'\n')
        #             # Write to R2
        #             R2handle.write(str(row[4])+'\n'+str(row[6])+'\n+\n'+str(row[5])+'\n')

        with open(filename1, 'w') as R1handle:
            for frame in self.read_dict:
                for row in self.read_dict[frame].itertuples():
                    # print(row)
                    # Write to R1
                    R1handle.write(str(row[1])+'\n'+str(row[3])+'\n+\n'+str(row[2])+'\n')

        with open(filename2, 'w') as R2handle:
            for frame in self.read_dict:
                for row in self.read_dict[frame].itertuples():
                    # print(row)
                    # Write to R2
                    R2handle.write(str(row[4])+'\n'+str(row[6])+'\n+\n'+str(row[5])+'\n')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processes Illumina NGS sequences into super reads')
    parser.add_argument('-l', '--lanes', nargs=1, required=True, help='number of lanes', type=int)
    # parser.add_argument('')

    # Generate ngsReads object
    data = ngsReads()

    # The input files names for easy testing
    lanes = [['Sequences\MSO5_001_L1_R1.fastq', 'Sequences\MSO5_001_L1_R2.fastq'],
             ['Sequences\MSO5_001_L2_R1.fastq', 'Sequences\MSO5_001_L2_R2.fastq'],
             ['Sequences\MSO5_001_L3_R1.fastq', 'Sequences\MSO5_001_L3_R2.fastq'],
             ['Sequences\MSO5_001_L4_R1.fastq', 'Sequences\MSO5_001_L4_R2.fastq']]

    # import files for each lane and add them to ngsReads object
    for i in range(0, len(lanes)):
        data.addLane(i + 1, annotateSeq([lanes[i][0], lanes[i][1]]))

    data.toFastq()
    data.toCsv()
