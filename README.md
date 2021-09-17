# LASV_Sample_Classification
 A collection of scripts and pipelines to process Illumina reads from LASV positive samples into taxonomically classified contigs.

## Dependencies

 These pipelines rely on several third-party tools, including Diamond, SPAdes and NCBI.

### Conda Environment

 lasv_sample_classification.yml contains most of the packages needed to run the pipelines. You will need to clone the environment using Conda:

 conda create --name lasv_sample_class --file lasv_sample_classification.yml

 Then activate it:

 conda ctivate lasv_sample_class

### RiboPicker

 **RiboPicker**  is a tool for filtering out rRNA reads from samples. It is not available on any Conda channel and must be installed separately from:

 https://sourceforge.net/projects/ribopicker/ 

 Ensure that ribopicker can be run with the command ribopicker.pl. Alternatively, modify the ribopicker command in the config.yml file to suit
 your installation.


### DIAMOND Database
s
 The contig classification step relies on a functional Diamond2 database constructed from all RefSeq Protein entries in NCBI. Additionally, the database must also include taxonomic information for each entry (TaxID). If you already have such a database, simply change the following pointer in the config.yml file:

 diamond_db:
  /home2/mvv1e/Databases/RefSeq_Protein.dmnd

 If not, you will have to construct the databse yourself. You can do so following these instructions.

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

