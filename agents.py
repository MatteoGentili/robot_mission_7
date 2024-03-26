from abc import ABC, abstractmethod
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random

from objects import HazardGrid, WasteAgent, GreenWasteAgent, YellowWasteAgent, RedWasteAgent

##########################
###### Robot Agents ######
##########################

class Robot(Agent):
    """
    Carry is a variable that counts the number of wastes carried by the robot (0, 1 or 2)
    Go_east is a boolean that indicates if the robot should go east, its value is True when the robots reaches maximum carrying capacity
    Made_action is a boolean that indicates if the robot has already made an action in the current step
    """

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.carry = 0
        self.go_east = False
        self.action = ""
        self.pos = pos
        self.border = None

    def get_new_pos(self):
        if self.go_east:
            return self.pos[0] + 1, self.pos[1]
        else:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
            possible_steps = [pos for pos in possible_steps if pos[0] < self.border] # Cannot go further east
            return random.choice(possible_steps)

class GreenRobot(Robot):
    """
    Green Robot:
        ○ walk to pick up 2 initial wastes (i.e. green),
        ○ if possession of 2 green wastes transport them further east,
        ○ if possession of 2 green wastes and at the border of green zone, unload a yellow waste,
        ○ green robot cannot exceed zone z1.
    """

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.border = self.model.width//3 - 1 # frontière de la zone verte


    def pick_up_waste(self):
        if self.carry < 2:
            if "is_green_waste" :  # TO COMPLETE
                self.action = "pick_ip"
                self.carry += 1
                g = GreenWasteAgent("new_id", self.model, self.pos) # TO COMPLETE (ex : self.model.generate_new_id)
                return g
        
        if self.carry == 2:
            self.go_east = True

    def drop_waste(self):
        if self.pos[0] == self.border and self.carry == 2:
            self.carry = 0
            self.go_east = False
            self.action = "drop"
            y = YellowWasteAgent("new_id", self.model, self.pos) # TO COMPLETE (ex : self.model.generate_new_id)
            return y

    def step(self):

        new_pos = self.get_new_pos()

        if self.action == "" :
            waste = self.pick_up_waste()

        if self.action == "" :
            waste = self.drop_waste()

        else :
            self.action = "move"

        self.model.do(self, self.action, pos = new_pos, waste = waste)
        self.action = ""

class YellowRobot(Robot):
    """
    Yellow Robot:
        ○ walk to pick up 2 initial yellow wastes,
        ○ if possession of 2 yellow wastes then transformation into 1 red waste,
        ○ if possession of 1 red waste, transport it further east,
        ○ yellow robot can move in zones z1 and z2.
    """

    def carry_waste(self):
        if "iswates" == True :
            self.carry += 1
    def fusion_waste(self):
        pass

    def move_to_red_robot(self):
        pass

    def step(self):
        self.move()
        if self.carry < 2:
            self.carry_waste()
        elif self.carry == 2: 
            self.fusion_waste()
            self.move_to_red_robot()

class RedRobot(Robot):
    """
    Red Robot:
        ○ walk to pick up 1 red waste,
        ○ if possession of 1 red waste then transport it further east on the “waste
        disposal zone”, the waste is then “put away”,
        ○ red robot can move in zones z1, z2 andz3.    
    """


    pass
        

