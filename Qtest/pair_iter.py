my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]

if len(my_list) % 2 != 0:
    my_list.append(None)

it = iter(my_list)
for pair in zip(it, it):
    if pair[1] is None:
        target = (pair[0],)
    else:
        target = pair
    
    print(pair)
    