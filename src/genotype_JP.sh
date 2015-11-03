#!/bin/bash

f=`cd \`dirname $1\`; pwd`/`basename $1`
fb=`basename ${f%.tree}`
seg=`echo $fb | awk -F"_" '{print $1}'`

cmd="python ~/src/python/prune_tree.py $f ${fb}_sub.tree"
echo $cmd

cmd="python3 ~/src/python/add_tip_color.py ${fb}_sub.tree > ${fb}_sub_col.tree"
echo $cmd

cmd="python ~/src/python/add_annotations.py ${fb}_sub_col.tree ${fb}_sub_col_ann.tree"
echo $cmd

cmd="python ~/src/python/tree_handler.py -i ${fb}_sub_col_ann.tree -a genotype -g ${seg}.grp"
echo $cmd

# HA is longer
awk 'BEGIN{FS="\t"} $2=substr($2, 0, 1) {print $1"="$2}' ${seg}.grp > ${seg}.txt

## update 100820215
python ~/app/flu_seq/src/adhoc/geno.py -f *.grp > cx_trees.tsv
loadR
Rscript /home/swang/app/flu_seq/src/adhoc/geno_plot.R cx_trees.tsv

