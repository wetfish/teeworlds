#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       Author: Aleksi Palomäki, a.k.a Allu2 <aleksi.ajp@gmail.com>
#        Copyright: GPL3 2011
#
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

import time, json


class Tee(object):
    def __init__(self, idnum, nick, ip, port, score, spree):

        self.attributes = {"nick": nick,
                           "id": int(idnum),
                           "ip": ip,
                           "port": port,
                           "score": score,
                           "spree": spree,
                           "largest_spree": 0,
                           "multikill": 1,
                           "largest_multikill": 0,
                           "kills": 0,
                           "lastkilltime": 0,
                           "team": None,
                           "deaths": 0,
                           "freezes": 0,
                           "frozen": 0,
                           "froze_by": 0,
                           "steals": 0,
                           "hammers": 0,
                           "hammered": 0,
                           "suicides": 0}

    def json_encode(self):
        return

    def get_hammers(self):
        return self.attributes["hammers"]
    def get_hammered(self):   #lol
        return self.attributes["hammered"]
    def get_suicides(self):
        return self.attributes["suicides"]
    def get_spree(self):
        return self.attributes["spree"]
    def get_deaths(self):
        return self.attributes["deaths"]
    def get_freezes(self):
        return self.attributes["freezes"]
    def get_frozen(self):
        return self.attributes["frozen"]
    def get_froze_by(self):
        return self.attributes["froze_by"]
    def get_steals(self):
        return self.attributes["steals"]
    def get_kills(self):
        return self.attributes["kills"]
    def killed(self, num):
        self.attributes["deaths"] += num
    def hammer(self, num):
        self.attributes["hammers"] += num
    def hammered(self, num):
        self.attributes["hammered"] += num
    def suicide(self, num):
        self.attributes["suicides"] += num
    def freeze(self, num):
        self.attributes["freezes"] += num
    def froze(self, id, num):
        self.attributes["frozen"] += num
        self.attributes["froze_by"] = id
    def steal(self, num):
        self.attributes["steals"] += num
    def sac(self, num):
        self.attributes["kills"] += num
    def set_spree(self, spree):
        now = time.time()
        if spree > 0:
            if spree > self.attributes["largest_spree"]:
                self.attributes["largest_spree"] = spree

            if now - self.attributes["lastkilltime"] <= 5:
                self.attributes["multikill"] += 1

            if now - self.attributes["lastkilltime"] > 5:
                self.attributes["multikill"] = 1

            if self.attributes["multikill"] > self.attributes["largest_multikill"]:
                self.set_largest_multikill(self.attributes["multikill"])

            self.attributes["lastkilltime"] = now
        self.attributes["spree"] = spree
#        self.attributes["kills"] += 1
    def get_idnum(self):
        return self.attributes["id"]

    def set_idnum(self, idnum):
        self.attributes["id"] = int(idnum)

    def get_nick(self):
        return self.attributes["nick"]

    def set_nick(self, nick):
        self.attributes["nick"] = nick

    def get_ip(self):
        return self.attributes["ip"]

    def set_ip(self, ip):
        self.attributes["ip"] = ip

    def get_port(self):
        return self.attributes["port"]

    def set_port(self, port):
        self.attributes["port"] = port

    def get_score(self):
        return self.attributes["score"]

    def set_score(self, score):
        self.attributes["score"] = score

    def set_multikill(self, multikill):
        self.attributes["multikill"] = multikill

    def get_multikill(self):
        return self.attributes["multikill"]

    def set_largest_spree(self, spree):
        self.attributes["largest_spree"] = spree

    def get_largest_spree(self):
        return self.attributes["largest_spree"]

    def get_largest_multikill(self):
        return self.attributes["largest_multikill"]

    def set_largest_multikill(self, largest_multikill):
        self.attributes["largest_multikill"] = largest_multikill

    def get_kd(self):
        tk = self.get_kills()
        td = self.get_deaths() if (self.get_deaths() != 0) else 1
        return tk / td

    def get_frz_ratio(self):
        tf = self.get_freezes()
        tz = self.get_frozen() if (self.get_frozen() != 0) else 1
        return tf / tz

    def get_hmr_ratio(self):
        th = self.get_hammers()
        tr = self.get_hammered() if (self.get_hammered() != 0) else 1
        return th / tr

    def gen_stats_line(self, line):
        if line == 1:
            return "Stats for player {}:".format(self.get_nick())
        elif line == 2:
            ts = self.get_largest_spree()
            tm = self.get_largest_multikill()
            tx = self.get_suicides()
            ty = self.get_steals()
            return "Best spree = {:d}, Best multi = {:d} | {:d} steals, {:d} suicides".format(ts, tm, ty, tx)
        elif line == 3:
            tf = self.get_freezes()
            tz = self.get_frozen()
            th = self.get_hammers()
            tr = self.get_hammered()
            tfz = self.get_frz_ratio()
            thr = self.get_hmr_ratio()
            return "Freeze ratio = {:d}/{:d} = {:3.2f} | Hammer ratio = {:d}/{:d} = {:3.2f}".format(tf,tz,tfz,th,tr,thr)
        elif line == 4:
            tk = self.get_kills()
            td = self.get_deaths()
            tkd = self.get_kd()
            return "K/D ratio = {:d}/{:d} = {:3.2f}".format(tk, td, tkd)
        else:
            return "---------------------"

    @property
    def tojson(self):
        return json.dumps(self.attributes, indent=3)

    def __str__(self):
        return ( str(self.attributes["nick"]) + ' comes from IP adress: ' + str(self.attributes["ip"]) + ':' + str(self.attributes["port"]) + ' and has player ID: ' + str(
            self.attributes["id"]) + ' and has ' + str(self.attributes["score"]) + ' points.')
