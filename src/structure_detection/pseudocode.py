#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from loop import loop, conditional_rank_block
from callstack import callstack
from utilities import pretty_print
from gui import *

class pseudo_line(object):
    def __init__(self, deph):
        self.deph = deph
        self.first_col = "--"
        self.second_col = "--"
        self.third_col = "--"
        self.metric = "metric..."
        self.metric_2 = ""

    def get_tabs(self):
        return ": "*self.deph

    def __str__(self):
        res = "{0:10.10} {1:>5.5} {2:40.40} {3:15.15}".format(
                self.first_col,
                self.second_col, 
                (self.get_tabs() + self.third_col), 
                self.metric_2)
        return res

class pseudo_for(pseudo_line):
    def __init__(self, iterations, misc, deph):
        pseudo_line.__init__(self, deph)
        self.iterations = iterations
        self.first_col = ""
        self.second_col = " "
        self.third_col = "FOR 1 TO {0} [[{1}]]".format(
                self.iterations,
                str(misc))
        self.metric = ""

class pseudo_for_end(pseudo_line):
    def __init__(self, iterations, deph):
        pseudo_line.__init__(self, deph)
        self.iterations = iterations
        self.first_col = ""
        self.second_col = " "
        self.third_col = "END LOOP"
        self.metric = ""

class pseudo_call(pseudo_line):
    def __init__(self, call, deph):
        pseudo_line.__init__(self, deph)
        self.call = call
        self.first_col = self.call.call_file
        if self.call.mpi_call:
            metric = self.call.my_callstack\
                    .metrics["global_mpi_duration_merged_percent"]
            self.second_col = "*"
            self.metric_2 = str(round(metric,2)) + "%"
#           self.metric_2 = str(self.call.my_callstack.repetitions)

        else:
            self.second_col = str(self.call.line)
            self.metric = ""
        self.third_col = "{0}()".format(self.call.call)

class pseudo_condition(pseudo_line):
    def __init__(self, ranks, el, eli, deph):
        pseudo_line.__init__(self, deph)
        self.ranks = ranks
        self.el = el
        self.eli = eli

        self.first_col = ""
        self.second_col = " "
        if self.el:
            self.third_col = "else"
        elif self.eli:
            self.third_col = "elif Rank is {0}".format(self.ranks)
        else:
            self.third_col = "if Rank is {0}".format(self.ranks)
        self.metric = ""


class condition(object):
    def __init__(self, set1, set2):
        set1 = set(set1)
        set2 = set(set2)

        self.is_equal = set1 == set2
        self.is_subset = set1.issubset(set2) and not self.is_equal
        self.is_superset = set1.issuperset(set2) and not self.is_equal
        self.is_complement = len(set1.intersection(set2)) == 0

class pseudocode(object):
    def __init__(self, clusters_set, nranks, only_mpi):
        self.lines = []
        self.all_ranks = range(nranks)
        self.only_mpi = only_mpi
        self.last_callstack = []

        # Sort the clusters by program order
        #
        clusters_set.sort(key=lambda x: x.get_first_line(), reverse=False)
        #clusters_set.reverse()

        for cluster in clusters_set:
            for loop_obj in cluster.loops:
                self.parse_loop(loop_obj, 0)

    def parse_loop(self, loop_obj, tabs):
        # Callstack to loop
        #
        if not self.only_mpi:
            if not loop_obj.common_with_prev is None:
                tabs += len(loop_obj.common_with_prev)

            tabs += self.parse_callstack(loop_obj.common_callstack, tabs)

        # Loop description
        #
        loop_id = str(loop_obj.cluster_id) + ":" + str(loop_obj._id)
        self.lines.append(pseudo_for(loop_obj.iterations, loop_id, tabs))
        self.parse_conditional_rank_block(
                loop_obj.conditional_rank_block,
                loop_obj.get_all_ranks(), 
                tabs+1)
        self.lines.append(pseudo_for_end(loop_obj.iterations, tabs))

    def parse_callstack(self, callstack_obj, tabs):
        if callstack_obj is None:
            return 0

        calls=callstack_obj.calls
        my_tabs=0

        if not self.only_mpi:
            for call in calls:
#               if not call in self.last_callstack:
                self.lines.append(pseudo_call(call, tabs+my_tabs))
                my_tabs += 1
        else:
            if len(calls) > 0:
                self.lines.append(pseudo_call(calls[-1],tabs))

#        self.last_callstack = callstack_obj.calls
        return my_tabs

    def parse_conditional_rank_block(self, 
            conditional_rank_block_obj, 
            prev_ranks,
            tabs):

        item = conditional_rank_block_obj

        # Print the common callstack
        if not self.only_mpi:
            if conditional_rank_block_obj.common_with_prev != None:
                tabs += len(conditional_rank_block_obj.common_with_prev)

            tabs += self.parse_callstack(
                        conditional_rank_block_obj.common_callstack, 
                        tabs)

        # Print the conditional
        condition_tabs=0

        if item.ranks != self.all_ranks:
            self.lines.append(pseudo_condition(
                item.ranks, False, False, tabs+condition_tabs))
            condition_tabs += 1

#        my_ranks = set(conditional_rank_block_obj.ranks)
#        condition_obj = condition(my_ranks, prev_ranks)
#        if condition_obj.is_equal:
#            pass
#        elif condition_obj.is_subset:
#            #condition_tabs += 1
#            self.lines.append(pseudo_condition(
#                item.ranks, False, False, tabs+condition_tabs))
#            condition_tabs += 1
#        elif condition_obj.is_complement:
#            if set(prev_ranks).union(set(item.ranks)) == set(self.all_ranks):
#                el = False; eli = True
#            else:
#                el = False; eli = True
#
#            #condition_tabs += 1
#            self.lines.append(pseudo_condition(item.ranks, 
#                el, eli,tabs+condition_tabs))
#            condition_tabs += 1
#        elif condition_obj.is_superset:
#            assert False # ????
#            self.lines.append(pseudo_condition(item.ranks, False, False,
#                tabs+condition_tabs))
#            condition_tabs += 1
    

        # Print whatever we have under the conditional
        #
        for item in conditional_rank_block_obj.callstacks:
            if isinstance(item, loop):
                self.parse_loop(item, tabs+condition_tabs)
                prev_ranks = item.get_all_ranks()
            elif isinstance(item, conditional_rank_block):
                self.parse_conditional_rank_block(
                        item, 
                        prev_ranks, 
                        tabs+condition_tabs)
                prev_ranks = item.ranks
            else:
                tabs_c = 0
                if item.common_with_prev != None:
                    tabs_c = len(item.common_with_prev)
                self.parse_callstack(item, tabs+tabs_c+condition_tabs)
                prev_ranks = item.get_all_ranks()

    def show_console(self):
        self.gui = console_gui(self.lines)
        self.gui.show()

    def show_html(self):
        pass

