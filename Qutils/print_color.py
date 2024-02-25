from typing import Literal


def cprint(msg, color:Literal['red','green']):
    name = ['green', 'red', 'reset']
    shell = "\033[32m", "\033[31m", "\033[0m"
    cmap = dict(zip(name, shell))
    print(f"{cmap[color]}{msg}{cmap['reset']}")
    if shell=='green':
        print(f"{cmap[color]}{msg}{cmap['reset']}")
    elif shell =='red':
        print(f"{cmap[color]}{msg}{cmap['reset']}")



if __name__ == "__main__":
    cprint('hi','green')
    cprint('hi','red')