class C:
    def __init__(self, t):
        self.t = t
    def __del__(self):
        print(f"{self.t} deleted")
    def __str__(self):
        return 'C'

d = C("123")
c = d

del d
print(c, end='')