__author__ = 'Aleksi'
class Chat:
    def __init__(self):
        self.handle_events = ["CHAT"]
        pass
    def handle(self, event, bot, plugins):
        msg = event["message"]
        if "!" != msg[0]:
            return
        id = event["player_id"]
        ms = msg.split(' ', 1)
        tee = {}

        if "!top" == msg:
            for x in range(1, 5):
                bot.say(bot.teelst.gen_bests_line(x))
        elif "!topall" == msg:
            for x in range(1, 5):
                bot.say(bot.plist.gen_bests_line(x))
        elif "!stats" == ms[0]:
            tee = bot.teelst.get_Tee(id) if (len(ms) == 1) else bot.teelst.find_tee(ms[1])
        elif "!statsall" == ms[0]:
            tee = bot.plist.find_tee(event["player_name"]) if (len(ms) == 1) else bot.plist.find_tee(ms[1])

        if tee == {}:
            if len(ms) > 1:
                bot.say("could not find tee {}".format(ms[1]))
            return

        bot.say("Stats for player {}:".format(tee.attributes["nick"]))

        ts = tee.attributes["largest_spree"]
        tm = tee.attributes["largest_multikill"]
        tx = tee.attributes["suicides"]
        ty = tee.attributes["steals"]
        bot.say("Best spree = {:d}, Best multi = {:d} | {:d} steals, {:d} suicides".format(ts, tm, ty, tx))

        tf = tee.attributes["freezes"]
        tz = tee.attributes["frozen"]
        th = tee.attributes["hammers"]
        tr = tee.attributes["hammered"]
        tfz = ((tf / tz) if (tz != 0) else tf)
        thr = ((th / tr) if (tr != 0) else th)
        bot.say("Freeze ratio = {:d}/{:d} = {:3.2f} | Hammer ratio = {:d}/{:d} = {:3.2f}".format(tf,tz,tfz,th,tr,thr))

        tk = tee.attributes["kills"]
        td = tee.attributes["deaths"]
        tkd = ((tk / td) if (td != 0) else tk)
        bot.say("K/D ratio = {:d}/{:d} = {:3.2f}".format(tk, td, tkd))
