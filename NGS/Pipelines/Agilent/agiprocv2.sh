#!/bin/bash
# Run Agilent pipeline 
# Trim FQ (SurecallTrimmer) -> Alignment (bwa-mem) -> Barcoding (LocatIt)
usage() {
    echo "Usage: $0 [-d <string>] [-l <string>] [-b <string>]"
    echo "        -d bottom directory"
    echo "        -l file containing names of samples to be used"
    echo "                e.g. MK29-T_S4"
    echo "        -b bed file"
    exit 1;
}
while getopts ":d:l:b:" o; do
    case "${o}" in
        d)
            d=${OPTARG}
            ;;
        l)
            l=${OPTARG}
            ;;
        b)
            b=${OPTARG}
	    ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))
# if [ -z "${d}" ] || [ -z "${l}" ]; then
if [ -z "${l}" ]; then
    usage
fi
if [ -z "${d}" ]; then
    d="FNA_Molecular_Barcoding_02162018"
fi
if [ -z "${b}" ]; then
    usage
    #  b="Agilent/CREv2/S30409818_Covered.bed"
fi
SECONDS=0
echo "d = ${d}" > ${l%.txt}_log.txt
echo "l = ${l}" >> ${l%.txt}_log.txt
echo "b = ${b}" >> ${l%.txt}_log.txt

SurecallTrimer="Agilent/SurecallTrimmer_v4.0.1.jar"
LocatIt="Agilent/LocatIt_v4.0.1.jar"

echo "Trimming fastq" >> ${l%.txt}_log.txt
mkdir ${d}/Trimmed
for s in $(cat ${l}); do
    echo "Sample input: ${s}" >> ${l%.txt}_log.txt
    if [ ! -f ${d}/Trimmed/${s}/${s}_R1_trim.fastq.gz ] ; then
        inputR1=${d}/fastq_files/${s}_R1_001.fastq.gz
        inputR3=${d}/fastq_files/${s}_R3_001.fastq.gz

        java -jar ${SurecallTrimer} -fq1 ${inputR1} -fq2 ${inputR3} -xt -out_loc ${d}/Trimmed/${s}/ >> ${l%.txt}_log.txt
        mv "${d}/Trimmed/${s}/${s}"*"_R1"*".fastq.gz" "${d}/Trimmed/${s}/${s}_R1_trim.fastq.gz"
        mv "${d}/Trimmed/${s}/${s}"*"_R3"*".fastq.gz" "${d}/Trimmed/${s}/${s}_R3_trim.fastq.gz"
    else 
       echo "File already trimmed" >> ${l%.txt}_log.txt
    fi
    duration=$((${SECONDS}/60))
    # echo "Time elapsed: ${duration} minutes"
    echo "Time elapsed: ${duration} minutes" >> ${l%.txt}_log.txt 
done
mkdir ${d}/Bams
mkdir ${d}/Bams/${s}  
echo "Aligning" >> ${l%.txt}_log.txt
for s in $(cat ${l}); do
    echo "Sample input: ${s}" >> ${l%.txt}_log.txt
    if [ ! -f ${s}.bam ] || [ ! -f ${d}/Bams/${s}/${s}.bam ] ; then
	mkdir ${d}/tmp
        ## can edit number of threads based on system. Should probably update to around 4-6 
        ## bwa mem -t 6 -M -I 200,100 -B 4 -A 1.0 -w 100 -k 19 -R "@RG\tID:${s}\tSM:${s}\tLB:AgilentSureCall\tPL:Illumina\tPU:Unknown" ref/hg19_k/hg19.fasta ${d}/Trimmed/${s}/${s}_R1_trim.fastq.gz ${d}/Trimmed/${s}/${s}_R3_trim.fastq.gz | samtools sort -o ${d}/Bams/${s}/${s}.bam -
        bwa mem -t 6 -M -R "@RG\tID:${s}\tSM:${s}\tLB:AgilentSureCall\tPL:Illumina\tPU:Unknown" ref/hg19_k/hg19.fasta ${d}/Trimmed/${s}/${s}_R1_trim.fastq.gz ${d}/Trimmed/${s}/${s}_R3_trim.fastq.gz | samtools sort -n -T ${d}/tmp/${s}.tmp.bam -@ 6 -o ${d}/Bams/${s}/${s}.bam -
    else
        echo "File already aligned" >> ${l%.txt}_log.txt
    fi
    duration=$((${SECONDS}/60))
    # echo "Time elapsed: ${duration} minutes"
    echo "Time elapsed: ${duration} minutes" >> ${l%.txt}_log.txt
done

echo "Processing Barcodes" >> ${l%.txt}_log.txt
for s in $(cat ${l}); do
    if [ ! -f ${d}/Bams/${s}.umi.bam ] ; then
        inputR2=${d}/fastq_files/${s}_R2_001.fastq.gz
    
        # mv ${s}.bam ${d}/Bams/${s}/${s}.bam

        java -Xmx100G -jar ${LocatIt} \
        -X ${d}/temp \
        -q 0 \
        -m 1 \
        -U \
        -IB \
        -OB \
	-r \
        -i \
        -c 2500 \
        -l ${b} \
        -o ${d}/Bams/${s}/${s}.umi.bam \
        ${d}/Bams/${s}/${s}.bam \
        ${inputR2} >> ${l%.txt}_log.txt
# keeps the old bam (non-barcoded)
    else
	echo "Already processed barcodes" >> ${l%.txt}_log.txt
    fi
    if [ ! -f ${d}/Bams/${s}/${s}.umi.sorted.bam ] ; then
	echo "Sorting..." >> ${l%.txt}_log.txt
    	samtools sort -T ~/tmp/${s}tmp.bam -@ 6 -o ${d}/Bams/${s}/${s}.umi.sorted.bam ${d}/Bams/${s}/${s}.umi.bam
	samtools index ${d}/Bams/${s}/${s}.umi.sorted.bam
	if [ -f ${d}/Bams/${s}/${s}.umi.sorted.bam ] ; then
    		rm ${d}/Bams/${s}/${s}.umi.bam
	fi
    fi
    duration=$((${SECONDS}/60))
    echo "Time elapsed: ${duration} minutes" >> ${l%.txt}_log.txt
done
