#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       Author: Aleksi Palomäki, a.k.a Allu2 <aleksi.ajp@gmail.com>
#        Copyright: GPL3 2011
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import json
import Tee

class Tees(object):
    def __init__(self):
        self.teelst = {}

    def add_Tee(self, idnum, nick, ip, port, score, spree):
        tee = Tee.Tee(idnum, nick, ip, port, score, spree)
        self.teelst[int(tee.attributes["id"])] = tee

    def get_Tee(self, player_id):
        return self.teelst[int(player_id)]

    def rm_Tee(self, player_id):
        del self.teelst[int(player_id)]

    def rm_Tee_all(self):
        self.teelst = {}

    def get_TeeLst(self):
        return self.teelst

    def find_tee(self, nick):
        t = self.get_TeeLst()
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            if ttmp.get_nick() == nick:
                return ttmp
        return {}

    def get_bests_argv(self, handle, max):
        t = self.get_TeeLst()
        best = 0
        btees = []
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            tval = ttmp.get_kd() if (handle == "kd") else ttmp.attributes[handle]
            if (tval > best) and (tval < max):
                best = tval
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            tval = ttmp.get_kd() if (handle == "kd") else ttmp.attributes[handle]
            if tval == best:
                btees.append(ttmp.get_nick())

        teestr = ", ".join(btees) if (best != 0) else "None"
        fmtn = "{:3.2f}".format(best) if (handle == "kd") else "{:d}".format(best)

        return best, ("{:s} ({:s})".format(fmtn, teestr))

    def get_bests_arg(self, handle, max):
        arr = []
        best = 999999999
        for x in range(0, max):
            bests = self.get_bests_argv(handle, best)
            if bests[0] >= best:
                break
            arr.append(bests[1])
            best = bests[0]
        astr = ", ".join(arr)
        return astr

    def gen_bests_line(self, line):
        if line == 1:
            return "Best k/d = {:s}".format(self.get_bests_arg("kd", 3))
        elif line == 2:
            return "Best spree = {:s}".format(self.get_bests_arg("largest_spree", 2))
        elif line == 3:
            return "Best multi = {:s}".format(self.get_bests_arg("largest_multikill", 1))
        elif line == 4:
            return "Most steals = {:s}".format(self.get_bests_arg("steals", 2))
        else:
             return "---------------------"
