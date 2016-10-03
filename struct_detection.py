#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
Copyright © 2016 Juan Francisco Martínez <juan.martinez[AT]bsc[dot]es>

*****************************************************************************
*                        ANALYSIS PERFORMANCE TOOLS                         *
*                              [tool name]                                  *
*                         [description of the tool]                         *
*****************************************************************************
*     ___     This library is free software; you can redistribute it and/or *
*    /  __         modify it under the terms of the GNU LGPL as published   *
*   /  /  _____    by the Free Software Foundation; either version 2.1      *
*  /  /  /     \   of the License, or (at your option) any later version.   *
* (  (  ( B S C )                                                           *
*  \  \  \_____/   This library is distributed in hope that it will be      *
*   \  \__         useful but WITHOUT ANY WARRANTY; without even the        *
*    \___          implied warranty of MERCHANTABILITY or FITNESS FOR A     *
*                  PARTICULAR PURPOSE. See the GNU LGPL for more details.   *
*                                                                           *
* You should have received a copy of the GNU Lesser General Public License  *
* along with this library; if not, write to the Free Software Foundation,   *
* Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA          *
* The GNU LEsser General Public License is contained in the file COPYING.   *
*                                 ---------                                 *
*   Barcelona Supercomputing Center - Centro Nacional de Supercomputacion   *
*****************************************************************************
'''

import sys, os
import numpy

from traceParsing import *
from callstackDistribution import *
from calculateDelta import *
from clustering import *

import constants


# At this point a and b are sorted
def get_b_to_a_pos(a, b):
    result=[]

    ib=0
    for i in range(len(a)):
        if ib >= len(b):
            break

        if a[i] <= b[ib]: 
            continue
        else: 
            ind=i
            while a[ind-1]==None:
                ind-=1
            result.append(ind)
            ib+=1

            while a[i] > b[ib]:
                while a[ind-1]==None:
                    ind-=1
                result.append(ind)

                ib+=1

    result.extend([len(a)]*(len(b)-ib))

    # Make positions relative
    for i in range(1,len(result)):
        result[i]=result[i]-sum(result[0:i])

    # Substract one position
    for i in range(len(result)):
        if result[i]>0: result[i]=result[i]-1

    return result

def invert_holes(holes):
    new_holes=[]

    for i in range(1, len(holes)):
        new_holes.append(holes[i]*-1)

    new_holes.append(holes[0]*-1)
    return new_holes

def add_holes(holes, row):
    # Translate holes into indexes

    hindex=[]
    hi=0
    for h in holes:
        while hi < len(row) and row[hi]==None: hi+=1
        cnt=h
            
        if cnt > 0:
            while cnt > 0:
                hindex.append(hi+len(hindex)) # to left
                cnt-=1
        elif cnt < 0:
            hi+=1
            while cnt<0:
                hindex.append(hi+len(hindex)) # to right
                cnt+=1
        hi+=1

    # Add holes
    for hind in hindex:
        if hind < len(row) and row[hind] == None:
            continue
        row.insert(hind, None)

    return row



# This function performs all the matrix transformation (gaps add) needed
# in order to guarantee the constraint of iterations non-overlaping.
# i.e. the last element of col n must be less or equal that the first
# element of n+1 col
def boundaries_sort(tmat):
    matrix=tmat.tolist()
    ncols=len(matrix[0])
    nrows=len(matrix)

    #newmat=[[]]*nrows

    for row in range(nrows-1):
        holes=get_b_to_a_pos(matrix[row], matrix[row+1])

        add_holes(holes, matrix[row+1])

        iholes=invert_holes(holes)
        for rrow in range(row, -1, -1):
            add_holes(iholes, matrix[rrow])

    return numpy.matrix(matrix)

def align_cluster(rank, cluster):
    keys_cs=[]
    index=0
    max_size=0

    tomat=[]

    for cs in cluster:
        k=cs.keys()[0]
        
        if cs[k]["rank"] != "0": continue

        if len(cs[k]["when"]) > max_size:
            max_size=len(cs[k]["when"]) 
            for i in range(index-1, -1, -1):
                holes=max_size-len(tomat[i])
                tomat[i].extend([-1]*holes)
        elif len(cs[k]["when"]) < max_size:
            holes=max_size-len(cs[k]["when"])
            cs[k]["when"].extend([-1]*holes)

        tomat.append(cs[k]["when"])
        keys_cs.append(k)
        index+=1

    return numpy.matrix(tomat),max_size

def calculate_it_boundaries(cluster):
    tmat,max_size=align_cluster(0, cluster)

    # For the moment w/o references to the callstacks
    
    '''
    ki=0
    for row in tomat:
        row.append(ki)
        ki+=1
    '''

    # Sorting by the first column
    tmat=tmat.view("i8,"*(max_size-1)+"i8")
    tmat.sort(order=["f0"], axis=0)
    tmat=tmat.view(np.int)

    keys_ordered=[]
    '''
    ordered_calls=tmat[:,max_size].transpose()

    # Get the calls ordered by times
    for row in range(len(keys_cs)):
        ki=tmat.item((row,-1))
        keys_ordered.append(keys_cs[ki])
    '''

    # Adding holes if needed
    tmat=boundaries_sort(tmat)
    tmat=align_cluster(0,tmat)

    # TODO: New way to get iterations
    # Get the iterations times
    iterations=[]
    for it in range(max_size+1):
        ite=tmat[:,it].transpose().tolist()[0]
        
        index_from=0
        from_time=ite[index_from]

        while from_time == -1:
            index_from+=1
            from_time=ite[index_from]

        index_to=-1
        to_time=ite[index_to]

        while to_time == -1:
            index_to-=1
            to_time=ite[index_to]

        iterations.append((from_time,to_time))

    return iterations, keys_ordered
    #return tmat.tolist()[0][:-1], keys_ordered 

def main(argc, argv):
    if argc < 2:
        print("Usage(): {0} [-l call_level] [-f img1[,img2,...]] <trace>\n"
                .format(argv[0]))
        return -1

    level="0"; trace = argv[-1]; image_filter=["ALL"]
    for i in range(1, len(argv)-1):
        if argv[i] == "-f": image_filter=argv[i+1].split(",")
        elif argv[i] == "-l": level=argv[i+1]

    clevels = "All"
    if level != "0":
        clevels=str(level)

    if constants._verbose:
        print("{0} : Calls level={1}; Image filter={2}; Trace={3}\n\n"
                .format(argv[0], clevels, str(image_filter), trace.split("/")[-1]))

    cs_files,app_time=get_callstacks(trace, level, image_filter)

    if constants._verbose: print("[Merging data]")

    mean_delta=0; filtered_data=[]; nonfiltered_data=[]
    for csf in cs_files:
        cdist=getCsDistributions(csf)
        new_delta, new_fdata=getDelta(cdist,app_time)
        mean_delta+=new_delta
        filtered_data.append(new_fdata)
        nonfiltered_data.append(cdist)

        '''
        print("callstack\ttimes\ttime_mean\ttime_std\tdist_mean\tdist_std")
        for c,d in cdist.items():
            print("{0}\t{1}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}"
                .format(c,d["times"], d["time_mean"], d["time_std"], d["dist_mean"], d["dist_std"], d["when"]))
        '''

    mean_delta/=len(cs_files)
    nclusters, clustered_data=clustering(filtered_data, False)

    # Printing results
    ordered_cluster={}
    for cluster in clustered_data.keys():
        it_cluster,cs_ordered=calculate_it_boundaries(clustered_data[cluster])
        
        print("[\033[1mCluster {0}\033[0m have been found {1} iterations]".format(cluster, len(it_cluster)))
        cnt=1
        for i in range(len(it_cluster)-1):
            print("-  Iteration_{0} found @ [ {1} , {2} )".format(cnt,it_cluster[i][0],it_cluster[i][1]))
            cnt+=1

        #print("-  Iteration_TOT found @ [ {0} , {1} ]".format(it_cluster[0][0], it_cluster[0][0]+app_time*mean_delta))
        print("[Every iteration has this calls]")
        for cs in cs_ordered:
            print("-  {0}".format(cs))
        
    print("[Results]")
    print("  -> {0} clusters detected".format(nclusters))
    print("  -> Really useful time (in loops): {0:.2f} %".format(mean_delta*100))
    print("[Done]")

    # Remove all temporal files
    for csf in cs_files: os.remove(csf)

    return 0

if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))