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
        tee = Tee.Tee(idnum, nick, ip, port, score, spree, 0, 
                 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.teelst[int(tee.id)] = tee

    def rm_Tee(self, player_id):
        del self.teelst[int(player_id)]

    def find_tee(self, nick):
        for tmp in self.teelst:
            if self.teelst[tmp].nick == nick:
                return self.teelst[tmp]
        return {}

    def get_arg(self, tee, handle):
        if handle == "kd":
            return tee.get_kd()
        elif handle == "largest_spree":
            return tee.largest_spree
        elif handle == "largest_multikill":
            return tee.largest_multikill
        elif handle == "steals":
            return tee.steals
        else:
            print("invalid handle")

    def get_bests_argv(self, handle, max):
        best = 0
        btees = []
        for tmp in self.teelst:
            tval = self.get_arg(self.teelst[tmp], handle)
            if (tval > best) and (tval < max):
                best = tval
        for tmp in self.teelst:
            ttmp = self.teelst[tmp]
            tval = self.get_arg(ttmp, handle)
            if tval == best:
                btees.append(ttmp.nick)

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
