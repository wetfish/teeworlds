__author__ = 'Aleksi'
from subprocess import check_output
class Stats:
    def __init__(self):
        self.handle_events = ["NOTHING"]
        pass
    def handle(self, event, bot, plugins):
        bot.debug("Statistics is handling this.")
        msg = event[1]
        nick = event[0]
        id = event[2]
        if "!stats" == msg:
            tee = bot.get_Tee(id)
            tk = tee.get_kills()
            td = tee.get_deaths()
            tf = tee.get_freezes()
            tz = tee.get_frozen()
            th = tee.get_hammers()
            tr = tee.get_hammered()  #lol
            tx = tee.get_suicides()
            ty = tee.get_steals()
            ts = tee.get_largest_spree()
            tm = tee.get_largest_multikill()
            tkd = tk / td
            tfz = tf / tz
            thr = th / tr
            bot.say("Player: {}".format(tee.get_nick()))
            bot.say("Best spree: {:3d} | Best multi: {:3d}".format(ts, tm))
            bot.say("Kills:      {:3d} | Deaths:     {:3d} | Ratio: {:3.2f}".format(tk, td, tkd))
            bot.say("Freezes:    {:3d} | Frozen:     {:3d} | Ratio: {:3.2f}".format(tf, tz, tfz))
            bot.say("Hammers:    {:3d} | Hammered:   {:3d} | Ratio: {:3.2f}".format(th, tr, thr))
            bot.say("Steals:     {:3d} | Suicides:   {:3d}".format(ty, tx))
        if "/pause" == msg or "/stop" == msg:
            bot.say("One does not simply pause an online game!")
        if "!lag" == msg:
            lag = str(check_output(["ifstat", "1", "1"])).split()
            down = lag[-2]
            up = lag[-1].replace("\\", "").replace("n", "").replace("\n","").replace("'", "")
            bot.say("In: {}kb/s  Out: {}kb/s.".format(down, up))
