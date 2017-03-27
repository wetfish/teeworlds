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
    def __init__(self, idnum, nick, ip, port, score, spree, largest_spree, 
                 multikill, largest_multikill, kills, lastkilltime, team, deaths, 
                 freezes, frozen, froze_by, steals, hammers, hammered, suicides):
        self.nick = nick
        self.id = int(idnum)
        self.ip = ip
        self.port = port
        self.score = score
        self.spree = spree
        self.largest_spree = largest_spree
        self.multikill = 1
        self.largest_multikill = largest_multikill
        self.kills = kills
        self.lastkilltime = 0
        self.team = None
        self.deaths = deaths
        self.freezes = freezes
        self.frozen = frozen
        self.froze_by = 0
        self.steals = steals
        self.hammers = hammers
        self.hammered = hammered
        self.suicides = suicides

    def get_kd(self):
        tk = self.kills
        td = self.deaths
        return (tk / td) if (td != 0) else tk

#    @property
#    def tojson(self):
#        return json.dumps(self.attributes, indent=3)

#    def __str__(self):
#        return ( str(self.attributes["nick"]) + ' comes from IP adress: ' + str(self.attributes["ip"]) + ':' + str(self.attributes["port"]) + ' and has player ID: ' + str(
#            self.attributes["id"]) + ' and has ' + str(self.attributes["score"]) + ' points.')
