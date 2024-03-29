from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random
import tkinter as tk
from tqdm import trange

from agents import GreenRobot, YellowRobot, RedRobot
from objects import GreenWasteAgent, HazardGrid, WasteAgent, YellowWasteAgent, RedWasteAgent


class Environnement(Model):
    def __init__(self, Nr, Nw, L, H, debug=False):
        super().__init__()
        self.debug = debug
        self.num_robots = Nr
        self.num_waste = Nw

        self.grid_len = L
        self.grid_height = H
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            agent_reporters={"Carry": lambda a: len(a.inventory) if hasattr(a, "inventory") else 0},
            model_reporters={"NbWaste": lambda m: len([a for a in m.schedule.agents if isinstance(a, WasteAgent)])}
        )
        
        # Grid
        master = tk.Tk()
        master.geometry("400x300")
        self.master = master
        self.grid = HazardGrid(master, L, H, 3)

        # Agents Waste
        # self.W = dict()
        for i in range (Nw):
            pos = (random.randint(0, L-1), random.randint(0, H-1))
            w = GreenWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w) # gerer par les données de radio-activité

        # Agents Robots
        for i in Nr:
            for j in range(i):
                pos = (random.randint(0, L-1), random.randint(0, H-1))
                a = GreenRobot(self.next_id(), self, pos)
                self.grid.place_agent(a, pos)
                self.schedule.add(a)

    def do(self, agent, action, **kwargs):
        if action == "move":
            if self.debug:
                print("Agent", agent.unique_id, "moving to", kwargs["pos"])
            self.grid.move_agent(agent, kwargs["pos"])
        elif action == "pick_up":
            if self.debug:
                print("Agent", agent.unique_id, "picking up waste", kwargs["waste"].unique_id)
            # remove the waste picked up from the grid
            self.grid.remove_agent(kwargs["waste"])
            # add the waste picked up to the agent
            agent.inventory.append(kwargs["waste"])
        elif action == "drop":
            if self.debug:
                print("Agent", agent.unique_id, "dropping waste")
            # kwargs here is empty
            # add a transformed waste to the grid according to the agent's color
            if isinstance(agent, GreenRobot):
                waste = YellowWasteAgent(self.next_id(), self, agent.pos)
            elif isinstance(agent, YellowRobot):
                waste = RedWasteAgent(self.next_id(), self, agent.pos)
            else:
                waste = kwargs["waste"]
            agent.inventory = []
            self.grid.place_agent(waste, agent.pos)
        else:
            print("Unknown action: ", action)
        percepts = {"pos": agent.pos, "inventory": agent.inventory, "wastes": self.grid.get_wastes(), "robots": self.grid.get_robots()}
        return percepts



    # 1. this method performs only 1 step for all agents
    def one_step(self):

        self.datacollector.collect(self)
        self.schedule.step()


        # self.grid.draw()

    # 2. this method performs only n steps for all agents
    def run_n_steps(self,n):
        for i in trange(n):
            self.one_step()