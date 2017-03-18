__author__ = 'Aleksi'
import threading
class Spree:
    def __init__(self):
        self.handle_events = ["KILL"]
        pass
    def handle(self, event, bot, plugins):
        bot.debug("Spree_notifications is handling this.")
        if event["event_type"] == "KILL":
            try:
                killer_tee = bot.get_Tee(event["killer_id"])
                victim_tee = bot.get_Tee(event["victim_id"])
                if (event["user_weapon_id"] == '-2') or (killer_tee.get_idnum() == victim_tee.get_idnum()):
                    killer_tee.suicide(1)
                elif event["user_weapon_id"] == '5': #sac
                    killer_tee.sac(1)
                    killer_tee.set_spree(killer_tee.get_spree() + 1)
                    if victim_tee.get_spree() >= 5:
                        t = threading.Timer(5, bot.shutdown, args=[victim_tee, killer_tee, victim_tee.get_spree()])
                        t.start()
                    victim_tee.killed(1)
                    victim_tee.set_spree(0)
                    bot.killSpree(killer_tee.get_idnum())
                    id = victim_tee.get_froze_by()
                    if killer_tee.get_idnum() == id:
                        bot.Multikill(killer_tee.get_idnum())
                    else:
                        bot.say("{} stole {}'s kill!".format(killer_tee.get_nick(),bot.get_Tee(id).get_nick()))
                        killer_tee.steal(1)
                elif event["user_weapon_id"] == '4': #freeze
                    killer_tee.freeze(1)
                    victim_tee.froze(killer_tee.get_idnum(), 1)
                elif event["user_weapon_id"] == '0': #hammer
                    killer_tee.hammer(1)
                    victim_tee.hammered(1)
            except (KeyError, NameError) as e:
                bot.exception(e)
                bot.debug("Guessing Tee didn't exist! Updating player list!")
                bot.writeLine("status")
        pass
