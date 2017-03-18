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
from json import dumps
import Tees
import plugin_loader
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
        self.plugin_loader = plugin_loader.Plugin_loader(self)
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
        self.info("Saying: {}".format(message))
        self.writeLine('say "'+self.name+': ' + message.replace('"', "'") + "\"'")

    def brd(self, message):
        self.info("Broadcating: {}".format(message))
        self.writeLine('broadcast "' + message.replace('"', "'") + "\"'")

    def killSpree(self, id):
        tee = self.get_Teelista().get(id)
        spree = tee.get_spree()
        if (spree % 5) == 0 and spree != 0:
            msg = "{} is on a killing spree with {} kills!".format(tee.get_nick(), tee.get_spree())
            self.brd(msg)
            self.say(msg)
            pass
    def Multikill(self, id):
        tee = self.get_Teelista().get(id)
        multikill = tee.get_multikill()
        if multikill == 2:
            msg = "{} DOUBLEKILL!".format(tee.get_nick())
        elif multikill == 3:
            msg = "{} TRIPLEKILL!".format(tee.get_nick())
        elif multikill == 4:
            msg = "{} QUODRAKILL!!".format(tee.get_nick())
        elif multikill == 5:
            msg = "{} PENTAKILL!".format(tee.get_nick())
        elif multikill >= 6:
            msg = "{} IS A BADASS!".format(tee.get_nick())
        else:
            return
        self.brd(msg)
        self.say(msg)

    def shutdown(self, victim_tee, killer_tee, spree):
        msg = "{0}'s {2} kill spree was shutdown by {1}!".format(victim_tee.get_nick(), killer_tee.get_nick(), str(spree))
        self.brd(msg)
        self.say(msg)

    def get_Teelista(self):
        return self.teelst.get_TeeLst()
    def get_Teelistp(self):
        return self.plist.get_TeeLst()
    def get_Tee(self, id):
        return self.teelst.get_Tee(int(id))
    def get_Tee_persistent(self, id):
        return self.plist.get_Tee(int(id))

    def find_tee(self, nick):
        t = self.get_Teelista()
        for tmp in t:
            ttmp = self.get_Tee(tmp)
            if ttmp.get_nick() == nick:
                return ttmp
        return {}

    def find_ptee(self, nick):
        t = self.get_Teelistp()
        for tmp in t:
            ttmp = self.get_Tee_persistent(tmp)
            if ttmp.get_nick() == nick:
                return ttmp
        return {}

    def updTeeList(self, event):

        # try:
        # self.debug(result.groups(), "DEBUG")
        # if result.groups()[3] in banned_nicks:
        #         self.writeLine("kick {0}".format(result.groups()[0]))
        #
        # except AttributeError as e:
        #     self.debug("Error: {0}".format(e), "CRITICAL")
        try:
            tee = self.teelst.get_Tee(event["player_id"])
            if tee.get_nick() != event["player_name"]:
                old_ip = tee.get_ip()
                tee.set_nick(event["player_name"])
                tee.set_score(event["score"])
                tee.set_ip(event["ip"])
                tee.set_port(event["port"])
                if old_ip != tee.get_ip():
                    with open(accesslog, "a", encoding="utf-8") as accesslogi:
                        time1 = time.strftime("%c", time.localtime())
                        accesslogi.write("[{}] ".format(time1) + "{} joined the server ({})".format(tee.get_nick(),
                                                                                                    tee.get_ip()) + "\n")
                else:
                    pass
        except AttributeError as e:
            self.exception(e)
        except KeyError as e:
            #self.exception(e)
            self.debug("Didn't find Tee: {} in player lists, adding it now:".format(event["player_name"]))
            with open(accesslog, "a", encoding="utf-8") as accesslogi:
                nick = event["player_name"]
                ip = event["ip"]
                time1 = time.strftime("%c", time.localtime())
                accesslogi.write(
                    "[{}] ".format(time1) + "{} joined the server ({})".format(nick, ip) + "\n")
            self.teelst.add_Tee(event["player_id"], event["player_name"], event["ip"], event["port"],
                                event["score"], 0)  # id, name, ip, port, score
            self.plist.add_Tee(event["player_id"], event["player_name"], event["ip"], event["port"], event["score"], 0)
        return self.teelst.get_TeeLst()

    def get_Leaves(self, ide):
        nick = self.teelst.get_Tee(ide).get_nick()
        self.teelst.rm_Tee(ide)
        return nick

    def get_Chat(self, line):
        return self.events.conversation(line)

    def print_bests(self):
        self.say("Best k/d = {:s}".format(self.teelst.get_bests_kd(3)))
        self.say("Best spree = {:s}".format(self.teelst.get_bests_arg("largest_spree")))
        self.say("Best multi = {:s}".format(self.teelst.get_bests_arg("largest_multikill")))
        self.say("Most steals = {:s}".format(self.teelst.get_bests_arg("steals")))

    def print_bests_all(self):
        self.say("Best k/d = {:s}".format(self.plist.get_bests_kd(3)))
        self.say("Best spree = {:s}".format(self.plist.get_bests_arg("largest_spree")))
        self.say("Best multi = {:s}".format(self.plist.get_bests_arg("largest_multikill")))
        self.say("Most steals = {:s}".format(self.plist.get_bests_arg("steals")))


    def round_end(self):
        t = self.teelst.get_TeeLst()
        for tmp in t:
            ttmp = self.teelst.get_Tee(tmp)
            nick = ttmp.get_nick()
            ptmp = self.find_ptee(nick)
            if ptmp == {}:
                self.plist.add_Tee(ttmp.get_idnum(), nick, ttmp.get_ip(), ttmp.get_port(), ttmp.get_score(), ttmp.get_spree())
            ptmp = self.find_ptee(nick)
            if ptmp.get_largest_spree() < ttmp.get_largest_spree():
                ptmp.set_largest_spree(ttmp.get_largest_spree())
            if ptmp.get_largest_multikill() < ttmp.get_largest_multikill():
                ptmp.set_largest_multikill(ttmp.get_largest_multikill())
            ptmp.killed(ttmp.get_deaths())
            ptmp.hammer(ttmp.get_hammers())
            ptmp.hammered(ttmp.get_hammered())
            ptmp.suicide(ttmp.get_suicides())
            ptmp.freeze(ttmp.get_freezes())
            ptmp.froze(0, ttmp.get_frozen())
            ptmp.steal(ttmp.get_steals())
            ptmp.sac(ttmp.get_kills())
        for tmp in t:
            ttmp = self.teelst.get_Tee(tmp)
            idn = ttmp.get_idnum()
            nick = ttmp.get_nick()
            ip = ttmp.get_ip()
            port = ttmp.get_port()
            self.teelst.rm_Tee(tmp)
            self.teelst.add_Tee(idn, nick, ip, port, 0, 0)

    def get_Event(self, line):

        lst = self.events.game_events(line)
        lst["line"] = line
        self.debug("We got event:\n"+dumps(lst))
        if lst is not None:
            if lst["event_type"] == "START":
                self.print_bests()
                self.round_end()
            if lst["event_type"] == "RELOAD ORDER":
                self.info("Reloaded plugins")
                importlib.reload(plugin_loader)
            if lst["event_type"] == "NICK CHANGE":
                self.writeLine("status")
            if lst["event_type"] == "MAP_CHANGE":
                self.game["map"] = lst["map_name"]

            if lst["event_type"] == "STATUS_MESSAGE":
                nick = lst["player_name"]
                ide = lst["player_id"]
                if nick in banned_nicks:
                    self.writeLine("kick {0}".format(ide))
                lista = self.updTeeList(lst)
            if lst["event_type"] == "LEAVE":
                with open(accesslog, "a", encoding="utf-8") as accesslogi:
                    tee = self.get_Tee(lst["player_id"])
                    nick = tee.get_nick()
                    ip = tee.get_ip()
                    time1 = time.strftime("%c", time.localtime())
                    accesslogi.write(
                        "[{}] ".format(time1) + "{} left the server ({})".format(nick, ip) + "\n")
                self.debug("{} has left the game.".format(self.get_Leaves(lst[0])))
                self.writeLine("status")
                tees = self.player_count
                if tees == 0:
                    self.writeLine("restart")

            else:
                pass
            self.plugin_loader.event_handler(lst)

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



