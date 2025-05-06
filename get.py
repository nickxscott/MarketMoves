import requests as reqs

def get_request():
	x = reqs.get('https://marketmoves.onrender.com')
	print(x.status_code)