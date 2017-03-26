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

    def get_nick(self):
        return self.attributes["nick"]

    def get_kd(self):
        tk = self.attributes["kills"]
        td = self.attributes["deaths"]
        return (tk / td) if (td != 0) else tk

    @property
    def tojson(self):
        return json.dumps(self.attributes, indent=3)

    def __str__(self):
        return ( str(self.attributes["nick"]) + ' comes from IP adress: ' + str(self.attributes["ip"]) + ':' + str(self.attributes["port"]) + ' and has player ID: ' + str(
            self.attributes["id"]) + ' and has ' + str(self.attributes["score"]) + ' points.')
