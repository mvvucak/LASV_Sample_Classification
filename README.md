# LASV_Sample_Classification
 A collection of scripts and pipelines to process Illumina reads from LASV-positive samples into taxonomically classified contigs. In this case, the pipeline was used to identify all arenavirus sequences present in samples.

## Dependencies

### Conda Environment

 lasv_sample_classification.yml contains most of the packages needed to run the pipelines. You will need to clone the environment using Conda.

 Conda can be installed from: https://docs.conda.io/en/latest/miniconda.html

 Once conda has been installed, you can create the environment with:

 conda create --name lasv_sample_class --file lasv_sample_classification.yml

 Then activate it:

 conda ctivate lasv_sample_class

### RiboPicker

 **RiboPicker**  is a tool for filtering out rRNA reads from samples. It is not available on any Conda channel and must be installed separately from:

 https://sourceforge.net/projects/ribopicker/ 

 Ensure that ribopicker can be run with the command ribopicker.pl. Alternatively, modify the following entry in config.yml with your own ribopicker command:

 `ribopicker_command:
    ribopicker.pl`

 You must also modify the names of the SILVA rRNA databses installed with ribopicker in the config.yml:

 `ribopicker_slr_db:
    slr123`
  ``ribopicker_ssr_db:
    ssr123`


### DIAMOND Database

 The contig classification step relies on a functional Diamond2 database constructed from all RefSeq Protein entries in NCBI. Additionally, the database must also include taxonomic information for each entry (TaxID). If you already have such a database, simply change the following pointer in the config.yml file:

 `diamond_db:
  /home2/mvv1e/Databases/RefSeq_Protein.dmnd`

 If not, you will have to run Snakedb to construct the databse:

 ``snakemake --snakefile Snakedb`` 

 Note that this process can take several hours and that the database will take up ~90GB of storage space when complete.

## Usage

The pipeline consists of 4 Snakemake pipelines to be run sequentially. A config.yml supplies supporting information. 
The Snakemake files should be run from the project directory using:

`snakemake --snakefile {filename} -j {allocated threads}.`

This pipeline does not include additional manual steps such as combining arenavirus contigs into complete sequences:
- Splitting erroneously joined segments (L and S segments in one contig)
- Joining contigs via read mapping extension

### Config File

config.yml stores the following:

#### Sample/Animal Information:

- Animal IDs under animal (five-digit numbers with leading 0s e.g. 00019)
- Sample IDs under all_samples, starting with animal ID followed by sample type and Illumina run identifiers:
    - 00019_BL_L1_NA_S13 denotes blood sample from animal 00019
- Sample IDs are grouped under their corresponding animal under all_samples_by_animal

#### Target taxon information:

- tax_ranks lists the taxonomic ranks to be identified for each Diamond hit. Used by the get_tax_ranks.py script
- target_taxons lists information for any taxa being searched for in the de novo output: 
    - Scientific name (e.g. mammarenavirus)
    - Taxon rank (e.g. genus)
    - TaxID (e.g. 1653394)

#### Mundane processing information:

- Expected file extensions (e.g. fastq, fq.gz)
- Database paths.

### Snakemake Pipeline

 The pipeline consists of 4 separate Snakemake files, to be run sequentially. A fifth Snakemake file can be used to construct a Diamond database.

#### Snakereads

This Snakefile runs basic read processing steps on raw Illumina reads, including:
- Adapter trimming and quality control (trim-galore v0.4.1)
- Deduplication (fastuniq v1.1)
- rRNA filtering (riboPicker v0.4.3)
- Additional steps for counting reads at each stage.
Run with `snakemake --snakefile Snakereads -j {threads}`

#### Snakeassemble

This Snakefile runs processed reads through de novo assembly using SPAdes v.3.13
Run with `snakemake --snakefile Snakeassemble -j {threads}`

#### Snakediamond

This Snakefile classifies contigs from the de novo assembly through several steps:
   - BLASTX using Diamond v.2.0.9 against a Diamond2 database including all RefSeq Proteins and their taxonomy information
   - Custom Python scripts to match each contig to the Lowest Common Ancestor of all its BLASTx hits.
   - Custom Python scripts to idnetify and extract contigs matching a target taxon (e.g. all contigs with arenavirus hits)
Run with 

`snakemake --snakefile Snakediamond -j {threads}`

Diamond hit results are stored in the Diamond directory
Classified contigs are stored in the Contigs directory
    - Each target taxon has its own subdirectory.

#### Snakemap

This Snakefile maps reads onto LASV contigs using Bowtie2 \-\-local. 
It uses samtools to output .bam alignment files for viewing in Tablet or further analysis.
- The pipeline relies on LASV sequences being stored in the "Sequences/Final" directory.
    - This includes two .fasta files per animal:
        - One for the L segment (e.g. 00019_L.fasta)
        - One for the S segment (e.g. 00019_S.fasta)
- Where each animal has more than one sample (e.g. blood, oral), each sample is mapped individually
- Additionally, an aggregate dataset of all samples (denoted "all_samples") is also mapped onto the sequences.
- .bam files are stored in the Alignments directory.

#### Snakedb

This Snakefile builds a Diamond database using NCBI RefSeq Protein nonredundant entries.
- First, all RefSeq nonredundant protein entries are downloaded from https://ftp.ncbi.nlm.nih.gov/refseq/
    - These are stored in a Databases/Fastas directory
- Next, NCBI taxonomy files are downloaded from https://ftp.ncbi.nih.gov/pub/taxonomy/:
    - taxdmp.zip which contains nodes.dmp and names.dmp (taxonomy data)
    - prot.accession2taxid.gz which matches RefSeq accessions with taxonomy IDs
- Finally, a Diamond RefSeq Protein database incorporating taxonomy data is constructed
Does not need to be run if you already have a Diamond database incorporating taxonomy data.


