#!/bin/bash

fasta=$1
if [[ $fasta != *.fasta ]]; then
    echo ">>> \"$fasta\" does not ends with \".fasta\""
    exit 1
fi

# 1. sequence alignment
fasta_out=`basename ${fasta/.fasta/_mu.fasta}`
echo ">>> Your alignment fasta file is:"
echo "$fasta_out"
echo ""
muscle -quiet -in $fasta -out $fasta_out

# 2. input updated fasta, and original meta file
#    output motif, and print csv
python fasta_to_csv.py $fasta_out ${fasta/.fasta/.xls}
# 3. summary/plot

