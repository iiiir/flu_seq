#!/bin/bash -e

if [ $# -lt 1 ]; then
	echo ""
	echo "Error: please provide trees file"
	EXE_file=`basename $0`
	echo "run as: $EXE_file <thousand trees>"
	echo ""
	exit 0
fi

ddup=~/app/workspace/compbio/flu_analysis/trunk/resources/dups
thousand_tree=$1
fname=`basename $thousand_tree`
seg=`basename $thousand_tree | awk -F"_" '{print $1}'`

if [[ ! "$fname" =~ ^HA_*|^NA_*|^PB2_*|^PB1_*|^PA_*|^NP_*|^MP_*|^M_*|^NS_* ]]; then
	echo -e "\nFile name mal-formatted: $1"
	echo -e "Needs to start with the segment names\n"
	exit 0
fi

echo "*** Starts pipeline ***"
cmd="sumtrees.py --rooted $thousand_tree \
	-f 0.01 \
	--collapse-negative-edges \
	-o ${fname/.trees/_consensus.tree}"
echo $cmd

# target is the topology to comput branch length etc.
cmd="treeannotator -target ${fname/.trees/_consensus.tree} \
	-burnin 0 \
	-heights median \
	$thousand_tree \
	$seg.tree"
echo $cmd
#mv ${fname/.trees/_consensus.tree} $seg.consensus.tree

cmd="python ~/src/python/tree_handler.py \
	-a partition \
	-i $seg.tree \
	-n $seg.newick \
	-t 0.2 \
	-p ${seg}.clade \
	-b ${seg}_clade.tree"
echo $cmd
#rm $seg.newick ${seg}.clade

cmd="python ~/src/python/aln_and_tree_renamer.py \
	${seg}_clade.tree \
	${seg}_clade_named.tree \
	phylogeny \
	nexus \
	/nfs_exports/genomes/1/projects/Flu/JuanPu/merged_data_06182014/seqs_metadata.tsv \
	VID \
	Virus.name_with_subtype_marker"
echo $cmd
#rm ${seg}_clade.tree

cmd="python ~/src/python/add_dup.py ${seg}_clade_named.tree $ddup/big2_${seg}.txt ${seg}_clade_named_dup.tree"
echo $cmd
#rm ${seg}_clade_named.tree

#cmd="python ~/src/python/prune_HK.py ${seg}_clade_named_dup.tree ${seg}_clade_named_dup.tree"
#echo $cmd
#rm ${seg}_clade_named_dup.tree

cmd="python3 ~/src/python/add_tip_color.py ${seg}_clade_named_dup.tree > ${seg}_clade_named_dup_col.tree"
echo $cmd
#rm ${seg}_clade_named_dup.tree

cmd="python ~/src/python/add_annotations.py ${seg}_clade_named_dup_col.tree ${seg}_clade_named_dup_col_ann.tree"
echo $cmd
#rm ${seg}_clade_named_dup_col.tree

