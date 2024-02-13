import Utils
import liveUtils
from runLive import Live
from datetime import datetime
from Users import User


if __name__ == '__main__':
    client = User("kotak")
    runLive = Live(Utils.indexToken)
    currMin = None
    while "00:00:00" <= datetime.now().strftime("%H:%M:%S") <= "24:29:00":
        if datetime.now().strftime("%M") != currMin:
            runLive.callback_method(client.client)
            currMin = datetime.now().strftime("%M")
        if runLive.mtmhit:
            break

