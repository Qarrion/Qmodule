import uuid 

ud = uuid.uuid4()
print(type(ud), ud)
print(type(str(ud)), str(ud))
print(str(ud)[:8])



import json
ticket = str(uuid.uuid4())[:8]
type = 'ticker'
codes=['KRW-BTC']
format='SIMPLE'

request_format = [
    {"ticket": ticket},
    {
        "type": type,
        "codes": codes,
        "isOnlyRealtime": True
    },
    {"format": format}
]

print(json.dumps(request_format))