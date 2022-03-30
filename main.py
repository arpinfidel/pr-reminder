import dataclasses
import json
import time
from datetime import datetime

import slack
import github
import config
import utils
import entity

def make_msg()->str:
	msg = "`< PR REMINDER >`\n"
	msg += f'{config.team}\n'
	for repo_name, repo_data in config.repos:
		prs = github.get_prs(repo_name, "open")

		approved         :list[entity.PullRequest] = []
		needs_approval   :list[entity.PullRequest] = []
		changes_requested:list[entity.PullRequest] = []
		draft = []

		for gpr in prs:
			pr = entity.PullRequest(
				title    = gpr["title"],
				author   = gpr["user"]["login"],
				num      = gpr["number"],
				base     = gpr["base"]["ref"],
				is_draft = gpr["draft"],
				url      = f'https://github.com/tokopedia/{repo_name}/pull/{gpr["number"]}',

				requested_reviewers = [req["login"] for req in gpr["requested_reviewers"]],
			)

			if pr.author in config.user_blacklist:
				continue
				
			if pr.is_draft:
				draft.append(pr)
				continue

			reviews = github.get_reviews(repo_name, pr.num)

			latest_reviews:dict[str, entity.Reviewer]= {}
			for rev in reviews:
				rv = entity.Reviewer(
					github = rev["user"]["login"],
					review = rev["state"],
				)

				if rv.github == pr.author:
					continue

				if rv.github in latest_reviews and rv.review == "COMMENTED":
					continue

				latest_reviews[rv.github] = rv
			

			for rv in latest_reviews.values():
				pr.reviewers.append(rv)
				if rv.review == "APPROVED":
					pr.ap_count += 1
				elif rv.review == "CHANGES_REQUESTED":
					pr.rc_count += 1
				elif rv.review == "COMMENTED":
					pr.cm_count += 1

			print(json.dumps(dataclasses.asdict(pr), indent=2))

			if pr.rc_count > 0:
				changes_requested.append(pr)
				continue

			if pr.ap_count >= 2:
				approved.append(pr)
				continue

			needs_approval.append(pr)

		msg += f'>{repo_name}\n'
		
		if approved:
			msg += ":approved2: APPROVED (>=2):\n"
			for pr in reversed(approved):
				url = utils.slack.format_slack_url("#"+str(pr.num), pr.url)
				initials = config.users[pr.author].initials
				slack_id = config.users[pr.author].slack_id
				msg += f'  {url} [`{initials:^5}`] [ {pr.base:^7} ] {pr.title} {slack_id}\n'
			msg += "\n"
			
			if "deploy_msg" in repo_data:
				msg += repo_data["deploy_msg"]
				msg += "\n"

		if needs_approval:
			msg += ":question: NEEDS REVIEW:\n"
			for pr in reversed(needs_approval):
				url = utils.slack.format_slack_url("#"+str(pr.num), pr.url)
				initials = config.users[pr.author].initials
				msg += f'  {url} [`{initials:^5}`] [ {pr.base:^7} ] {pr.title} ({pr.ap_count}/2)'
				if pr.cm_count > 0:
					msg += " `has comments`"
				if pr.requested_reviewers:
					msg += f' {" ".join([config.users[req].slack_id for req in pr.requested_reviewers])}'
				msg += "\n"
			msg += "\n"

		if changes_requested:
			msg += ":request-changes: CHANGES REQUESTED:\n"
			for pr in reversed(changes_requested):
				url = utils.slack.format_slack_url("#"+str(pr.num), pr.url)
				initials = config.users[pr.author].initials
				slack_id = config.users[pr.author].slack_id
				msg += f'  {url} [`{initials:^5}`] [ {pr.base:^7} ] {pr.title} {slack_id}\n'
			msg += "\n"

		if draft:
			msg += "DRAFT:\n"
			for pr in reversed(draft):
				url = utils.slack.format_slack_url("#"+str(pr.num), pr.url)
				initials = config.users[pr.author].initials
				msg += f'  {url} [`{initials:^5}`] [ {pr.base:^7} ] {gpr.title}\n'
			msg += "\n"
		
		msg += "\n"

	return msg


while True:
	try:
		last_ts = slack.get_last_ts(config.channel)
		print(f'{last_ts=}')
		last_dt = datetime.fromtimestamp(float(last_ts))
		msg = make_msg()
		print(f'{msg=}')

		now = datetime.now()
		if (now - last_dt).total_seconds() <= 2 * 3600 or now.hour != 9 or (now.hour == 9 and now.minute < 30):
			res = utils.slack.update_message(config.channel, last_ts, msg)
			print("update", last_ts)
			print(res.text)
			if res.json()["ok"]:
				time.sleep(15)
				continue
		
		res = utils.slack.send_message(config.channel, msg)
		print("send")
		print(res.text)


		time.sleep(15)
	except Exception as e:
		print(e)
		pass

# print(time.time()-1648181970.939829)