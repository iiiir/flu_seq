#!/bin/python
import re

def date_to_mmddyy(yymmdd):
    '''
    str -> str

    Translate 'mm/dd/yy' or 'yy-mm-dd' date format to standard mm/dd/yy
    Needs to provide the date as string

    >>> date_to_mmddyy('//2013', -1, '/')
    //2013
    >>> date_to_mmddyy('2013-1-1', 0, '-')
    1/1/2013
    '''
    if '-' in yymmdd:
        delim ="-"
    elif '/' in yymmdd:
        delim ="/"
    else:
        yy=re.search(r'\d{4}', yymmdd ).group(0)
        return '00/00/%s'%yy
    lis =yymmdd.split(delim)
    if len(lis) == 3:
        mm = lis[0] if delim =="/" else lis[1]
        dd = lis[1] if delim =="/" else lis[2]
        yy = lis[2] if delim =="/" else lis[0]
    elif len(lis) == 2:
        mm = lis[0] if delim =="/" else lis[1]
        dd = ''
        yy = lis[1] if delim =="/" else lis[0]
    else:
        print('ill formated dates %s'%yymmdd)
    return '%s/%s/%s'%(mm, dd, yy)

def h7n9_part1():
    return [l.split("|")[0].strip() for l in h7n9_strains()
            if date_to_mmddyy(l.rsplit("|")[1]).split("/")[0]
                in ['1','2','3','01', '02', '03']]

def h7n9_part2():
    return [l.split("|")[0].strip() for l in h7n9_strains()
            if date_to_mmddyy(l.rsplit("|")[1]).split("/")[0] 
                not in ['1','2','3','01', '02', '03']]

def h7n9_all():
    return [l.split("|")[0].strip() for l in h7n9_strains()]

def h7n9_strains(fin='/home/swang/src/python/h7n9_month.txt'):
    return [l.strip(">").strip() for l in open(fin) if not l.startswith('#')]

def main():
    print(h7n9_all())

if __name__=="__main__":
    main()
