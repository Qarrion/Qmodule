my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# if len(my_list) % 2 != 0:
#     my_list.append(None)

# it = iter(my_list)
# for pair in zip(it, it):
#     if pair[1] is None:
#         target = (pair[0],)
#     else:
#         target = pair
    
#     print(pair)
    

# ---------------------------------------------------------------------------- #
import itertools
# market_list를 N개씩 묶어서 처리합니다.

def chunk_market_list(market_list, N):
    it = iter(market_list)
    while True:
        chunk = list(itertools.islice(it, N))
        if not chunk:
            break
        yield chunk


print(list(chunk_market_list(my_list,5)))


for pair in chunk_market_list(my_list,5):
    print(pair)