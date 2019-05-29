#!/usr/bin/env Rscript
## with BQSR adjusted and combined bams
library(ggplot2)
library(ComplexHeatmap)
library(data.table)
library(scales)
library(circlize)
library(dplyr)
library(RColorBrewer)
library(stringr)
## Genelist
genelist <- fread("~/rsrch/Agilent/FNAgenelist.csv")
# genelist <- fread("~/rsrch/actiongenelist.csv")
geneorder = genelist$Gene
gllist <- fread("~/rsrch/Agilent/glgenelist.csv")
cosmicfilter = 5

## remove fields function
removeFields <- function(dt){
  dt <- dt[, lapply(.SD, as.character), by=c("Chr", "Start")]
  remove <- c("Otherinfo","V57","V58","V59","V60","V61","V62","V63","V64","V65","V66","V67","V68","V69", "Alter","Depth","MAF","log2Depth","Depth.z", "sift", "poly", "lrt", "taste", "provean", "vest", "cadd", "fathmm", "gerp", "siphy", "Alter1", "Alter2", "Depth1", "Depth2")
  return(dt[, -..remove])
}

## SureCall
sureCall <- function(tumor, normal){
  if(is.na(tumor)){
    stop("Missing Tumor File")
  } else if(is.na(normal) | normal == FALSE){
    tumor <- fread(tumor, sep="\t")
    tumor <- tumor[, c("Alt.tumor.SC", "Depth.tumor.SC", "MAF.tumor.SC") := .(Alter, Depth, MAF)] %>% removeFields
    return(tumor)
  }
  tumor <- fread(tumor, sep="\t")
  tumor <- tumor[, c("Alt.tumor.SC", "Depth.tumor.SC", "MAF.tumor.SC") := .(Alter, Depth, MAF)] %>% removeFields
  normal <- fread(normal, sep="\t")
  normal <- normal[, c("Alt.normal.SC", "Depth.normal.SC", "MAF.normal.SC") := .(Alter, Depth, MAF)] %>% removeFields
  sample <- merge(tumor, normal, all.x=TRUE)
  sample[, `:=`(Germline = ifelse(is.na(MAF.normal.SC), "0", ifelse(MAF.normal.SC > 0.2, "1", "0")))]
  return(sample)
}

Mutect2 <- function(path){
  sample <- fread(path, sep="\t")
  sample <- sample[, c("Alt.Mutect", "Depth.Mutect", "MAF.Mutect") := .(Alter, Depth, MAF)]  %>% removeFields
  return(sample)
}

MuSE <- function(path){
  sample <- fread(path, sep="\t")
  sample <- sample[, c("Alt.MuSE", "Depth.MuSE", "MAF.MuSE") := .(Alter, Depth, MAF)]  %>% removeFields
  return(sample)
}

## function to find intersection between all three
pairedConcensusMuts <- function(surecall, mutect, muse){
  xsection <- Reduce(function(x,y) merge(x, y, all=TRUE), list(surecall, mutect, muse))
  ## take the genes that are shared in 2 or more
  xsection[, `:=`(SC=ifelse(is.na(Alt.tumor.SC), 0, 1), Mutect=ifelse(is.na(Alt.Mutect), 0, 1), Muse=ifelse(is.na(Alt.MuSE), 0, 1))]
  # xsection <- xsection[sum(SC, Mutect, Muse) > 1] ## do this later
  return(xsection)
}

singleConcensusMuts <- function(surecall, mutect){
  xsection <- merge(surecall, mutect)
  xsection[, `:=`(xsection = 2)]
  return(xsection)
}

rmeans <- function(x, y){
  if (is.na(x) & is.na(y)) {
    return(0)
  }
  return((as.numeric(x) + as.numeric(y))/2)
}

## condense to hm format
collapseHM <- function(dt, name){
  dt <- dt[keep == 1, .(tumor = paste(ExonicFunc.refGene, collapse=";")), by=Gene.refGene]
  colnames(dt) <- c("Gene", name)
  condensed <- dt[genelist, on="Gene"]
  setkey(condensed, "Gene")
  return(condensed[, .SD[, 1:2]])
}
## label splice sites, insertions and deletions / frameshifts
annotateNonSnp <- function(Ref, Alt, MutFunc, Reg){
  # check for stuff we dont want to change
  if (MutFunc %in% c("nonsynonymous SNV", "stopgain", "synonymous SNV", "unknown", "stoploss")) {
    return(MutFunc)
  } else if (MutFunc == ".") { #only need to check the unlabeled ones
    # splice sites easy
    if (Reg == "splicing") {return("splice site")}
    # deletions
    if ((nchar(Ref) > nchar(Alt)) | Alt == "-") {
      if( (nchar(Ref) - nchar(gsub("-", "", Alt))) %% 3 == 0 ) { return("indel") }
      else { return("frameshift") }
      #insertions
    } else if((nchar(Ref) < nchar(Alt)) | Ref =="-") {
      if( (nchar(Alt) - nchar(gsub("-", "", Ref))) %% 3 == 0) { return("indel") }
      else { return("frameshift") }
    }
  } else if (is.element(MutFunc, c("frameshift deletion", "frameshift insertion"))) {
    return("frameshift")
  } else if (is.element(MutFunc, c("nonframeshift deletion", "nonframeshift insertion"))) {
    return("indel")
  }
  return(MutFunc)
}

annotateGermline <- function(dt){
  # dt[, `:=`(Germline = (ifelse(MAF > 0.25, "HaplotypeCaller", ifelse(Germline == "1", "SureCall", "0")) ) )]
  # dt[, `:=`(Germline = ifelse(MAF > 0.25 & Germline == "1", "1","0") ) ]
  dt[, `:=`(Germline = ifelse(Germline == "1", ifelse(MAF > 0.25 | !is.element(ExonicFunc.refGene,c("nonsynonymous SNV", "synonymous SNV")), "1", "0"  ),"0") ) ]
  ## removed  & Gene.refGene %in% gllist$Gene
  return(dt)
}

## This needs to do two things
## assign germline variants based off of the haplotype caller if it is in the PBMC's
## and remove artifacts and stuff based on stuff found within everything else.
PoNFilter <- function(dt, PoN, samp, paired){
  dt[, End := as.numeric(End)]
  temp <- merge(dt, PoN[grepl(samp, variable)], by=c("Chr", "Start","End", "Ref", "Alt", "Func.refGene", "Gene.refGene", "ExonicFunc.refGene"), all.x = TRUE)
  temp <- temp[is.na(freq) | 
                 (freq < 0.1 & avg.MAF > .25) ]
  temp[, ExonicFunc.refGene := mapply(annotateNonSnp, Ref, Alt, ExonicFunc.refGene, Func.refGene)]
  if(paired){
    temp <- annotateGermline(temp)
    temp[, ExonicFunc.refGene := ifelse(!is.na(Germline) & Germline != "0", ifelse(ExonicFunc.refGene == "synonymous SNV", "Germline - synonymous", "Germline"), ExonicFunc.refGene)] 
    ## final filter
    temp[, `:=`(xsection = sum(SC, Mutect, Muse) ), by=.(Chr, Start, End, Ref, Alt)]
    temp[, `:=`(keep = ifelse(!is.na(Germline) & Germline != "0", 1, ifelse(xsection > 1, 1, 0)))]
  } else {
    temp[, `:=`(keep = 1)]
  }
  temp <- temp[, .SD[1], .(Chr, Start, End, Alt)]
  write.table(temp, paste0("~/rsrch/Agilent/FNAHMintermediates/", samp, ".txt"), sep="\t", quote = FALSE, row=FALSE )
  return(temp)
}

## Mutational Burden from SNV calls and stuff unsure whether or not to keep non-SNVs (indels etc.)
## makes more sense to do all mutations
## No CNVs  
mutBurden <- function(dt, name){
  temp <- dt[keep == 1, .N, by=ExonicFunc.refGene]
  colnames(temp) <- c("Mut.Type", name)
  return(temp)
}

## New
## split data into germline tumor pairs as well as individual tumors.
args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
} else if (length(args)==1) {
  # default output file
  args[2] = "~/rsrch/Agilent/HCnormals/WEShaplotypes.txt"
}
args[2] = "~/rsrch/Agilent/HCnormals/WEShaplotypes.txt"
## read in file paths as a dataframe
files <- fread("~/rsrch/Agilent/FNAsnvpaths2.csv")
CNV <- fread("~/rsrch/CNV/FNA_v1/cnvX4082019/allSamps.txt", sep="\t")
CNV <- CNV[Call != "Call" & !is.na(Gene)]
CNV[, sample_id := sapply(sample_id, function(x) str_replace(x, "-", "_"))]
## Other files to read in:
PoN <- fread(args[2], sep="\t")
PoN <- PoN[!is.element(variable, c("BW13-PBMC_S2", "BW13_PBMC_reseq_S4", "MK248-PBMC_S1", "MK279-GL_S8", "MKC27-PBMC_S3", "MKC37-GL_S1", "WB17-GL_S2", "WB23-GL_S2", "WB26-PBMC_S5", "WB28-GL_S3", "WB30-GL_S2", "GV79-GL_S5", "MK336-GL_S4"))]
# rmcols <- c("INFO", "FORMAT", "variable", "value")
# rmcols <- c("INFO", "FORMAT")
# PoN <- PoN[, -..rmcols]
# PoN[, End := as.character()]

# Idea is to do things in two parts, first Paired, then unpaired
# weird exception is non-enriched samples that need something else.

##############
### Paired
# several steps needed to process the data. SureCall needs to be filtered against its normal. 
# Then comparisons must be made with MuSE and Mutect2. Germline calls will be based off the normal in surecall + haplotypecaller
# Final output will be written to a file for checking for inbetweens
paired <- list()
mutburden <- list()
for (f in  files[(Paired) & !grepl("NE", Sample), Sample] ) {
  # print(files[Sample == eval(f)])
  print(f)
  if(f %in% c("WB21","MK282_T", "MKC27_T2", "MK86_T", "MK86")){
    ##| !is.element(f, c("MK267"))
    next
  }
  s_id <- files[Sample == eval(f), SC_tumor] %>% strsplit(split = "/") %>% unlist
  s_id <- s_id[3] %>% strsplit(split="_[0-9][0-9]") %>% unlist
  s_id <- s_id[1]
  print(s_id)
  if (f == "GV79") {
    s_id = "GV79_T_S6"
  }
  sc <- sureCall(tumor = paste0("~/rsrch/Agilent/",files[Sample == eval(f), SC_tumor]),
                 normal = paste0("~/rsrch/Agilent/",files[Sample == eval(f), SC_normal]) )
  mut <- Mutect2(paste0("~/rsrch/Agilent/",files[Sample == eval(f), Mutect2] ))
  muse <- MuSE(paste0("~/rsrch/Agilent/",files[Sample == eval(f), MuSE]))
  dt <- pairedConcensusMuts(sc, mut, muse) %>% PoNFilter(PoN = PoN, samp = f, paired=TRUE)
  mb <- mutBurden(dt, f)
  mutburden <- append(mutburden, list(mb))
  cnvsamp <- CNV[sample_id == eval(s_id) & is.element(Call, c("+", "-")), .(Gene, Call)]
  print(head(cnvsamp))
  colnames(cnvsamp) <- c("Gene.refGene", "ExonicFunc.refGene")
  if(f %in% c("MK86")){
    cnvsamp[, keep := 0]
  } else {
    cnvsamp[, keep := 1] 
  }
  dt <- rbind(dt[ExonicFunc.refGene != "Germline - synonymous", .SD[1], by=.(Start, End)], cnvsamp, fill=TRUE)
  cl <- dt %>% collapseHM(name=f)
  
  paired <- append(paired, list(cl))
}
pairdt <- Reduce(function(x, y) merge(x,y, by="Gene"), paired)

####### unpaired
unpaired <- list()
for (f in  files[!(Paired) & !grepl("NE", Sample), Sample] ) {
  # print(files[Sample == eval(f)])
  print(f)
  if(f %in% c("WB21", "DH07-2")){
    next
  }
  s_id <- files[Sample == eval(f), SC_tumor] %>% strsplit(split = "/") %>% unlist
  s_id <- s_id[3] %>% strsplit(split="_[0-9][0-9]") %>% unlist
  s_id <- s_id[1]
  print(s_id)
  sc <- sureCall(tumor = paste0("~/rsrch/Agilent/",files[Sample == eval(f), SC_tumor]), normal = FALSE)
  mut <- Mutect2(paste0("~/rsrch/Agilent/",files[Sample == eval(f), Mutect2] ))
  dt <- singleConcensusMuts(sc, mut) %>% PoNFilter(PoN = PoN, samp = f, paired =FALSE)
  mb <- mutBurden(dt, f)
  mutburden <- append(mutburden, list(mb))
  cnvsamp <- CNV[sample_id == eval(s_id) & is.element(Call, c("+", "-")), .(Gene, Call)]
  print(head(cnvsamp))
  colnames(cnvsamp) <- c("Gene.refGene", "ExonicFunc.refGene")
  cnvsamp[, keep := 1]
  dt <- rbind(dt[, .SD[1], by=.(Start, End)], cnvsamp, fill=TRUE)
  unpaired <- append(unpaired, list(dt %>% collapseHM(name=f)))
}
unpairdt <- Reduce(function(x, y) merge(x,y, by="Gene"), unpaired)
TMB <- Reduce(function(x, y) merge(x,y, by="Mut.Type", all=TRUE), mutburden)

tmb.m <- melt(TMB[!is.element(Mut.Type, c("Germline", "Germline - synonymous" , "unknown"))], id.vars = "Mut.Type") %>% dcast(variable ~ Mut.Type)
tmb.m <- as.data.frame(tmb.m)
rownames(tmb.m) <- tmb.m$variable
tmb.m$variable <- NULL
tmb.m[is.na(tmb.m)] <- 0
write.table(tmb.m, "~/rsrch/Agilent/FNA_SNV_v2/TumorBurden.txt", sep="\t")

#### Create Heatmap
## For now we'll collapse the two tables
# m <- merge(tpairs, tonly, on="Gene")
# m <- m[!m[,sum(is.na(.SD)) == length(.SD), Gene]$V1] %>% as.data.frame
allsamps <- merge(pairdt, unpairdt)
## manual changes to some MK158
allsamps[Gene == "KRAS", MK158 := "nonsynonymous SNV"]

m <- as.data.frame(allsamps)
row.names(m) <- m$Gene
m$Gene <- NULL
m <- as.matrix(m)
sampledata <- fread("~/rsrch/Agilent/FNA_annnotations.csv")
sampledata <- sampledata[Sample != "MK86"]
sampnames <- colnames(m)
sampledata <- sampledata[order(match(Sample, sampnames))]

## colors
stagecolor <- brewer.pal(4, "Dark2")
gendercolor <- brewer.pal(3, "PRGn")

### trial
# colors = brewer.pal(8, "Set1")
# abcolors = brewer.pal(3, "Set2")
# topannocolor = c(colors[5], colors[7], colors[2], colors[1], colors[6], colors[3])
# col = c(stopgain = colors[1], "nonsynonymous SNV" = colors[2], stoploss = colors[6], "splice site"=colors[4], "frameshift"=colors[5], "synonymous SNV" = colors[3], "indel" = colors[7], Germline = "black", "+" = abcolors[2], "-" = abcolors[1], "cnloh" = abcolors[3])
## new
colors = brewer.pal(10, "Paired")
col = c("nonsynonymous SNV" = colors[4], "synonymous SNV" = colors[3],
        "+" = colors[6], "-" = colors[2],
        frameshift = colors[10], indel=colors[9],
        stopgain=colors[8], stoploss=colors[7],
        "splice site" = colors[1], Germline = "black")
topannocolor = c(colors[10], colors[9], colors[4], colors[8], colors[7], colors[3])
# heatmap stuff
topAnnotation <- HeatmapAnnotation(df = sampledata[!is.element(Sample, c("MK282-E")), .(Gender, Age, Stage, Sample.Type)], samp_mut = anno_barplot(as.matrix(tmb.m/67.3), which = "column", border = FALSE, axis=TRUE, gp = gpar(fill = topannocolor)),
                                   col = list( Stage = c( "Metastatic" = stagecolor[1], "Localized" =stagecolor[2]),
                                               Age =colorRamp2(c( floor(min(sampledata$Age)/10)*10, ceiling(max(sampledata$Age/10))*10 ), c("#2166AC", "#B2182B")),
                                               Gender = c("Female"=gendercolor[1], "Male"=gendercolor[3])),
                                   annotation_height = unit(c(.5, .5, .5, .5, 3), c("cm","cm","cm","cm","cm")))
# topAnnotest <- HeatmapAnnotation(samp_muts = anno_barplot(as.matrix(test2), which = "column", border = FALSE, gp = gpar(fill=col), axis = TRUE) )
# barplotAnnotation <- HeatmapAnnotation(samp_muts = anno_oncoprint_barplot())
## setup heatmap
alter_fun = list(
  background = function(x, y, w, h) {
    grid.rect(x, y, w-unit(0.5, "mm"), h-unit(0.5, "mm"), gp = gpar(fill = "#CCCCCC", col = NA))
  },
  "+" = function(x, y, w, h) {
    grid.rect(x, y, w-unit(0.5, "mm"), h-unit(0.5, "mm"), gp = gpar(fill = colors[6], col = NA))
  },
  "-" = function(x, y, w, h) {
    grid.rect(x, y, w-unit(0.5, "mm"), h-unit(0.5, "mm"), gp = gpar(fill = colors[2], col = NA))
  },
  "splice site" = function(x, y, w, h) {
    grid.rect(x, y, w*0.2, h-unit(0.5, "mm"), gp = gpar(fill = colors[1], col = NA))
  },
  "indel" = function(x, y, w, h) {
    grid.rect(x, y, w*0.2, h-unit(0.5, "mm"), gp = gpar(fill = colors[9], col = NA))
  },
  "frameshift" = function(x, y, w, h) {
    grid.rect(x, y, w*0.2, h-unit(0.5, "mm"), gp = gpar(fill = colors[10], col = NA))
  },
  "synonymous SNV" = function(x, y, w, h) {
    grid.rect(x, y, w*.5, h*.5, gp = gpar(fill = colors[3], col = NA))
  },
  "nonsynonymous SNV" = function(x, y, w, h) {
    grid.rect(x, y, w*.5, h*.5, gp = gpar(fill = colors[4], col = NA))
  },
  stoploss = function(x, y, w, h) {
    grid.rect(x, y, w*.5, h*.5, gp = gpar(fill = colors[7], col = NA))
  },
  stopgain = function(x, y, w, h) {
    grid.rect(x, y,w*.5, h*.5, gp = gpar(fill = colors[8], col = NA))
  },
  Germline = function(x, y, w, h) {
    grid.rect(x, y, w*0.2, h*0.33, gp = gpar(fill = "black", col = NA))
  }
)
genelist <- fread("~/rsrch/Agilent/FNAgenelist.csv")
# genelist <- fread("~/rsrch/actiongenelist.csv")
geneorder = genelist$Gene
op <- oncoPrint(m, get_type = function(x) strsplit(x, ";")[[1]],
                alter_fun = alter_fun, col = col, show_column_names = TRUE, row_names_side = "right", show_pct = TRUE, top_annotation = topAnnotation,## top_annotation_height = unit(3, "cm"),
                # row_order = c("KRAS", "TP53", "SMAD4", "CDKN2A", "BRCA2", "GNAS",  "TGFBR2", "ARID1A", "BRCA1",  "CHD4",   "EEF2",   "ERBB2",  "FBXW7",  "ITPR3",  "KALRN",  "KMT2D",  "PRSS1",  "SORCS1", "TGFBR1", "STK11",  "ACVR2A","ATM",    "BRAF",   "DISP2",  "GATA6",  "HIVEP1", "KDM6A",  "L1CAM",  "MAP2K4", "MARK2",  "MET",    "MSH2",   "MYC",    "PIK3CA", "PMS2",   "RNF213", "RNF43",  "ROBO2",  "SF3B1",  "SIN3B",  "SMARCA4","TLE4", "TRIM42", "BCORL1"),
                row_order = geneorder,
                heatmap_legend_param = list(title = "Mutations", at = c("stopgain", "stoploss", "splice site", "frameshift", "indel", "nonsynonymous SNV", "synonymous SNV", "Germline", "+", "-", "cnloh"), labels = c("Stop Gain", "Stop Loss", "Splice Site", "Frameshift", "InDel", "Missense", "Silent", "Germline", "Amplification", "Deletion", "Copy-Neutral LOH"))
                # annotation_legend_param = list()
                # top_annotation = HeatmapAnnotation(column_bar = anno_oncoprint_barplot(), annotation_height = unit(2, "cm"))
)
setkey(genelist, "Gene")
gl <- as.data.frame(genelist)
# setkey(gl, "Gene")
row.names(gl) <- gl$Gene
gl$Gene <- NULL
row_anno <- rowAnnotation(df = gl)
jpeg(filename="FNAHeatmapv2.jpeg", width = 2700, height = 3600, units="px", res = 300)
draw(row_anno + op, annotation_legend_side = "bottom")
dev.off()



### Comparisons
# MK247 NE vs E
# MK37 NE vs E
# MK24 NE vs E
#
# DH07 S4 vs S2
# MK282 S3 vs S2
