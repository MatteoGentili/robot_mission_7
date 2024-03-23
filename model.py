from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random

from agents import GreenRobot
from objects import GreenWasteAgent, HazardGrid, WasteAgent


class Environnement(Model):
    def __init__(self, Nr, Nw, L):
        super().__init__()

        self.num_robots = Nr
        self.num_waste = Nw

        self.grid_len = L
        self.scheduler = RandomActivation(self)
        self.datacollector = DataCollector(
            agent_reporters={"Carry": "carry"},
            model_reporters={"NbWaste": lambda m: len([a for a in m.schedule.agents if isinstance(a, WasteAgent)])}
        )
        
        # Grid
        self.grid = HazardGrid (L, 0, 1)

        # Agents Waste
        self.W = dict()
        for i in range (Nw):
            pos = random.randint(0, L)
            w = GreenWasteAgent(i, self, pos)
            self.W.append(w)
            #self.scheduler.add(w) # gerer par les données de radio-activité

        # Agents Robots
        for i in range(self.num_agents):
            a = GreenRobot(i, self)  # Pass 'self' to give the agent access to the model
            #self.scheduler.add(a)

    def do(self, agent, action, **kwargs):
        if action == "move":
            self.grid.move_agent(agent, kwargs["pos"])
        elif action == "pick_up":
            # remove the waste picked up from the grid
            self.grid.remove(kwargs["waste"])
            agent.carry += 1
        elif action == "drop":
            # add the waste dropped to the grid
            self.grid.place(kwargs["waste"], agent.pos)
            agent.carry == 0
        else:
            print("Unknown action: ", action)


    # 1. this method performs only 1 step for all agents
    def one_step(self):
        # get waste position
        wPos = [w.pos() for w in self.W]

        
        distance_robot = []

        self.datacollector.collect(self)
        self.scheduler.step()


        self.grid.print()

    # 2. this method performs only n steps for all agents
    def run_n_steps(self,n):
        for i in range(n):
            self.one_step()