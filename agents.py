from mesa import Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random

from .model import HazardGrid

##########################
###### Waste Agents ######
##########################

class WasteAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

class GreenWasteAgent(WasteAgent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.type = "Green"

class YellowWasteAgent(WasteAgent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.type = "Yellow"

class RedWasteAgent(WasteAgent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.type = "Red"