import utils.slack as slack
import json

def get_last_ts(channel:str)->str:
	res = slack.get_history(channel)
	res = res.json()
	# print(json.dumps(res, indent=4))
	msg = [x for x in res["messages"] if "bot_id" in x and x["bot_id"] == "B02GSL83WH4" and x["text"].startswith("`&lt; PR REMINDER &gt;`")]
	if len(msg) == 0:
		return "0"
	return msg[0]["ts"]