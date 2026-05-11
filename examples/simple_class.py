class HelloWorldClass:
    name: str
    age: int = 0

    def __init__(self, name: str):
        self.name = name

    def say_hello(self) -> str:
        return f"Hello, {self.name}"

def say_hello(name: str) -> str:
    return f"Hello, {name}"

def say_goodbye(name: str) -> str:
    return f"Goodbye, {name}"