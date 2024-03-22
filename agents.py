from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carry = 0

    def move(self):
        self.model.grid.move_agent(self, "position_donnée_par_environnement")

class GreenRobot(Robot):
    """
    Green Robot:
        ○ walk to pick up 2 initial wastes (i.e. green),
        ○ if possession of 2 green wastes then transformation into 1 yellow waste,
        ○ if possession of 1 yellow waste, transport it further east,
        ○ green robot cannot exceed zone z1.
    """

    def carry_waste(self):
        if "iswates" == True :
            self.carry += 1
    def fusion_waste(self):
        pass

    def move_to_yellow_robot(self):
        pass

    def step(self):
        self.move()
        if self.carry < 2:
            self.carry_waste()
        elif self.carry == 2: 
            self.fusion_waste()
            self.move_to_yellow_robot()

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
        

