#!/bin/bash
echo "Running AnnotateUMISeq.py"
lanes=1
sub_dir="/media/jonathan/ANTHONY/jonathan/MS05_H2B_exoDNA-42887042/"
R1files0="MS05-H2B-exoDNA_S2_L001_R1_001.fastq"
R1files1="MS05-H2B-exoDNA_S2_L002_R1_001.fastq"
R1files2="MS05-H2B-exoDNA_S2_L003_R1_001.fastq"
R1files3="MS05-H2B-exoDNA_S2_L004_R1_001.fastq"

R2files0="MS05-H2B-exoDNA_S2_L001_R2_001.fastq"
R2files1="MS05-H2B-exoDNA_S2_L002_R2_001.fastq"
R2files2="MS05-H2B-exoDNA_S2_L003_R2_001.fastq"
R2files3="MS05-H2B-exoDNA_S2_L004_R2_001.fastq"

./AnnotateUMISeq.py -l $lanes -R $sub_dir$R1files0 $sub_dir$R1files1 $sub_dir$R1files2 $sub_dir$R1files3 -L $sub_dir$R2files0 $sub_dir$R1files1 $sub_dir$R1files2 $sub_dir$R1files3 -p $sub_dir