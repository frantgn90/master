#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os

if "PARAVER_ON" in os.environ:
    _verbose=False
else:
    _verbose=True


TOTAL_TIME = 1
TRACE = ""
TRACE_NAME = ""
CALLSTACK_SIZE=15

_intra_field_separator="|"
_inter_field_separator="#"

###############
### PARAVER ###
###############

PARAVER_MPI_CFG = "/home/jmartinez/BSC/software/paraver/cfgs/mpi/views/MPI_call.cfg"

CALLER_EVENT_BASE ="300000"
CALLIN_EVENT_BASE ="300001"
MPICAL_EVENT_BASE ="700000"
MPILIN_EVENT_BASE ="800000"
MPI_EVENT_BASE    ="500000"
OMPCAL_EVENT_BASE =""
OMPLIN_EVENT_BASE =""

PARAVER_EVENT     ="2"
PARAVER_COMM      ="3"

FUNC_MAP_FILE     ="functions.map"
MPI_LIB_FILE      ="*"

_empty_cell=0

####################
#### CLUSTERING ####
####################

_x_axis_label     ="Number of occurrences"
_y_axis_label     ="Mean period bw occurrences"
_z_axis_label     ="delta"

_x_axis           ="times"
_y_axis           ="time_mean"
_z_axis           ="delta"

_eps =0.1
_min_samples = 1

#_eps              =0.2
#_min_samples      =1


###############
#### LOOPS ####
###############

PURELOOP          =0
MULTILOOP         =1

#####################
#### PSEUDO-CODE ####
#####################

FORLOOP           ="for loop 1 to {0}:\n"
IF_RANK           ="if RANK in {0}:\n"
IF_DATA           ="if CHANCE is ({0:.3f}):\n"
ELSE_RANK         ="elif RANK in {0}:\n"
TAB               =":  "

##############
### RANDOM ###
##############

RANDOM_SEED       =5748473

#############
### CPLEX ###
#############

OPL_PROJECT = "/home/jmartinez/BSC/master/master-thesis/git/"\
        "src/structure_detection/opl/deltas_fitting"
OPL_RUN_SCRIPT    ="/home/jmartinez/BSC/master/master-thesis/git/"\
        "src/structure_detection/opl/run.sh"
OPL_PROBLEM_IN    ="/home/jmartinez/BSC/master/master-thesis/git/"\
        "src/structure_detection/opl/deltas_fitting/input_problem.dat"
OPL_PROBLEM_OUT   ="cplex.out"
OPL_PROBLEM_ERR   ="cplex.err"

OPL_ARG_BIGM    = "bigM"
OPL_ARG_NDELTAS = "nDeltas"
OPL_ARG_NPOINTS = "nPoints"
OPL_ARG_DELTAS  = "Deltas"
OPL_ARG_POINTS  = "Points"
OPL_ARG_DISTDP  = "Distance_dp"

OPL_DELTA_DIST    ="maxDeltaDistance"
OPL_USED_DELTA    ="UsedDelta"
OPL_POINT_DELTA   ="Cover_dp"

MAX_ITERATIONS = 1

#######
# LOG #
#######

log_level = 0
