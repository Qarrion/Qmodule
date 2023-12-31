from Qupbit.api import market



def get_market(quote:str=None, base:str=None):
    resp = market.get()
    resp = market.filter(resp['payload'], quote, base)
    return [e['market'] for e in resp]


