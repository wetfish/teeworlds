__author__ = 'Aleksi'
from subprocess import check_output
class Chat:

    def __init__(self):
        self.handle_events = ["CHAT"]
        self.commands = "commands.cfg"
        pass
    def handle(self, event, bot, plugins):
        bot.debug("Chat_Commands is handling this.")
        msg = event["message"]
        nick = event["player_name"]
        id = event["player_id"]
        if "!" == msg[0]:
            with open(self.commands, "r", encoding="utf-8") as cmds:
                msgg = msg
                print("We got: {} as msgg.".format(msgg))
                lines = cmds.readlines()
                for x in lines:
                    split = x.split(" _ ")
                    if split[0] == msgg:
                        print(x)
                        bot.say(split[1].rstrip("\n"))
                    else:
                        pass
        if "!" != msg[0]:
            return
        ms = msg.split(' ', 1)
        if "!stats" == ms[0]:
            if len(ms) == 1:
                tee = bot.get_Tee(id)
            else:
                tee = bot.find_tee(ms[1])
                if tee == {}:
                     bot.say("could not find tee {}".format(ms[1]))
                     return
            x = 1
            while x <= 4:
                bot.say(tee.gen_stats_line(x))
                x += 1
        elif "!statsall" == ms[0]:
            if len(ms) == 1:
                tee = bot.get_Tee_persistent(id)
            else:
                tee = bot.find_ptee(ms[1])
                if tee == {}:
                    bot.say("could not find tee {}".format(ms[1]))
                    return
            x = 1
            while x <= 4:
                bot.say(tee.gen_stats_line(x))
                x += 1
        elif "!lag" == msg:
            lag = str(check_output(["ifstat", "1", "1"])).split()
            down = lag[-2]
            up = lag[-1].replace("\\", "").replace("n", "").replace("\n","").replace("'", "")
            bot.say("In: {}kb/s  Out: {}kb/s.".format(down, up))
