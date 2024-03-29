from mesa.space import MultiGrid
from mesa.agent import Agent
import matplotlib.pyplot as plt
import numpy as np
import random
import tkinter as tk
from agents import Robot

##################
###### Grid ######
##################

# class HazardGrid(MultiGrid):
#     def __init__(self, width, height, n_zones=3):
#         super().__init__(width+1, height, False)
#         self.n_zones = n_zones
#         self.zone_width = width // n_zones
#         self.radioactivity_map = np.ones((height, width+1))
#         # last column is the general waste disposal zone

#         for i in range(n_zones):
#             # for each zone, assign a random radioactivity level (between 0.0 and 0.33 for zone 1, 0.33 and 0.66 for zone 2, 0.66 and 1.0 for zone 3)
#             random_values = np.random.uniform(i / n_zones, (i + 1) / n_zones, (self.height, self.zone_width))
#             self.radioactivity_map[:, i*self.zone_width:(i+1)*self.zone_width] = random_values

    
#     def print(self, wastes_pos, robots_pos):
#         """
#         Plot the grid with wastes and robots
#         """
#         fig, ax = plt.subplots()
#         ax.imshow(self.radioactivity_map, cmap='afmhot', interpolation='nearest')
#         for waste in wastes_pos:
#             # adds a "W" to the waste position
#             ax.text(waste[0], waste[1], "W", color='green', fontsize=12)
#         for robot in robots_pos:
#             # adds a "R" to the robot position
#             ax.text(robot[0], robot[1], "R", color='red', fontsize=12)
#         plt.show()

# if __name__=="__main__":
#     grid = HazardGrid(15, 5, 1)
#     grid.print([(1, 1), (2, 2)], [(3, 3), (4, 4)])


class HazardGrid(MultiGrid):
    def __init__(self, master, width, height, n_zones=3):
        super().__init__(width, height, False)
        self.master = master
        self.width = width
        self.height = height
        self.n_zones = n_zones
        self.zone_width = width // n_zones
        assert width % n_zones == 0, "Width must be a multiple of the number of zones"
        self.radioactivity_map = np.ones((height, width))
        # last column is the general waste disposal zone
        # print("n_zones = ",n_zones)
        for i in range(n_zones):
            # for each zone, assign a random radioactivity level
            random_values = np.random.uniform(i / n_zones, (i + 1) / n_zones, (self.height, self.zone_width))
            self.radioactivity_map[:, i*self.zone_width:(i+1)*self.zone_width] = random_values
        # General waste disposal zone : 200 radioactivity at end of red zone, arbitrary y
        self.radioactivity_map[random.randint(0, self.height-1), -1] = 200
        # print("radioactivity_map = ",self.radioactivity_map)
        # No waste, just ground
        # for _ in range(0, 30):
        #     i = np.random.randint(0, self.height)
        #     j = np.random.randint(0, self.width+1)
        #     self.radioactivity_map[i][j] = 10
    
    def get_zone(self, pos):
        """
        Get the zone of a position
        """
        return pos[0] // self.zone_width

    def get_all_agents(self):
        """
        Get all the agents in the grid
        """
        agents = []
        for cell in self.coord_iter():
            cell_content, (x, y) = cell
            for agent in cell_content:
                agents.append(agent)
        return agents


    def get_wastes(self):
        """
        Get the wastes positions
        Returns a dictionary with the type of waste as key and a list of agents as value
        """
        wastes = {
            "green": [],
            "yellow": [],
            "red": []
        }
        for agent in self.get_all_agents():
            if isinstance(agent, WasteAgent):
                wastes[agent.type.lower()].append(agent)
        return wastes

    def get_robots(self):
        """
        Get the robots positions
        """
        robots = {
            "green": [],
            "yellow": [],
            "red": []
        }
        for agent in self.get_all_agents():
            if isinstance(agent, Robot):
                robots[agent.type.lower()].append(agent)
        return robots

    def get_distance(self, pos1, pos2):
        """
        Get the Manhattan distance between two positions
        """
        if pos1 is None or pos2 is None:
            return np.inf
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def draw(self):
        """
        Draw the grid with wastes and robots
        """
        cell_width = 60
        cell_height = 60

        canvas = tk.Canvas(self.master, width=self.width*cell_width, height=self.height*cell_height)
        canvas.pack()
        wastes_pos = {}
        robots_pos = {}
        for agent in self.get_all_agents():
            if isinstance(agent, WasteAgent):
                if agent.pos is None:
                    continue
                wastes_pos[agent] = agent.pos
            elif isinstance(agent, Robot):
                robots_pos[agent] = agent.pos

        for i in range(self.height):
            for j in range(self.width):
                x0 = j * cell_width
                y0 = i * cell_height
                x1 = x0 + cell_width
                y1 = y0 + cell_height
                color = self.get_color(self.radioactivity_map[i][j])
                canvas.create_rectangle(x0, y0, x1, y1, fill=color)

        for waste in wastes_pos:
            pos = wastes_pos[waste]
            x = pos[0] * cell_width + cell_width / 2
            y = pos[1] * cell_height + cell_height / 2
            fill = 'green' if waste.type == "Green" else 'yellow' if waste.type == "Yellow" else 'red'
            # make the letter more visible by adding a black outline
            text_item = canvas.create_text(x, y, text="W", fill=fill, anchor='center', font=("Helvetica", 16, "bold"))
            bbox = canvas.bbox(text_item)
            rect_item = canvas.create_rectangle(bbox, outline="white", fill="black")
            canvas.tag_raise(text_item,rect_item)

        for robot in robots_pos:
            pos = robots_pos[robot]
            x = pos[0] * cell_width + cell_width / 2
            y = pos[1] * cell_height + cell_height / 2
            fill = 'green' if robot.type == "green" else 'yellow' if robot.type == "yellow" else 'red'
            text_item = canvas.create_text(x, y, text="R", fill=fill, anchor='center', font=("Helvetica", 16, "bold"))
            bbox = canvas.bbox(text_item)
            rect_item = canvas.create_rectangle(bbox, outline="white", fill="black")
            canvas.tag_raise(text_item,rect_item)
    
    def print(self):
        """
        Plot the grid with wastes and robots
        """
        wastes_pos = {}
        robots_pos = {}
        for agent in self.get_all_agents():
            if isinstance(agent, WasteAgent):
                if agent.pos is None:
                    continue
                wastes_pos[agent] = agent.pos
            elif isinstance(agent, Robot):
                robots_pos[agent] = agent.pos
        fig, ax = plt.subplots()
        ax.imshow(self.radioactivity_map, cmap='afmhot', interpolation='nearest')
        for waste in wastes_pos:
            # adds a "W" to the waste position
            pos = wastes_pos[waste]
            color = 'green' if waste.type == "Green" else 'yellow' if waste.type == "Yellow" else 'red'
            ax.text(pos[0], pos[1], "W", color=color, fontsize=12)
        for robot in robots_pos:
            # adds a "R" to the robot position
            pos = robots_pos[robot]
            color = 'green' if robot.type == "green" else 'yellow' if robot.type == "yellow" else 'red'
            ax.text(pos[0], pos[1], "R", color=color, fontsize=12)
        plt.show()

    def get_color(self, radioactivity):
        # Map radioactivity to shades of yellow, orange, and red
        if radioactivity < 0.33:
            # Green to dark green
            red = 0
            green = int(255 * (radioactivity / 0.33))
            blue = 0
        elif radioactivity < 0.66:
            # Yellow to orange
            red = 230
            green = int(255 * ((0.66 - radioactivity) / 0.33))
            blue = 0
        elif radioactivity > 0.66 and radioactivity < 1:
            # Red
            red = int(255 * ((0.99 - radioactivity) / 0.33))
            green = 0
            blue = 0
        # Special color for the general waste disposal zone
        elif radioactivity == 200:
            red = 95
            green = 95
            blue = 95
        # Special color for no waste, just ground
        elif radioactivity == 10:
            red = 217
            green = 225
            blue = 147
        else:
            # Default color for any other radioactivity value
            red = 160
            green = 147
            blue = 225

        return "#{:02x}{:02x}{:02x}".format(red, green, blue)
if __name__=="__main__":
    root = tk.Tk()
    root.geometry("400x300")
    grid = HazardGrid(root, 15, 15, 3)
    grid.draw([(1, 1), (2, 2)], [(3, 3), (4, 4)])
    root.mainloop()



##########################
###### Waste Agents ######
##########################

class WasteAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
    
    def step(self):
        pass

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