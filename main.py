import numpy as np

class Animal:
    def __init__(self, age) -> None:
        self.age = age

    def sleep(self):
        print("i schleep")


class Dog(Animal):
    def __init__(self, name) -> None:
        self.name = name

    def bark(self):
        print(f'Woof woof, my name is {self.name}')


dog_max = Dog("Max")
dog_max.sleep

