from dataclasses import dataclass, field

@dataclass
class User:
	initials : str = ""
	github   : str = ""
	slack_id : str = ""

@dataclass
class Reviewer:
	github : str = ""
	review : str = ""

@dataclass
class PullRequest:
	title     : str  = ""
	author    : str  = ""
	num       : int  = 0
	base      : str  = ""
	is_draft  : bool = False
	url       : str  = ""
	reviewers : list[Reviewer] = field(default_factory=list[Reviewer])
	ap_count  : int  = 0
	rc_count  : int  = 0
	cm_count  : int  = 0

	requested_reviewers:list[str] = field(default_factory=list[str])