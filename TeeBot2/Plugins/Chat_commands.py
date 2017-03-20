__author__ = 'Aleksi'
from subprocess import check_output
class Chat:

    def __init__(self):
        self.handle_events = ["CHAT"]
        self.commands = "commands.cfg"
        pass
    def handle(self, event, bot, plugins):
        #bot.debug("Chat_Commands is handling this.")
        msg = event["message"]
        if "!" != msg[0]:
            return
        nick = event["player_name"]
        id = event["player_id"]
        if "!top" == msg:
            bot.print_bests()
            return
        if "!topall" == msg:
            bot.print_bests_all()
            return
        ms = msg.split(' ', 1)
        tee = {}
        dbgm = "len = {:d} 1 = \"{:s}\", 2 = \"{:s}\"".format(len(ms),ms[0],ms[1])
        print(dbgm)
        if "!stats" == ms[0]:
            if len(ms) == 1:
                tee = bot.get_Tee(id)
            else:
                tee = bot.find_tee(ms[1])
        elif "!statsall" == ms[0]:
            if len(ms) == 1:
                tee = bot.get_Tee_persistent(id)
            else:
                tee = bot.find_ptee(ms[1])
        else:
            return

        if tee == {}:
            bot.say("could not find tee {}".format(ms[1]))
            return
        x = 1
        while x <= 4:
            bot.say(tee.gen_stats_line(x))
            x += 1

        #elif "!lag" == msg:
        #    lag = str(check_output(["ifstat", "1", "1"])).split()
        #    down = lag[-2]
        #    up = lag[-1].replace("\\", "").replace("n", "").replace("\n","").replace("'", "")
        #    bot.say("In: {}kb/s  Out: {}kb/s.".format(down, up))
