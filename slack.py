import utils.slack as slack

def get_last_ts(channel:str)->str:
	res = slack.get_history(channel)
	msg = [x for x in res.json()["messages"] if "bot_id" in x and x["bot_id"] == "B02GSL83WH4" and x["text"].startswith("`&lt; PR REMINDER &gt;`")][0]
	return msg["ts"]