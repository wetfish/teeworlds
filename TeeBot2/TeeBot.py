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
import Events_TeeBot
from config import accesslog
from config import nick
from config import banned_nicks
from config import password
from config import port
from config import hostname

class Tee(object):
    def __init__(self, id, nick, ip, port, score, spree, largest_spree, 
                 multikill, largest_multikill, kills, lastkilltime, team, deaths, 
                 freezes, frozen, froze_by, steals, hammers, hammered, suicides):
        self.nick = nick
        self.id = int(id)
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

class TeeBot(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.passwd = password
        self.host = hostname
        self.port = port
        self.address = self.host + ":" + str(port)
        self.teelst = {}
        self.plist = {}
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
                self.plist[x] = Tee.Tee(**tt)
                print(self.plist[x].__dict__)
                x += 1
        except ValueError as e:
            print("json error {} at {:d}".format(e.msg, e.pos))
        
    @property
    def player_count(self):
        return len(self.teelst.keys())

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

    def add_tee(self, list, idnum, nick, ip, port, score, spree):
        tee = Tee(idnum, nick, ip, port, score, spree, 0, 
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        list[int(tee.id)] = tee

    def find_tee(self, list, nick):
        for tmp in list:
            if list[tmp].nick == nick:
                return list[tmp]
        return {}

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
            tee = self.teelst[int(event["player_id"])]
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
            self.add_tee(self.teelst, int(event["player_id"]), nick, ip, port, sc, 0)
            if self.find_tee(self.plist, nick) == {}:
                newid = len(self.plist) + 1
                self.add_tee(self.plist, newid, nick, ip, port, sc, 0)
        return self.teelst

    def round_end(self):
        tbuf = []
        for tmp in self.teelst:
            p = self.teelst[tmp]
            tbuf.append([p.id, p.nick, p.ip, p.port])
        self.teelst = {}
        for tb in tbuf:
            self.add_tee(self.teelst, tb[0], tb[1], tb[2], tb[3], 0, 0)
        with open('stats.json', 'w+') as outf:
            buf = []
            for tmp in self.plist:
                 dct = self.plist[tmp].__dict__
                 buf.append("{:s}".format(json.dumps(dct)))
            bufs = "[" + ",\n".join(buf) + "]"
            print(bufs)
            outf.write(bufs)

    def get_arg(self, tee, handle):
        if handle == "kd":
            return tee.kills / (tee.deaths if (tee.deaths != 0) else 1)
        elif handle in tee.__dict__:
            return tee.__dict__[handle]
#        elif handle == "largest_spree":
#            return tee.largest_spree
#        elif handle == "largest_multikill":
#            return tee.largest_multikill
#        elif handle == "steals":
#            return tee.steals
        else:
            print("invalid handle")

    def get_bests_argv(self, list, handle, max):
        best = 0
        btees = []
        for tmp in list.teelst:
            tval = self.get_arg(list.teelst[tmp], handle)
            if (tval > best) and (tval < max):
                best = tval
        for tmp in list.teelst:
            ttmp = list.teelst[tmp]
            tval = self.get_arg(ttmp, handle)
            if tval == best:
                btees.append(ttmp.nick)

        teestr = ", ".join(btees) if (best != 0) else "None"
        fmtn = "{:3.2f}".format(best) if (handle == "kd") else "{:d}".format(best)

        return best, ("{:s} ({:s})".format(fmtn, teestr))

    def get_best(self, list, handle, max):
        arr = []
        best = 999999999
        for x in range(0, max):
            bests = self.get_bests_argv(list, handle, best)
            if bests[0] >= best:
                break
            arr.append(bests[1])
            best = bests[0]
        astr = ", ".join(arr)
        return astr

    def gen_bests(self, list):
        self.say("Best k/d = {:s}".format(self.get_best(list, "kd", 3)))
        self.say("Best spree = {:s}".format(self.get_best(list, "largest_spree", 2)))
        self.say("Best multi = {:s}".format(self.get_best(list, "largest_multikill", 1)))
        self.say("Most steals = {:s}".format(self.get_best(list, "steals", 2)))

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

    def do_kill_notifs(self, ktg, vtg, spr):
        if (ktg.spree % 5) == 0 and ktg.spree != 0:
            self.bs("{} is on a killing spree with {} kills!".format(ktg.nick, ktg.spree))
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
            tt = self.teelst[vtg.froze_by]
            self.say("{} stole {}'s kill!".format(ktg.nick, tt.nick))
            ktg.steals += 1
            ktp.steals += 1
        if spr >= 5:
            t = threading.Timer(5, self.shutdown, args=[vtg, ktg, spr])
            t.start()

    def on_kill(self, event): 
        try:
            ktg = self.teelst[int(event["killer_id"])]
            vtg = self.teelst[int(event["victim_id"])]
            ktp = self.find_tee(self.plist, ktg.nick)
            vtp = self.find_tee(self.plist, vtg.nick)
            if (event["user_weapon_id"] == '-2') or (ktg.id == vtg.id):
                ktg.suicides += 1
                ktp.suicides += 1
            elif event["user_weapon_id"] == '5': #sac
                spr = self.handle_sacr(event, ktg, vtg)
                self.handle_sacr(event, ktp, vtp)
                self.do_kill_notifs(ktg, vtg, spr)
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

    def do_stats(self, tee):
        tf = tee.freezes
        tz = tee.frozen
        th = tee.hammers
        tr = tee.hammered
        tk = tee.kills
        td = tee.deaths
        tkd = ((tk / td) if (td != 0) else tk)
        tfz = ((tf / tz) if (tz != 0) else tf)
        thr = ((th / tr) if (tr != 0) else th)
        self.say("Stats for player {}:".format(tee.nick))
        self.say("Best spree: {:d}, Best multi: {:d}, Steals: {:d}, Suicides: {:d}".format(
            tee.largest_spree, tee.largest_multikill, tee.suicides, tee.steals))
        self.say("Freeze ratio = {:d}/{:d} = {:3.2f}".format(tf, tz, tfz))
        self.say("Hammer ratio = {:d}/{:d} = {:3.2f}".format(th, tr, thr))
        self.say("K/D ratio = {:d}/{:d} = {:3.2f}".format(tk, td, tkd))

    def on_chat(self, event):
        msg = event["message"]
        if "!" != msg[0]:
            return
        id = int(event["player_id"])
        ms = msg.split(' ', 1)
        tee = {}

        if "!top" == msg:
            self.gen_bests(self.teelst)
        elif "!topall" == msg:
            self.gen_bests(self.plist)
        elif "!stats" == ms[0]:
            tee = self.teelst[id] if (len(ms) == 1) else self.find_tee(self.teelst, ms[1])
        elif "!statsall" == ms[0]:
            tee = self.find_tee(self.plist, (event["player_name"] if (len(ms) == 1) else ms[1]))

        if tee == {}:
            if len(ms) > 1:
                self.say("could not find tee {}".format(ms[1]))
        else:
            self.do_stats(tee)

        

    def get_Event(self, line):
        lst = self.events.game_events(line)
        lst["line"] = line
        self.debug("We got event:\n"+dumps(lst))
        if lst is not None:
            if lst["event_type"] == "START":
                self.gen_bests(self.teelst)
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
                tee = self.teelst[int(lst["player_id"])]
                self.access_log(tee.nick, tee.ip, "left")
                del self.teelst[int(lst["player_id"])]
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

