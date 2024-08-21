from typing import Optional, overload

@overload
def example_function(d,x: None = None) -> str:
    ...

@overload
def example_function(d,x: Optional[int]) -> str:
    ...

def example_function(d,x: Optional[int] = None) -> str:
    if x is None:
        return "No argument provided"
    else:
        return f"Argument provided: {x}"

# Test cases
print(example_function('a'))       # No argument provided
print(example_function('a',10))     # Argument provided: 10
print(example_function('a',None))  

from configparser import ConfigParser