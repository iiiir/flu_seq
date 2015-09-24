#!/bin/env python
import dendropy as dp
from pandas import read_csv
import sys
import os
from argparse import ArgumentParser
from subprocess import check_call
import droplist
import flu_utils as flu

# Most tree handling are inplace, default of dendropy #

p =ArgumentParser()
p.add_argument('--input_tree', '-i', required=True, help='Filename of input <beast.tree>')
p.add_argument('--action', '-a', required =True, help='Action for beast tree: <subtree|partition|genotype>')
p.add_argument('--out_nexus','-b', default=None, help='Filename for output nexus tree')
p.add_argument('--out_newick', '-n', default=None, help='Filename for output newick tree, required if partitioning')
p.add_argument('--out_partition_file', '-p', default=None, help='Filename for partition result, required if performing partitioning')
p.add_argument('--out_grp', '-g', default=None, help='Filename for group output')
p.add_argument('--threshold', '-t', default=0.2, help='Threshold for partitioning the tree')
p.add_argument('--stringent_h9n2', '-s1', default=False, help='Default will filt H9N2 strains before 2014, otherwise before April 2013 ')
p.add_argument('--stringent_h7n9', '-s2', default=False, help='Default will filt H7N9 strains before April 2013, otherwise filt ALL')
p.add_argument('--keep_H7', '-k', default=None, help ='Flag indicate H7 should be keep list')
p.add_argument('--trash','-j', default=None, help='output filename for stripped taxa')
args = p.parse_args()


def add_label(tree,ann_type='posterior'):
    ''' 
    Add labels, required if performing partition for beast tree format
    Not required for newick format
    '''
    for nd in tree.nodes():
        label_value =nd.annotations.get_value(ann_type)
        nd.label =label_value #if label_value else "0.0"
    return tree

def add_partition(tree, partition_input):
    pdata =read_csv(partition_input, sep=';')
    for leafname, row in pdata.groupby('leafname'):
        if row.shape[0] != 1:
            print 'Multiple partition data for:'
            print leafname
        else:
            leafname =leafname.strip("'")
        node =tree.find_node_with_taxon_label(leafname)
        if not node:
            # one of the virus name seem to be translated from 1.2 to 1,2
            leafname =leafname.replace(',','.')
            node =tree.find_node_with_taxon_label(leafname)
            if not node:
                print 'Partition information is not present for:'
                print leafname
                assert node
        else:
            node.annotations.add_new('cluster', 
                                 row.loc[row.index[0], 'clustername'])
    return tree

def add_root_node(tree):
    '''
    Add root node to tree (mutable), change in-place
    Needed for partitioning beast tree object
    '''
    root_node =tree.mrca(taxa=list(tree.taxon_set))
    root_node.label =None
    root_node.edge.length =None
    return tree

def add_h7n9_label(tree):
    for ts in tree.taxon_set:
        if ts.label in droplist.h7n9_all():
            ts.label = ts.label + '    *H7N9*    '
    return tree


def map_color(yy):
    if yy in range(1994,2000):
        return '#000000' # black
    elif yy in range(2000,2007):
        return '#0000FF' # blue
    elif yy in range(2007,2010):
        return '#00FFFF' # aqua
    elif yy in range(2010,2012):
        return '#FFCC00' # light megenta
    elif yy == 2012:
        return '#FF66FF' # heavier megenta
    elif yy == 2013:
        return '#FF0000' # red
    else:
        return '#000000' # black

def drop_duplicates(tree):
    '''
    tree object -> tree obj

    remove duplicates in tree if exists (kept first occurence). the following will eb considered as dups
    china/beijing/1/94
    A/China/Beijing/1/1994

    update: 09/14/2015
    Now remove duplicates in such formats:
    A/Gf/HK/NT101/2003
    A/Guinea fowl/Hong Kong/NT101/2003
    A/GuineaFowl/HongKong/NT101/03

    '''
    strain_party = dict()
    dups = []
    for ln in tree.leaf_nodes():
        v =flu.Virus(ln.taxon.label)
        if not strain_party.get(v.std_name, None):
            strain_party[v.std_name]=ln.taxon.label
        else:
            dups.append(ln.taxon.label)
    tree.prune_taxa_with_labels(dups, update_splits=True)
    return tree, dups #write_nexus_tree(tree, tree_file_name.replace('.tree','_dedup.tree') )

def drop_three_underscores(tree):
    for ts in tree.taxon_set:
        if '___' in ts.label:
            ts.label =ts.label.split('___')[1]
    return tree

def drop_taxa_annotation(tree, type=None):
    for ts in tree.taxon_set:
        ts.annotations.drop()
    return tree

def filt_taxon_by_host(taxons, keep_list=None):
    if not keep_list:
        keep_list =[]
    return [lb for lb in taxons 
                if lb in keep_list or
                strain_to_host(lb) in 
                ['chicken', 'Chicken', 'ChiCken','Ck']]

def filt_taxon_by_location(taxons, keep_list=None):
    if not keep_list:
        keep_list =[]
    return [lb for lb in taxons
                if lb in keep_list or
                    strain_to_city(lb) not in 
                    ['HK', 'Hong Kong', 'Hong_Kong', 'HongKong']]

def filt_taxon_by_time(taxons, h9n2_before_april=False, h7n9_before_april=False):
    '''
    Take a tree file (dendropy format)
    return droplist

    False/False -> strip H9N2 in 2014, strip all H7N9
    True/True -> strip H9N2 and H7N9 before Aripl 2013
    '''
    lbs=[lb for lb in taxons if not lb.endswith('2014')] # remove 2014
    if h9n2_before_april: # drop taxon list
        # due to the fact that i remove duplicats in my process 
        # and changed chichen, Chicken and ChiCken to chicken.
        h9n2 =droplist.h9n2()
        h9n2.extend([l.replace('Chicken','chicken') for l in h9n2]) # one capital C
        h9n2.extend([l.replace('ChiCken','chicken') for l in h9n2]) # two capital C
        lbs =[lb for lb in lbs if not lb in h9n2]
    # filt by h7
    if h7n9_before_april: # drop post-march 2013
        lbs =[lb for lb in lbs if not lb in droplist.h7n9_part2()]
    else: # drop all
        lbs =[lb for lb in lbs if not lb in droplist.h7n9_all()]
    return lbs

def china_chicken_0313(taxons, args):
    'Find china chicken before 03/2013'
    always_in =droplist.do_not_remove()
    always_in.extend(droplist.h7n9_all())
    taxons = filt_taxon_by_time(taxons, args.stringent_h9n2, args.stringent_h7n9)
    taxons = filt_taxon_by_location(taxons, always_in)
    taxons = filt_taxon_by_host(taxons, always_in)
    return taxons

def subtree(tree, keep_list=None, junkfile=None):
    '''Default kept first 20'''
    if not keep_list:
        keep_list=[t.label for i,t in enumerate(tree.taxon_set) 
                           if i < 20] # default kept all
    ignored_list =[t.label for t in tree.taxon_set 
                           if t.label not in keep_list]
    if not junkfile:
        print >> sys.stderr, '\n'.join(ignored_list)
    else:
        fo =open(junkfile,'w')
        print >> fo, '\n'.join(ignored_list)
        fo.close()
    tree.retain_taxa_with_labels(keep_list, update_splits=True)
    return tree

def strain_to_city(s):
    '''
    str -> str

    Parse city information from strain strain names. Note when there
    are four fields then there are special cases based on the dataset
    downloaded.
    MIGHT give wrong result if data has changed.

    >>> strain_to_city('A/bird/Guangxi/82/2005')
    Guangxi
    >>> strain_to_city('A/guinea fowl/Hong Kong/NT101/2003')
    'Hong Kong'
    '''
    strain_name_as_list =s.split('/')
    if len(strain_name_as_list) == 4 and strain_name_as_list[1].lower() != "chicken":
        return strain_name_as_list[1]
    else:
        return strain_name_as_list[2]

def strain_to_host(s):
    '''
    str -> str

    Similar to strain_to_city(), and might be merged in the future

    >>> strain_to_city('A/bird/Guangxi/82/2005')
    'Guangxi'
    >>> strain_to_host('A/guinea fowl/Hong Kong/NT101/2003')
    'guinea fowl'
    '''
    strain_name_as_list =s.split('/')
    if len(strain_name_as_list) == 4 and strain_name_as_list[1].lower() != "chicken":
        return "Human"
    else:
        return strain_name_as_list[1]


def read_beast_tree(f, tree_type='beast-summary-tree'):
    '''
    Return mutable BEAST tree objects by default. 
    '''
    tree = dp.Tree()
    tree.read_from_path(f, 
                        schema=tree_type, 
                        case_sensitive_taxon_labels=True, 
                        preserve_underscores = True, 
                        extract_comment_metadata=True)
    return tree

def read_nexus_tree(f, tree_type='nexus'):
    '''
    Return mutable NEXUS tree objects by default. 
    '''
    tree = dp.Tree()
    tree.read_from_path(f, 
                        schema=tree_type, 
                        case_sensitive_taxon_labels=True,
                        as_rooted =True,
                        preserve_underscores = True, 
                        extract_comment_metadata=True)
    return tree

def read_newick_tree(f, tree_type='newick'):
    '''
    Return mutable NEWICK tree objects by default. 
    '''
    tree = dp.Tree()
    tree.read_from_path(f, 
                        schema=tree_type, 
                        case_sensitive_taxon_labels=True, 
                        preserve_underscores = True, 
                        extract_comment_metadata=True)
    return tree

def tree_labels(tree):
    return [nd.label for nd in tree.leaf_nodes()]

def partition(newick_tree, thres, fout_partition):
    '''
    A novel methodology for large-scale phylogeny partition
    '''
    ppath ='/home/swang/app/pylo_partition/ncomms1325-s2.jar'
    failed =check_call(['java','-jar',ppath, newick_tree, '%s'%thres,'-o%s'%fout_partition])
    if failed:
        print '>>> partition failed'
        assert failed
    else:
        return int(not failed)

def write_grp(tree, out_grp=None, rich_info=True):
    '''
    tree object -> txt file

    defaut print group files (.grp) to stdout
    default is rich info that will print host etc
    
    rich_info print more columns
    '''
    if not out_grp:
        fo =sys.stdout
    else:
        fo =open(out_grp, 'w')
    for ln in tree.leaf_nodes():
        d=ln.annotations.values_as_dict()
        if rich_info:
            v =flu.Virus(ln.taxon.label)
            print >> fo, "%s\t%s\t%s\t%s\t%s" %(ln.taxon.label,d['cluster'], v.year, v.province, v.host) 
        else:
            print >> fo, "%s=%s"%(ln.taxon.label, d['cluster'])
    if out_grp:    
        fo.close()

def run_genotype(args):
    tree =read_nexus_tree(args.input_tree)
    tree =drop_three_underscores(tree)
    write_grp(tree, args.out_grp)

def write_nexus_tree(tree, fout):
    if not fout:
        tree.write_to_stream( sys.stdout, 
                            schema='nexus', 
                            unquoted_underscores=True, 
                            suppress_annotations=False)
    else:
        tree.write_to_path( fout, 
                            schema='nexus', 
                            unquoted_underscores=True, 
                            suppress_annotations=False)

def write_newick_tree(tree, fout):
    if not fout:
        tree.write_to_stream( sys.stdout, 
                            schema='newick', 
                            unquoted_underscores=True, 
                            suppress_rooting=True)
    else:
        tree.write_to_path( fout, 
                            schema='newick', 
                            unquoted_underscores=True, 
                            suppress_rooting=True)

def run_partitioning(args):
    tree =read_nexus_tree(args.input_tree)
    tree =add_label(tree)
    tree =add_root_node(tree)
    write_newick_tree(tree, args.out_newick)
    success = partition(args.out_newick, args.threshold, args.out_partition_file)
    if success:
        tree = add_partition(tree, args.out_partition_file)
    write_nexus_tree(tree,args.out_nexus)


def run_subtree(args):
    tree =drop_three_underscores( read_nexus_tree(args.input_tree) )
    taxons =[nd.label for nd in tree.taxon_set]
    good_taxons =china_chicken_0313(taxons, args)
    tree =subtree(tree,keep_list=good_taxons,junkfile=args.trash)
    tree =add_h7n9_label(tree)
    write_nexus_tree(tree,args.out_nexus)
    write_newick_tree(tree, args.out_newick)

def run_dedup(args):
    tree = read_nexus_tree(args.input_tree)
    tree, dups = drop_duplicates(tree)
    print >> sys.stdout, '>>> %d duplicates in %s' % (len(dups), args.input_tree)
    print >> sys.stdout, '\n'.join(dups)
    write_nexus_tree(tree, args.out_nexus )

def main():
    if args.action == 'subtree':
        run_subtree(args)
    elif args.action == 'partition':
        run_partitioning(args)
    elif args.action == 'genotype':
        run_genotype(args)
    elif args.action == 'dedup':
        run_dedup(args)
    else:
        print 'The options you provided are:\n'
        args_dict =vars(args)
        for k in args_dict:
            print k, '----------', args_dict[k]
        print ''

if __name__ == "__main__":
    main()
