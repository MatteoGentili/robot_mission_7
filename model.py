from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random
import tkinter as tk
from tqdm import trange
from time import sleep

from agents import GreenRobot, YellowRobot, RedRobot, CommunicatingGreenRobot, CommunicatingYellowRobot, CommunicatingRedRobot, RandomGreenRobot, RandomYellowRobot, RandomRedRobot
from objects import GreenWasteAgent, HazardGrid, WasteAgent, YellowWasteAgent, RedWasteAgent

from mesa_com.communication import MessageService, CommunicatingAgent


class Environnement(Model):
    def __init__(self, Nr, Nw, L, H, debug=False, draw=True):
        super().__init__()
        self.spawn_rate = 0.0
        self.debug = debug
        self.draw = draw
        self.num_robots = Nr
        self.num_waste = Nw

        self.grid_len = L
        self.grid_height = H
        self.full_recycled = 0
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            agent_reporters={"Carry": lambda a: len(a.inventory) if hasattr(a, "inventory") else 0},
            model_reporters={"NbWaste": lambda m: len([a for a in m.schedule.agents if isinstance(a, WasteAgent) and not a.suppressed]),
                            "FullRecycled": lambda m: m.full_recycled,
                            "green": lambda m: len([a for a in m.schedule.agents if isinstance(a, GreenWasteAgent) and not a.suppressed]),
                            "yellow": lambda m: len([a for a in m.schedule.agents if isinstance(a, YellowWasteAgent) and not a.suppressed]),
                            "red": lambda m: len([a for a in m.schedule.agents if isinstance(a, RedWasteAgent) and not a.suppressed])}
        )
        
        # Grid
        master = tk.Tk()
        width = L*60+40
        height = H*60+40
        master.geometry(f"{width}x{height}")
        self.master = master
        # Paramètres = (master, width, height, n_zones=3)
        self.grid = HazardGrid(master, L, H, 3)

        self.spawn_agents()

    def spawn_agents(self):
        # Agents Waste
        # self.W = dict()
        Nwg, Nwy, Nwr = int(self.num_waste*0.7), int(self.num_waste*0.2), int(self.num_waste*0.1)
        for i in range (Nwg):
            # put green wastes in the first zone
            pos = (random.randint(0, self.grid_len//3-1), random.randint(0, self.grid_height-1))
            w = GreenWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w) # gerer par les données de radio-activité
        for i in range (Nwy):
            # put yellow wastes in the second zone
            pos = (random.randint(self.grid_len//3, 2*self.grid_len//3-1), random.randint(0, self.grid_height-1))
            w = YellowWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w)
        for i in range (Nwr):
            # put red wastes in the third zone
            pos = (random.randint(2*self.grid_len//3, self.grid_len-1), random.randint(0, self.grid_height-1))
            w = RedWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w)

        # Agents Robots
        robot_classes = [GreenRobot, YellowRobot, RedRobot]
        for nb, classe, i in zip(self.num_robots, robot_classes, range(len(self.num_robots))):
            for j in range(nb):
                # get a random position in the according zone
                pos = random.randint(i*self.grid_len//3, (i+1)*self.grid_len//3-1), random.randint(0, self.grid_height-1)
                a = classe(self.next_id(), self, pos)
                self.grid.place_agent(a, pos)
                self.schedule.add(a)
                # print(a.border, a.type)

    def do(self, agent, action, **kwargs):
        if action == "move":
            if self.debug:
                print(agent.type, "Agent", agent.unique_id, "in pos", agent.pos, "moving to", kwargs["pos"], "in zone", self.grid.get_zone(kwargs["pos"]), "to", kwargs["objective"])
            self.grid.move_agent(agent, kwargs["pos"])
            grid_wastes = self.grid.get_wastes()
        elif action == "pick_up":
            if self.debug:
                print(agent.type, "Agent", agent.unique_id, "picking up waste", kwargs["waste"].unique_id)
            # remove the waste picked up from the grid
            self.grid.remove_agent(kwargs["waste"])
            # add the waste picked up to the agent
            agent.inventory.append(kwargs["waste"])
            grid_wastes = self.grid.get_wastes()
        elif action == "drop":
            if self.debug:
                print(agent.type, "Agent", agent.unique_id, "dropping waste")
            # kwargs here is empty
            # add a transformed waste to the grid according to the agent's color
            if isinstance(agent, GreenRobot):
                if len(agent.inventory) == 2:
                    for waste in agent.inventory:
                        waste.suppressed = True
                    waste = YellowWasteAgent(self.next_id(), self, agent.pos)
                    self.schedule.add(waste)
                    grid_wastes = self.grid.get_wastes()
                else:
                    waste = kwargs["waste"]
                    self.grid.place_agent(waste, agent.pos)
                    grid_wastes = self.grid.get_wastes()
                    # exclude the waste dropped by the agent
                    grid_wastes["green"].remove(waste)
            elif isinstance(agent, YellowRobot):
                if len(agent.inventory) == 2:
                    for waste in agent.inventory:
                        waste.suppressed = True
                    waste = RedWasteAgent(self.next_id(), self, agent.pos)
                    self.schedule.add(waste)
                    grid_wastes = self.grid.get_wastes()
                else:
                    waste = kwargs["waste"]
                    self.grid.place_agent(waste, agent.pos)
                    grid_wastes = self.grid.get_wastes()
                    # exclude the waste dropped by the agent
                    grid_wastes["yellow"].remove(waste)
            else:
                for waste in agent.inventory:
                    waste.suppressed = True
                waste = None
                self.full_recycled += 1
                grid_wastes = self.grid.get_wastes()
            agent.inventory = []
            self.grid.place_agent(waste, agent.pos) if waste is not None else None
        elif action == "give":
            src, dst = agent, kwargs["dest"]
            if self.debug:
                print(src.type, "Agent", src.unique_id, "giving waste to", dst.type, "Agent", dst.unique_id)
            waste = src.inventory.pop()
            dst.inventory.append(waste)
            grid_wastes = self.grid.get_wastes()
        
        elif action == "take":
            src, dst = kwargs["src"], agent
            if self.debug:
                print(src.type, "Agent", src.unique_id, "giving waste to", dst.type, "Agent", dst.unique_id)
            waste = src.inventory.pop()
            dst.inventory.append(waste)
            grid_wastes = self.grid.get_wastes()
        else:
            print("Unknown action: ", action)
        percepts = {"pos": agent.pos, "inventory": agent.inventory, "wastes": grid_wastes, "robots": self.grid.get_robots()}
        return percepts

    def spawn(self, spawn_rate):
        if random.random() < spawn_rate:
            pos = (random.randint(0, self.grid_len//3-1), random.randint(0, self.grid_height-1))
            w = GreenWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            self.schedule.add(w)
            if self.debug:
                print("New waste spawned at", pos)

    # 1. this method performs only 1 step for all agents
    def one_step(self):

        self.datacollector.collect(self)
        self.schedule.step()
        step = self.schedule.steps
        if self.draw:
            self.grid.draw(step)
        self.master.update()
        sleep(0.1)
        self.spawn(self.spawn_rate)
    
    def count_wastes(self):
        return len([a for a in self.schedule.agents if isinstance(a, WasteAgent) and a.pos is not None])

    # 2. this method performs only n steps for all agents
    def run_n_steps(self,n):
        for i in trange(n):
            self.one_step()

    def terminated(self):
        if self.count_wastes() == 0:
            # check robots' inventories and see if green or yellow robots have 2 wastes, or red robots have 1 waste
            for a in self.schedule.agents:
                if isinstance(a, GreenRobot) or isinstance(a, YellowRobot):
                    if len(a.inventory) == 2:
                        return False
                elif isinstance(a, RedRobot):
                    if len(a.inventory) == 1:
                        return False
            return True
        return False
    
    def run_while(self):
        while not self.terminated():
            # print(self.count_wastes())
            self.one_step()
            nsteps = self.schedule.steps
            if (nsteps % 10 == 0 or self.terminated()) and self.debug:
                # print with a color the following message: "Wastes remaining in inventories: {len([a for a in self.schedule.agents if isinstance(a, WasteAgent) and not a.suppressed])}"
                print(f"\033[1;32;40mWastes remaining in inventories: {len([a for a in self.schedule.agents if isinstance(a, WasteAgent) and not a.suppressed])} : \n\t {sum([len(a.inventory) for a in self.schedule.agents if isinstance(a, GreenRobot)])} green, {sum([len(a.inventory) for a in self.schedule.agents if isinstance(a, YellowRobot)])} yellow, {sum([len(a.inventory) for a in self.schedule.agents if isinstance(a, RedRobot)])} red : \n\t\t {[f'{a.type} Robot {a.unique_id}' for a in self.schedule.agents if isinstance(a, Robot) and len(a.inventory) == 1]}\033[0m")
        self.datacollector.collect(self)


class RandomEnvironnement(Environnement):
    def __init__(self, Nr, Nw, L, H, debug=False):
        super().__init__(Nr, Nw, L, H, debug)

    def spawn_agents(self):
        # Agents Waste
        # self.W = dict()
        Nwg, Nwy, Nwr = int(self.num_waste*0.7), int(self.num_waste*0.2), int(self.num_waste*0.1)
        for i in range (Nwg):
            # put green wastes in the first zone
            pos = (random.randint(0, self.grid_len//3-1), random.randint(0, self.grid_height-1))
            w = GreenWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w) # gerer par les données de radio-activité
        for i in range (Nwy):
            # put yellow wastes in the second zone
            pos = (random.randint(self.grid_len//3, 2*self.grid_len//3-1), random.randint(0, self.grid_height-1))
            w = YellowWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w)
        for i in range (Nwr):
            # put red wastes in the third zone
            pos = (random.randint(2*self.grid_len//3, self.grid_len-1), random.randint(0, self.grid_height-1))
            w = RedWasteAgent(self.next_id(), self, pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w)

        # Agents Robots
        robot_classes = [RandomGreenRobot, RandomYellowRobot, RandomRedRobot]
        for nb, classe, i in zip(self.num_robots, robot_classes, range(len(self.num_robots))):
            for j in range(nb):
                # get a random position in the according zone
                pos = random.randint(i*self.grid_len//3, (i+1)*self.grid_len//3-1), random.randint(0, self.grid_height-1)
                a = classe(self.next_id(), self, pos)
                self.grid.place_agent(a, pos)
                self.schedule.add(a)
                # print(a.border, a.type)


class CommunicationEnvironnement(Environnement):
    def __init__(self, Nr, Nw, L, H, debug=False, draw=True):
        super().__init__(Nr, Nw, L, H, debug, draw)
        self.datacollector = DataCollector(
            agent_reporters={"Carry": lambda a: len(a.inventory) if hasattr(a, "inventory") else 0},
            model_reporters={"NbWaste": lambda m: len([a for a in m.schedule.agents if isinstance(a, WasteAgent) and not a.suppressed]),
                            "FullRecycled": lambda m: m.full_recycled,
                            "green": lambda m: len([a for a in m.schedule.agents if isinstance(a, GreenWasteAgent) and not a.suppressed]),
                            "yellow": lambda m: len([a for a in m.schedule.agents if isinstance(a, YellowWasteAgent) and not a.suppressed]),
                            "red": lambda m: len([a for a in m.schedule.agents if isinstance(a, RedWasteAgent) and not a.suppressed]),
                            "NbMessages_green": lambda m: sum(len(a.messages_sent) for a in m.schedule.agents if isinstance(a, CommunicatingGreenRobot)),
                            "NbMessages_yellow": lambda m: sum(len(a.messages_sent) for a in m.schedule.agents if isinstance(a, CommunicatingYellowRobot)),
                            "NbMessages_red": lambda m: sum(len(a.messages_sent) for a in m.schedule.agents if isinstance(a, CommunicatingRedRobot))}

        )
    
    def spawn_agents(self):
        self.__messages_service = MessageService(self.schedule)
        # Agents Waste
        # self.W = dict()
        Nwg, Nwy, Nwr = int(self.num_waste*0.7), int(self.num_waste*0.2), int(self.num_waste*0.1)
        for i in range (Nwg):
            # put green wastes in the first zone
            pos = (random.randint(0, self.grid_len//3-1), random.randint(0, self.grid_height-1))
            w = GreenWasteAgent(self.next_id(), self, pos)
            if self.debug:
                print("Green waste spawned at", pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w) # gerer par les données de radio-activité
        for i in range (Nwy):
            # put yellow wastes in the second zone
            pos = (random.randint(self.grid_len//3, 2*self.grid_len//3-1), random.randint(0, self.grid_height-1))
            w = YellowWasteAgent(self.next_id(), self, pos)
            if self.debug:
                print("Yellow waste spawned at", pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w)
        for i in range (Nwr):
            # put red wastes in the third zone
            pos = (random.randint(2*self.grid_len//3, self.grid_len-1), random.randint(0, self.grid_height-1))
            w = RedWasteAgent(self.next_id(), self, pos)
            if self.debug:
                print("Red waste spawned at", pos)
            self.grid.place_agent(w, pos)
            # self.W.append(w)
            self.schedule.add(w)

        # Agents Robots
        robot_classes = [CommunicatingGreenRobot, CommunicatingYellowRobot, CommunicatingRedRobot]
        for nb, classe, i in zip(self.num_robots, robot_classes, range(len(self.num_robots))):
            for j in range(nb):
                # get a random position in the according zone
                pos = random.randint(i*self.grid_len//3, (i+1)*self.grid_len//3-1), random.randint(0, self.grid_height-1)
                a = classe(self.next_id(), self, pos)
                if self.debug:
                    print("Robot", a.unique_id, "spawned at", pos)
                self.grid.place_agent(a, pos)
                self.schedule.add(a)
                # print(a.border, a.type)

    def terminated(self):
        if self.count_wastes() == 0:
            nb_wastes=0
            # check robots' inventories and see if green or yellow robots have 2 wastes, or red robots have 1 waste
            for a in self.schedule.agents:
                if isinstance(a, GreenRobot) or isinstance(a, YellowRobot):
                    if len(a.inventory) == 2:
                        return False
                    elif len(a.inventory) == 1:
                        nb_wastes += 1
                elif isinstance(a, RedRobot):
                    if len(a.inventory) == 1:
                        return False
            if nb_wastes > 2:
                return False
            return True
        return False

    def one_step(self):

        self.datacollector.collect(self)
        
        self.__messages_service.dispatch_messages()

        self.schedule.step()
        step = self.schedule.steps
        if self.draw:
            self.grid.draw(step)
        self.master.update()
        sleep(0.1)
        self.spawn(self.spawn_rate)
