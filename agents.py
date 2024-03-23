from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

##########################
###### Robot Agents ######
##########################

class Robot(Agent):
    """
    Carry is a variable that counts the number of wastes carried by the robot (0, 1 or 2)
    Go_east is a boolean that indicates if the robot should go east, its value is True when the robots reaches maximum carrying capacity
    Made_action is a boolean that indicates if the robot has already made an action in the current step
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carry = 0
        self.go_east = False
        self.made_action = False

    def move(self):
        if self.go_east:
            self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1]))
            self.made_action = True
        else:
            self.model.grid.move_agent(self, "position_donnée_par_environnement") # TO COMPLETE
            self.made_action = True

class GreenRobot(Robot):
    """
    Green Robot:
        ○ walk to pick up 2 initial wastes (i.e. green),
        ○ if possession of 2 green wastes transport them further east,
        ○ if possession of 2 green wastes and at the border of green zone, unload them,
        ○ green robot cannot exceed zone z1.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.border = self.model.width//3 - 1 # frontière de la zone verte


    def carry_waste(self):
        if self.carry < 2:
            if "is_green_waste" :  # TO COMPLETE
                self.carry += 1
                self.made_action = True
        
        if self.carry == 2:
            self.go_east = True

    def unload_waste(self):
        self.carry = 0
        self.go_east = False
        self.model.make_agent("YellowWasteAgent", self.pos) # TO COMPLETE
        self.made_action = True

    def step(self):
        self.carry_waste()
        if not self.made_action:
            if self.pos[0] == self.border and self.carry == 2:
                self.unload_waste()
        if not self.made_action:
            self.move()
        self.made_action = False

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
        

