from ete3 import NCBITaxa
import pandas as pd 
from argparse import ArgumentParser


def get_args():
	parser = ArgumentParser()

	parser.add_argument("-i", "--input_file", required = True, 
		help = "Input .tsv with taxID data for contigs.")
	parser.add_argument("-r", "--ranks", nargs = '*', type = str, default = ["superkingdom"], 
		help = "Space-separated list of taxonomic ranks to identify for contigs. e.g. 'family genus'")
	parser.add_argument("-o", "--output_file", required = True, 
		help = "Output .tsv file to write contig data updated with taxonomic rank.")

	args = vars(parser.parse_args())
	return args


def read_in_taxonomy_db():
	ncbi = NCBITaxa()
	return ncbi 


def read_lca_tsv(input_file):
	lca_df = pd.read_csv(input_file, sep = '\t', index_col = 0, dtype = {"Diamond Hit TaxID": str})
	return lca_df

# Given a TaxID, returns its taxonomic rank
def get_rank(taxid):
	return ncbi.get_rank([taxid])	


def get_specified_parent_ranks(row, ranks):
	"""Update contig data with TaxIDs for taxon ranks of interest

	Parameters
	----------
	row: pandas.Series
		Row from a pandas DataFrame containing data for a contig,
		including the TaxID of the lowest common ancestor (LCA).
	ranks: list of str
		Taxonomic ranks of interest to be noted for the contig.
		e.g. superkingdom, family, genus.

	Returns
	-------
	row: pandas.Series
		Row containing data for a contig, updated with the names of
		taxonomic ranks of interest.
	"""

	# Return a list of parental TaxIDs for a contig's lowest common ancestor 
	lineage = ncbi.get_lineage(row["LCA"])

	# Convert parental TaxIDs into a dictionary of taxonomic ranks
	# Where Key:Value is TaxID:Rank
	lineage_ranks = ncbi.get_rank(lineage)

	# Get TaxID for each rank of interest and add it to the row.
	# If the rank is hierarchically beneath the LCA, add N/A instead.
	for rank in ranks:
		if rank in lineage_ranks.values():
			for lineage_taxid in lineage_ranks:
				if lineage_ranks.get(lineage_taxid) == rank:
					row[rank] = str(lineage_taxid)
		else:
			row[rank] = "N/A"

	return row



def get_lca(taxids):
	"""Given a list of TaxIDs, returns the TaxID of their lowest common ancestor

	Parameters
	----------
	taxids: list of str
		List of valid TaxIDs present in the NCBI Taxonomy Database.

	Returns
	-------
	lca: str
		TaxID of the lowest common ancestor of input TaxIDs.
		This is 1 (Root) if no LCA is found.
	"""

	# Residual text processing to remove non-TaxID characters.
	# TODO: Needs to be done further upstream in the pipeline.
	taxids = taxids.strip("[,]").split(' ')
	taxids = [taxid.rstrip(',') for taxid in taxids]
	taxids = [taxid.strip('\'') for taxid in taxids]

	# Remove duplicate TaxIDs
	taxids = list(set(taxids))

	def get_lineage(taxid):
		try:
			return ncbi.get_lineage(taxid)
		except ValueError:
			return None

	# Get hierarchical list of lineages for each query TaxID
	# Root is at index 0, query TaxID itself is at the end of list.
	lineages = [get_lineage(taxid) for taxid in taxids]

	# Remove any cases with no lineage.
	if None in lineages:
		lineages = [lineage for lineage in lineages if lineage is not None]
	# If no lineages are found for any TaxID, return LCA of of 1 (Root)
	if len(lineages) == 0:
		return "1"


	# Get length of shortest lineage (== max. iterations for loop)
	min_lineage_length = min([len(lineage) for lineage in lineages])

	lca = None

	# Find the LCA by iterating through all queries' lineages,
	# starting from root.
	for i in range(min_lineage_length):
		# Create set from all TaxIDs at this index in the lineages.
		# e.g. [1,2,2] becomes {1,2}, [1,1,1] becomes {1}
		taxids_at_index = set([lineage[i] for lineage in lineages])

		# A set length of 1 indicates all lineages have the same TaxID
		# at this index (i.e. common ancestor). Update the LCA.
		if len(taxids_at_index) == 1:
			lca = taxids_at_index.pop()

		# Otherwise, at least one lineage has deviated and the queries
		# no longer share a common ancestor past this indes.
		# Ancestor from the previous iteration is the LCA.
		else:
			return lca

	# If every index in the shortest lineage has been traversed with no
	# deviations in TaxID between lineages, the LCA is the last index 
	# of the shortest lineage.
	return lca

ncbi = None

def main():
	# Get input parameters.
	args = get_args()
	
	# Read NCBI Taxonomy database into memory
	global ncbi
	ncbi = read_in_taxonomy_db()
	
	# Read TaxID data for contigs in as dataframe
	lca_df = read_lca_tsv(args.get("input_file"))
	
	# Determine LCA for each contig.
	lca_df["LCA"] = lca_df["Diamond Hit TaxID"].apply(get_lca)
	
	# Identify taxonomic units for each contig based on LCA.
	lca_df = lca_df.apply(get_specified_parent_ranks, axis = 1, args = (args.get("ranks"),))
	
	# Write updated contig dataframe to file.
	lca_df.to_csv(args.get("output_file"), sep = '\t')


if __name__ == "__main__":
	main()







