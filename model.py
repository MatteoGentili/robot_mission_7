from mesa import Agent, Model
from mesa.time import RandomActivation
import random

from agents import GreenRobot

class Environnement(Model):
    def __init__(self, Nr, Nw, L):
        super().__init__()

        self.num_robots = Nr
        self.num_waste = Nw

        self.grid_len = L
        self.scheduler = RandomActivation(self)  
        
        # Grid
        self.grid = Grid (L)

        # Agents Waste
        self.W = dict()
        for i in range (Nw):
            pos = random.randint(0, L)
            w = waste(pos, self)
            self.W.append(w)
            #self.scheduler.add(w) # gerer par les données de radio-activité

        # Agents Robots
        for i in range(self.num_agents):
            a = GreenRobot(i, self)  # Pass 'self' to give the agent access to the model
            #self.scheduler.add(a)

    # 1. this method performs only 1 step for all agents
    def one_step(self):
        # get waste position
        wPos = [w.pos() for w in self.W]

        
        distance_robot = []
        self.scheduler.step()


        self.grid.print()

    # 2. this method performs only n steps for all agents
    def run_n_steps(self,n):
        for i in range(n):
            self.one_step()
        return [i.wealth for i in self.scheduler.agents]