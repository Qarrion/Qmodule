iprint = lambda x: print(f"TYPE(x = {type(x)}) VALUE({x = })")




if __name__ == "__main__":
    
    from datetime import datetime
    dd = datetime.now()
    iprint(dd)