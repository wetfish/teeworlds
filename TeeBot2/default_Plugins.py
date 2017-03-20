
class default_Plugins():
    def __init__(self, plugin_loader):
        self.register = plugin_loader.register

        from Plugins import Chat_commands
        self.register(Chat_commands.Chat())

        from Plugins import Spree_notifications
        self.register(Spree_notifications.Spree())

#        from Plugins import Chat_Logger
#        self.register(Chat_Logger.Logger())
