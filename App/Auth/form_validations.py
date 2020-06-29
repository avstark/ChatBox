import re

regex= re.compile(r'^[a-zA-z0-9_-]+[.+a-zA-z0-9_-]*@[a-zA-z0-9_-]+[.a-zA-z0-9_]*\.[a-zA-z0-9_]+$')

def data_required(username, field):
	if username is None or username == "":
		return "This {} is required".format(field)

def validate_email(email, field):
	if data_required(email, field) is None:
		if regex.match(email) is None:
			return "Invalid email address"
		else:
			return
	return data_required(email, field)
