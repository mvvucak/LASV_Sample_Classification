# LASV_Sample_Classification
 Collection of scripts and pipelines to process Illumina reads from LASV positive samples into taxonomically classified contigs.
 The pipeline consists of 3 separate Snakemake files, to be run sequentially:

 1. Snakereads
 	This Snakefile runs basic read processing steps on raw Illumina reads, including:
 		- Adapter trimming and quality control (trim-galore v0.4.1)
 		- Deduplication (fastuniq v1.1)
 		- rRNA filtering (riboPicker v0.4.3)
 		- Additional steps for counting reads at each stage.
 	Run with snakemake --snakefile Snakereads -j {threads}
 2. Snakeassemble
 	This Snakefile runs processed reads through de novo assembly using SPAdes v.3.13
 	Run with snakemake --snakefile Snakeassemble -j {threads}
 3. Snakediamond
 	This Snakefile classifies contigs from the de novo assembly through several steps:
 		- BLASTX using Diamond v.2.0.9 against a Diamond2 database including all RefSeq Proteins and their taxonomy information
 		- Custom Python scripts to match each contig to the Lowest Common Ancestor of all its BLASTx hits.
 		- Custom Python scripts to idnetify and extract contigs matching a target taxon (e.g. all contigs with arenavirus hits)
 	Run with snakemake --snakefile Snakediamond -j {threads}

