import requests
import config

def get_prs(repo:str, state:str="")->dict[str,any]:
	url = "https://api.github.com/repos/tokopedia/{repo}/pulls?"
	url = url.format_map({
		"repo": repo,
	})
	params = {
		"state": state,
	}
	prs = requests.get(url, auth=config.basic, params=params, headers={
		"content-type": "application/json; utf-8"
	}).json()

	return prs

def get_reviews(repo:str, pr_num:int)->dict[str,any]:
	url = "https://api.github.com/repos/tokopedia/{repo}/pulls/{pr_num}/reviews"
	url = url.format_map({
		"repo": repo,
		"pr_num": pr_num,
	})
	params = {}
	reviews = requests.get(url, auth=config.basic, params=params).json()
	return reviews
