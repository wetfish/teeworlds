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
    def get_bests_kdv(self, max):
        t = self.get_TeeLst()
        best = 0
        btees = []
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            tkdr = ttmp.get_kd()
            if (tkdr > best) and (tkdr < max):
                best = tkdr
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            tkdr = ttmp.get_kd()
            if tkdr == best:
                btees.append(ttmp.get_nick())
        teestr = ", ".join(btees)
        return best, teestr

    def get_bests_kd(self, max):
        arr = []
        best = 9999999
        x = 0
        while x < max:
           bests = self.get_bests_kdv(best)
           if bests[0] >= best:
               break
           arr.append("{:3.2f} ({:s})".format(bests[0], bests[1]))
           best = bests[0]
           x += 1
        astr = ", ".join(arr)
        return astr

    def get_bests_argv(self, handle, max):
        t = self.get_TeeLst()
        best = 0
        btees = []
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            tval = ttmp.attributes[handle]
            if (tval > best) and (tval < max):
                best = tval
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            tval = ttmp.attributes[handle]
            if tval == best:
                btees.append(ttmp.get_nick())
        teestr = ", ".join(btees)
        return best, teestr

    def get_bests_arg(self, handle, max):
        arr = []
        best = 999999999
        x = 0
        while x < max:
            bests = self.get_bests_argv(handle, best)
            if bests[0] >= best:
                break
            arr.append("{:d} ({:s})".format(bests[0], bests[1]))
            best = bests[0]
            x += 1
        astr = ", ".join(arr)
        return astr
