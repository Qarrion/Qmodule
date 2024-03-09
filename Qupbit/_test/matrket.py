
import requests
div = lambda x:  print(f"{"="*60} [{x}]")

url_market = "https://api.upbit.com/v1/market/all"
params = {"isDetails": 'true'}
params = {"isDetails": 'false'}
headers = {"Accept": "application/json"}

resp =  requests.get(url=url_market, headers=headers, params=params)


# print(resp.text)
div('header')
print(resp.headers)

div('json')
print(type(resp.json()))
print(resp.json()[0])


from Qupbit.tools.parser import Parser

div('remaining')
parser = Parser()
rem = parser.remaining(resp.headers['Remaining-Req'])
print(rem)