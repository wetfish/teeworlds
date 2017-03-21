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
        for x in range(1, 5):
            bot.say(tee.gen_stats_line(x))
