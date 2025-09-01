# make it Singleton
class Logger:
    def __init__(self, config):
        self.__system_logs = config["logging"]["system_logs"] == "on"
        pass

    def write(self, m: str, type: str = None):
        if type == "system":
            if self.__system_logs == True:
                # print() by default
                print("+ SYSTEM: " + m)
        else:
            # print() by default
            print(m)
