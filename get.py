import requests

def get_request():
	x = requests.get('https://marketmoves.onrender.com')
	print(x.status_code)