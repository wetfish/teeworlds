__author__ = 'Aleksi'
import threading, time
class Spree:
    def __init__(self):
        self.handle_events = ["KILL"]
        pass
    def handle(self, event, bot, plugins):
        bot.debug("Spree_notifications is handling this.")
        if event["event_type"] == "KILL":
            try:
                ktga = bot.teelst.get_Tee(event["killer_id"]).attributes
                vtga = bot.teelst.get_Tee(event["victim_id"]).attributes
                ktpa = bot.plist.find_tee(ktg.get_nick()).attributes
                vtpa = bot.plist.find_tee(vtg.get_nick()).attributes
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
                        t = threading.Timer(5, bot.shutdown, args=[vtg, ktg, spr])
                        t.start()
                    vtga["deaths"] += 1
                    vtga["spree"] = 0
                    vtpa["deaths"] += 1
                    vtpa["spree"] = 0
                    bot.killSpree(kid)
                    id = vtga["froze_by"]
                    if kid == id:
                        bot.Multikill(kid)
                    else:
                        tt = bot.teelst.get_Tee(id)
                        bot.say("{} stole {}'s kill!".format(ktga["nick"], tt.get_nick()))
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
                bot.exception(e)
                bot.debug("Guessing Tee didn't exist! Updating player list!")
                bot.writeLine("status")
        pass
