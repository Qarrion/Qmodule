def rprint(elm:str,idx:int,grp):
    lst = len(grp)-1
    print(f"\r {elm}\033[K",  end="\n" if idx==lst else '')