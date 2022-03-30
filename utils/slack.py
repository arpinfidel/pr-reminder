import json
import requests


headers = {
}

def format_slack_url(text:str, url:str)->str:
	return(f'<{url}|{text}>')

def send_message(chan:str, msg:str)->requests.Response:
	url = "https://slack.com/api/chat.postMessage"
	payload = {
		"channel": chan,
		"text": msg,
	}

	res = requests.post(url, headers=headers, json=payload)
	return res

def update_message(chan:str, ts:str, msg:str)->requests.Response:
	url = "https://slack.com/api/chat.update"

	payload = {
		"channel": chan,
		"ts": ts,
		"text": msg,
	}

	res = requests.post(url, headers=headers, json=payload)
	return res

def get_history(chan:str)->requests.Response:
	url = f'https://slack.com/api/conversations.history?channel={chan}'
	res = requests.get(url, headers=headers)
	return res


# res = send_message(channel, "test")
# res = update_message(channel, res.json()["ts"], "test edit")
# print(res.text)