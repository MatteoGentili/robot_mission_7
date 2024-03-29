from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random

from agents import GreenRobot, YellowRobot, RedRobot
from objects import GreenWasteAgent, HazardGrid, WasteAgent, YellowWasteAgent, RedWasteAgent


class Environnement(Model):
    def __init__(self, Nr, Nw, L):
        super().__init__()

        self.num_robots = Nr
        self.num_waste = Nw

        self.grid_len = L
        self.scheduler = RandomActivation(self)
        self.datacollector = DataCollector(
            agent_reporters={"Carry": lambda a: len(a.inventory)},
            model_reporters={"NbWaste": lambda m: len([a for a in m.schedule.agents if isinstance(a, WasteAgent)])}
        )
        
        # Grid
        master = "TO COMPLETE"
        self.grid = HazardGrid(master, L, 1, 1)

        # Agents Waste
        # self.W = dict()
        for i in range (Nw):
            pos = random.randint(0, L)
            w = GreenWasteAgent(i, self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.scheduler.add(w) # gerer par les données de radio-activité

        # Agents Robots
        for i in range(self.num_agents):
            pos = random.randint(0, L)
            a = GreenRobot(i, self)  # Pass 'self' to give the agent access to the model
            self.grid.place_agent(a, pos)
            self.scheduler.add(a)

    def do(self, agent, action, **kwargs):
        if action == "move":
            self.grid.move_agent(agent, kwargs["pos"])
        elif action == "pick_up":
            # remove the waste picked up from the grid
            self.grid.remove(kwargs["waste"])
            # add the waste picked up to the agent
            agent.inventory.append(kwargs["waste"])
        elif action == "drop":
            # kwargs here is empty
            # add a transformed waste to the grid according to the agent's color
            if isinstance(agent, GreenRobot):
                waste = YellowWasteAgent(self.next_id(), self, agent.pos)
            elif isinstance(agent, YellowRobot):
                waste = RedWasteAgent(self.next_id(), self, agent.pos)
            else:
                waste = kwargs["waste"]
                agent.inventory.remove(waste)
            self.grid.place_agent(waste, agent.pos)
        else:
            print("Unknown action: ", action)
        percepts = {"pos": agent.pos, "inventory": agent.inventory, "wastes": self.grid.get_wastes(), "robots": self.grid.get_robots()}
        return percepts



    # 1. this method performs only 1 step for all agents
    def one_step(self):
        # get waste position
        wPos = [w.pos() for w in self.W]

        
        distance_robot = []

        self.datacollector.collect(self)
        self.scheduler.step()


        self.grid.draw()

    # 2. this method performs only n steps for all agents
    def run_n_steps(self,n):
        for i in range(n):
            self.one_step()