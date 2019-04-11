# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 23:37:38 2019

@author: Guilherme
"""

class Character:
    
    def __init__(self, name):
        self.name = name
        self.relations = []
        
    def set_alias(self,alias):
        self.alias = alias
    
    def set_relation(self,target,type_):
        self.relations.append(Relation(self.name,type_,target.name))
        
class Relation:
    
    def __init__(self, char1, type_, char2):
        self.char1 = char1
        self.type_ = type_
        self.char2 = char2
        
    def print_(self):
        string = self.char2 + ' is ' + self.char1 +"'s " + self.type_
        print(string)
        return string