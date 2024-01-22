import liveUtils
from runLive import Live


def on_message(message):
    runLive.callback_method(client, message)


def on_error(error_message):
    print(error_message)


if __name__ == '__main__':
    client = liveUtils.login(on_message, on_error)
    runLive = Live(client, "26009")
    client.subscribe(instrument_tokens=[{"instrument_token": "26009", "exchange_segment": "nse_cm"}], isIndex=False,
                     isDepth=False)
