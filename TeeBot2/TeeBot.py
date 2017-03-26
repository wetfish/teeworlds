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

import telnetlib
from threading import Thread
import time, logging, importlib
import threading, time
import json
from json import dumps
import Tees
#import plugin_loader
import Events_TeeBot
from config import accesslog
from config import nick
from config import banned_nicks
from config import password
from config import port
from config import hostname

class TeeBot(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.passwd = password
        self.host = hostname
        self.port = port
        self.address = self.host + ":" + str(port)
        self.teelst = Tees.Tees()
        self.plist = Tees.Tees()
        self.events = Events_TeeBot.Events()
        self.name = nick
        logging.basicConfig()
        self.logger = logging.getLogger("Bot")
        self.logger.setLevel(logging.DEBUG)
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.exception = self.logger.exception
#        self.plugin_loader = plugin_loader.Plugin_loader(self)
        teebuf = []
        try:
            with open('stats.json') as jdata:
                teebuf = json.load(jdata)
            x = 0
            for tt in teebuf:
                self.plist.add_Tee(x, " ", " ", 0, 0, 0)
                self.plist.get_Tee(x).attributes = tt
                print(self.plist.get_Tee(x).attributes)
                x += 1
        except ValueError as e:
            print("json error {} at {:d}".format(e.msg, e.pos))
        self.game = {
            "type": "",
            "start_time": 0,
            "map": "",
            "red":{
                "score": 0,
                "players": 0,
            },
            "blue": {
                "score": 0,
                "players": 0,
            },
            "purple": {
                "score": 0,
                "players": 0,
            },
        }
    @property
    def player_count(self):
        return len(self.teelst.get_TeeLst().keys())

    @property
    def connect(self):
        self.debug("Connecting to server..")
        self.tn = telnetlib.Telnet(self.host, self.port)
        self.debug("Telnet Object created.")
        lines = self.tn.read_until(b"Enter password:")
        self.tn.write(str(self.passwd).encode('utf-8') + b'\n')
        return self.tn

    def talk(self, msg, method):
        #self.logger.debug(msg)
        if method == "game_chat":
            self.say(msg)
        elif method == "terminal":
            pass
        else:
            pass

    def readLine(self):
        return self.tn.read_until(b"\n")

    def team_solver(self, team_id):
        team_id = int(team_id)
        teams = {
            0: "red",
            1: "blue",
            -1: "purple"
        }
        return teams[team_id]

    def writeLine(self, line):
        self.tn.write(str(line).encode('utf-8') + b"\n")

    def readLines(self, until):
        return self.tn.read_until(str(until).encode('utf-8'), 0.6)

    def echo(self, message):
        self.debug("Echoing: {}".format(message))
        self.writeLine('echo "'+self.name+': ' + message.replace('"', "'") + "\"'")

    def say(self, message):
        message = message[:255]
        self.info("Saying: {}".format(message))
        self.writeLine('say "'+self.name+': ' + message.replace('"', "'") + "\"'")

    def brd(self, message):
        message = message[:255]
        self.info("Broadcasting: {}".format(message))
        self.writeLine('broadcast "' + message.replace('"', "'") + "\"'")

    def bs(self, message):
        self.say(message)
        self.brd(message)

    def killSpree(self, id):
        tee = self.teelst.get_TeeLst().get(id)
        spree = tee.attributes["spree"]
        if (spree % 5) == 0 and spree != 0:
            self.bs("{} is on a killing spree with {} kills!".format(tee.get_nick(), spree))

    def Multikill(self, id):
        tee = self.teelst.get_TeeLst().get(id)
        multikill = tee.attributes["multikill"]
        if multikill == 2:
            self.bs("{} DOUBLEKILL!".format(tee.get_nick()))
        elif multikill == 3:
            self.bs("{} TRIPLEKILL!".format(tee.get_nick()))
        elif multikill == 4:
            self.bs("{} QUODRAKILL!!".format(tee.get_nick()))
        elif multikill == 5:
            self.bs("{} PENTAKILL!".format(tee.get_nick()))
        elif multikill >= 6:
            self.bs("{} IS A BADASS!".format(tee.get_nick()))

    def shutdown(self, victim_tee, killer_tee, spree):
        self.bs("{}'s {} kill spree was shutdown by {}!".format(victim_tee.get_nick(), spree, killer_tee.get_nick()))

    def access_log(self, nick, ip, action):
        with open(accesslog, "a", encoding="utf-8") as accesslogi:
            time1 = time.strftime("%c", time.localtime())
            msg = "[{}] {} {} the server ({})\n".format(time1, nick, action, ip)
            accesslogi.write(msg)
            self.debug(msg)

    def updTeeList(self, event):
        nick = event["player_name"]
        ip = event["ip"]
        try:
            tee = self.teelst.get_Tee(event["player_id"])
            if tee.get_nick() != nick:
                old_ip = tee.attributes["ip"]
                tee.attributes["nick"] = nick
                tee.attributes["score"] = event["score"]
                tee.attributes["ip"] = ip
                tee.attributes["port"] = event["port"]
                if old_ip != ip:
                    self.access_log(nick, ip, "joined")
        except AttributeError as e:
            self.exception(e)
        except KeyError as e:
            self.debug("Didn't find Tee: {} in player lists, adding it now:".format(nick))
            self.access_log(nick, ip, "joined")
            self.teelst.add_Tee(event["player_id"], nick, ip, event["port"], event["score"], 0)
            if self.plist.find_tee(nick) == {}:
                newid = len(self.plist.get_TeeLst()) + 1
                self.plist.add_Tee(newid, nick, ip, event["port"], event["score"], 0)
        return self.teelst.get_TeeLst()

    def round_end(self):
        t = self.teelst.get_TeeLst()
        tbuf = []
        for tmp in t:
            p = self.teelst.get_Tee(tmp).attributes
            tbuf.append([p["id"], p["nick"], p["ip"], p["port"]])
        self.teelst.rm_Tee_all()
        for tb in tbuf:
            self.teelst.add_Tee(tb[0], tb[1], tb[2], tb[3], 0, 0)
        with open('stats.json', 'w+') as outf:
            p = self.plist.get_TeeLst()
            buf = []
            for tmp in p:
                 buf.append("{:s}".format(json.dumps(self.plist.get_Tee(tmp).attributes)))
            bufs = "[" + ",\n".join(buf) + "]"
            print(bufs)
            outf.write(bufs)
    def on_kill(self, event): 
        if event["event_type"] == "KILL":
            try:
                ktg = self.teelst.get_Tee(event["killer_id"])
                ktga = ktg.attributes
                vtg = self.teelst.get_Tee(event["victim_id"])
                vtga = vtg.attributes
                ktpa = self.plist.find_tee(ktga["nick"]).attributes
                vtpa = self.plist.find_tee(vtga["nick"]).attributes
                kid = ktga["id"]
                vid = vtga["id"]
                if (event["user_weapon_id"] == '-2') or (kid == vid):
                    ktga["suicides"] += 1
                    ktpa["suicides"] += 1
                elif event["user_weapon_id"] == '5': #sac
                    ksp = ktga["spree"] + 1
                    spr = vtga["spree"]
                    
                    now = time.time()
                    if ksp > ktga["largest_spree"]:
                        ktga["largest_spree"] = ksp
                    if ksp > ktpa["largest_spree"]:
                        ktpa["largest_spree"] = ksp

                    if now - ktga["lastkilltime"] <= 5:
                        ktga["multikill"] += 1
                    if now - ktga["lastkilltime"] > 5:
                        ktga["multikill"] = 1

                    if ktga["multikill"] > ktga["largest_multikill"]:
                        ktga["largest_multikill"] = ktga["multikill"]
                    if ktga["multikill"] > ktpa["largest_multikill"]:
                        ktpa["largest_multikill"] = ktga["multikill"]

                    ktga["lastkilltime"] = now
                    ktga["kills"] += 1
                    ktga["spree"] = ksp
                    ktpa["kills"] += 1
                    if spr >= 5:
                        t = threading.Timer(5, self.shutdown, args=[vtg, ktg, spr])
                        t.start()
                    vtga["deaths"] += 1
                    vtga["spree"] = 0
                    vtpa["deaths"] += 1
                    vtpa["spree"] = 0
                    self.killSpree(kid)
                    id = vtga["froze_by"]
                    if kid == id:
                        self.Multikill(kid)
                    else:
                        tt = self.teelst.get_Tee(id)
                        self.say("{} stole {}'s kill!".format(ktga["nick"], tt.get_nick()))
                        ktga["steals"] += 1
                        ktpa["steals"] += 1
                elif event["user_weapon_id"] == '4': #freeze
                    ktga["freezes"] += 1
                    ktpa["freezes"] += 1
                    vtga["frozen"] += 1
                    vtpa["frozen"] += 1
                    vtga["froze_by"] = kid
                    vtpa["froze_by"] = kid
                elif event["user_weapon_id"] == '0': #hammer
                    ktga["hammers"] += 1
                    ktpa["hammers"] += 1
                    vtga["hammered"] += 1
                    vtpa["hammered"] += 1
            except (KeyError, NameError) as e:
                self.exception(e)
                self.debug("Guessing Tee didn't exist! Updating player list!")
                self.writeLine("status")
    def on_chat(self, event):
        msg = event["message"]
        if "!" != msg[0]:
            return
        id = event["player_id"]
        ms = msg.split(' ', 1)
        tee = {}

        if "!top" == msg:
            for x in range(1, 5):
                self.say(self.teelst.gen_bests_line(x))
        elif "!topall" == msg:
            for x in range(1, 5):
                self.say(self.plist.gen_bests_line(x))
        elif "!stats" == ms[0]:
            tee = self.teelst.get_Tee(id) if (len(ms) == 1) else self.teelst.find_tee(ms[1])
        elif "!statsall" == ms[0]:
            tee = self.plist.find_tee(event["player_name"]) if (len(ms) == 1) else self.plist.find_tee(ms[1])

        if tee == {}:
            if len(ms) > 1:
                self.say("could not find tee {}".format(ms[1]))
            return

        self.say("Stats for player {}:".format(tee.attributes["nick"]))

        ts = tee.attributes["largest_spree"]
        tm = tee.attributes["largest_multikill"]
        tx = tee.attributes["suicides"]
        ty = tee.attributes["steals"]
        self.say("Best spree = {:d}, Best multi = {:d} | {:d} steals, {:d} suicides".format(ts, tm, ty, tx))

        tf = tee.attributes["freezes"]
        tz = tee.attributes["frozen"]
        th = tee.attributes["hammers"]
        tr = tee.attributes["hammered"]
        tfz = ((tf / tz) if (tz != 0) else tf)
        thr = ((th / tr) if (tr != 0) else th)
        self.say("Freeze ratio = {:d}/{:d} = {:3.2f} | Hammer ratio = {:d}/{:d} = {:3.2f}".format(tf,tz,tfz,th,tr,thr))

        tk = tee.attributes["kills"]
        td = tee.attributes["deaths"]
        tkd = ((tk / td) if (td != 0) else tk)
        self.say("K/D ratio = {:d}/{:d} = {:3.2f}".format(tk, td, tkd))


    def get_Event(self, line):
        lst = self.events.game_events(line)
        lst["line"] = line
        self.debug("We got event:\n"+dumps(lst))
        if lst is not None:
            if lst["event_type"] == "START":
                for x in range(1, 5):
                    self.say(self.teelst.gen_bests_line(x))
                self.round_end()
#            if lst["event_type"] == "RELOAD ORDER":
#                self.info("Reloaded plugins")
#                importlib.reload(plugin_loader)
            if lst["event_type"] == "NICK CHANGE":
                self.writeLine("status")
            elif lst["event_type"] == "MAP_CHANGE":
                self.game["map"] = lst["map_name"]
            elif lst["event_type"] == "STATUS_MESSAGE":
                nick = lst["player_name"]
                ide = lst["player_id"]
                if nick in banned_nicks:
                    self.writeLine("kick {0}".format(ide))
                lista = self.updTeeList(lst)
            elif lst["event_type"] == "LEAVE":
                tee = self.teelst.get_Tee(lst["player_id"]).attributes
                self.access_log(tee["nick"], tee["ip"], "left")
                self.teelst.rm_Tee(lst["player_id"])
                self.writeLine("status")
                if self.player_count == 0:
                    self.writeLine("restart")
            elif lst["event_type"] == "KILL":
                on_kill(event)
            elif lst["event_type"] == "CHAT":
                on_chat(event)
#            else:
#                pass
#            self.plugin_loader.event_handler(lst)

        return lst

    def run(self):
        self.tn  = self.connect
        self.say("Connected.")
        self.writeLine("status")
        ticks = 0.1
        while True:
            time.sleep(ticks)
            try:
                try:
                    line = self.readLine().decode()
                    if line != "\n":
                        self.debug("We got line: {}".format(line))
                except Exception as e:
                    self.exception(e)
                    exit()
                if line == "\n":
                    pass
                elif "[server]:" in line.split(" ")[0] and ("player" in line.split(" ")[1] and "has" in line.split(" ")[2]):
                    self.writeLine("status")
                else:
                    event = self.get_Event(line)
            except (KeyError, TypeError, AttributeError, NameError, UnicodeDecodeError) as e:
                self.exception(e)
                self.writeLine("status")



