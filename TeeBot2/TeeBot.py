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
import Tee
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

        teebuf = []
        try:
            with open('stats.json') as jdata:
                teebuf = json.load(jdata)
            x = 0
            for tt in teebuf:
                self.plist.teelst[x] = Tee.Tee(**tt)
                print(self.plist.teelst[x])
                x += 1
        except ValueError as e:
            print("json error {} at {:d}".format(e.msg, e.pos))
        
    @property
    def player_count(self):
        return len(self.teelst.teelst.keys())

    @property
    def connect(self):
        self.debug("Connecting to server..")
        self.tn = telnetlib.Telnet(self.host, self.port)
        self.debug("Telnet Object created.")
        lines = self.tn.read_until(b"Enter password:")
        self.tn.write(str(self.passwd).encode('utf-8') + b'\n')
        return self.tn

    def readLine(self):
        return self.tn.read_until(b"\n")

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

    def shutdown(self, vt, kt, spree):
        self.bs("{}'s {} kill spree was shutdown by {}!".format(vt.nick, spree, kt.nick))

    def access_log(self, nick, ip, action):
        with open(accesslog, "a", encoding="utf-8") as accesslogi:
            time1 = time.strftime("%c", time.localtime())
            msg = "[{}] {} {} the server ({})\n".format(time1, nick, action, ip)
            accesslogi.write(msg)
            self.debug(msg)

    def updTeeList(self, event):
        nick = event["player_name"]
        ip = event["ip"]
        sc = event["score"]
        port = event["port"]
        try:
            tee = self.teelst.teelst[event["player_id"]]
            if tee.nick != nick:
                old_ip = tee.ip
                tee.nick = nick
                tee.score = sc
                tee.ip = ip
                tee.port = port
                if old_ip != ip:
                    self.access_log(nick, ip, "joined")
        except AttributeError as e:
            self.exception(e)
        except KeyError as e:
            self.access_log(nick, ip, "joined")
            self.teelst.add_Tee(event["player_id"], nick, ip, port, sc, 0)
            if self.plist.find_tee(nick) == {}:
                newid = len(self.plist.teelst) + 1
                self.plist.add_Tee(newid, nick, ip, port, sc, 0)
        return self.teelst.teelst

    def round_end(self):
        tbuf = []
        for tmp in self.teelst.teelst:
            p = self.teelst.teelst[tmp]
            tbuf.append([p.id, p.nick, p.ip, p.port])
        self.teelst.teelst = {}
        for tb in tbuf:
            self.teelst.add_Tee(tb[0], tb[1], tb[2], tb[3], 0, 0)
        with open('stats.json', 'w+') as outf:
            buf = []
            for tmp in self.plist.teelst:
                 dct = self.plist.teelst[tmp].__dict__
                 buf.append("{:s}".format(json.dumps(dct)))
            bufs = "[" + ",\n".join(buf) + "]"
            print(bufs)
            outf.write(bufs)

    def handle_sacr(self, event, ktg, vtg):
        spr = vtg.spree
        now = time.time()

        ktg.spree += 1
        if ktg.spree > ktg.largest_spree:
            ktg.largest_spree = ktg.spree

        if now - ktg.lastkilltime <= 5:
            ktg.multikill += 1
        if now - ktg.lastkilltime > 5:
            ktg.multikill = 1

        if ktg.multikill > ktg.largest_multikill:
            ktg.largest_multikill = ktg.multikill

        ktg.lastkilltime = now
        ktg.kills += 1
        vtg.deaths += 1
        vtg.spree = 0
        return spr

    def on_kill(self, event): 
        try:
            ktg = self.teelst.teelst[event["killer_id"]]
            vtg = self.teelst.teelst[event["victim_id"]]
            ktp = self.plist.find_tee(ktg.nick)
            vtp = self.plist.find_tee(vtg.nick)
            if (event["user_weapon_id"] == '-2') or (ktg.id == vtg.id):
                ktg.suicides += 1
                ktp.suicides += 1
            elif event["user_weapon_id"] == '5': #sac
                spr = self.handle_sacr(event, ktg, vtg)
                self.handle_sacr(event, ktp, vtp)
                if spr >= 5:
                    t = threading.Timer(5, self.shutdown, args=[vtg, ktg, spr])
                    t.start()

                if (ktg.spree % 5) == 0 and ktg.spree != 0:
                    self.bs("{} is on a killing spree with {} kills!".format(
                        ktg.nick, ktg.spree))

                if ktg.multikill == 2:
                    self.bs("{} DOUBLEKILL!".format(ktg.nick))
                elif ktg.multikill == 3:
                    self.bs("{} TRIPLEKILL!".format(ktg.nick))
                elif ktg.multikill == 4:
                    self.bs("{} QUODRAKILL!!".format(ktg.nick))
                elif ktg.multikill == 5:
                    self.bs("{} PENTAKILL!".format(ktg.nick))
                elif ktg.multikill >= 6:
                    self.bs("{} IS A BADASS!".format(ktg.nick))

                if ktg.id != vtg.froze_by:
                    tt = self.teelst.teelst[vtg.froze_by]
                    self.say("{} stole {}'s kill!".format(ktg.nick, tt.nick))
                    ktg.steals += 1
                    ktp.steals += 1
            elif event["user_weapon_id"] == '4': #freeze
                ktg.freezes += 1
                ktp.freezes += 1
                vtg.frozen += 1
                vtp.frozen += 1
                vtg.froze_by = ktg.id
                vtp.froze_by = ktg.id
            elif event["user_weapon_id"] == '0': #hammer
                ktg.hammers += 1
                ktp.hammers += 1
                vtg.hammered += 1
                vtp.hammered += 1
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
            tee = self.teelst.teelst[id] if (len(ms) == 1) else self.teelst.find_tee(ms[1])
        elif "!statsall" == ms[0]:
            tee = self.plist.find_tee(event["player_name"]) if (len(ms) == 1) else self.plist.find_tee(ms[1])

        if tee == {}:
            if len(ms) > 1:
                self.say("could not find tee {}".format(ms[1]))
            return

        self.say("Stats for player {}:".format(tee.nick))
        self.say("Best spree: {:d} | Best multi: {:d} | {:d} steals | {:d} suicides".format(
            tee.largest_spree, tee.largest_multikill, tee.suicides, tee.steals))

        tf = tee.freezes
        tz = tee.frozen
        th = tee.hammers
        tr = tee.hammered
        tfz = ((tf / tz) if (tz != 0) else tf)
        thr = ((th / tr) if (tr != 0) else th)
        self.say("Freeze ratio = {:d}/{:d} = {:3.2f} | Hammer ratio = {:d}/{:d} = {:3.2f}".format(tf,tz,tfz,th,tr,thr))

        tk = tee.kills
        td = tee.deaths
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
            elif lst["event_type"] == "NICK CHANGE":
                self.writeLine("status")
            elif lst["event_type"] == "STATUS_MESSAGE":
                nick = lst["player_name"]
                ide = lst["player_id"]
                if nick in banned_nicks:
                    self.writeLine("kick {0}".format(ide))
                lista = self.updTeeList(lst)
            elif lst["event_type"] == "LEAVE":
                tee = self.teelst.teelst[lst["player_id"]]
                self.access_log(tee.nick, tee.ip, "left")
                self.teelst.rm_Tee(lst["player_id"])
                self.writeLine("status")
                if self.player_count == 0:
                    self.writeLine("restart")
            elif lst["event_type"] == "KILL":
                self.on_kill(lst)
            elif lst["event_type"] == "CHAT":
                self.on_chat(lst)
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



