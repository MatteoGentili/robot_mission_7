from mesa.space import MultiGrid
from mesa.agent import Agent
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk

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


class HazardGrid:
    def __init__(self, master, width, height, n_zones=3):
        self.master = master
        self.width = width
        self.height = height
        self.n_zones = n_zones
        self.zone_width = width // n_zones
        self.radioactivity_map = np.ones((height, width+1))
        # last column is the general waste disposal zone

        for i in range(n_zones):
            # for each zone, assign a random radioactivity level
            random_values = np.random.uniform(i / n_zones, (i + 1) / n_zones, (self.height, self.zone_width))
            self.radioactivity_map[:, i*self.zone_width:(i+1)*self.zone_width] = random_values

    def draw(self, wastes_pos, robots_pos):
        """
        Draw the grid with wastes and robots
        """
        cell_width = 20
        cell_height = 20

        canvas = tk.Canvas(self.master, width=self.width*cell_width, height=self.height*cell_height)
        canvas.pack()

        for i in range(self.height):
            for j in range(self.width+1):
                x0 = j * cell_width
                y0 = i * cell_height
                x1 = x0 + cell_width
                y1 = y0 + cell_height
                color = self.get_color(self.radioactivity_map[i][j])
                canvas.create_rectangle(x0, y0, x1, y1, fill=color)

        for waste in wastes_pos:
            x = waste[0] * cell_width
            y = waste[1] * cell_height
            canvas.create_text(x, y, text="W", fill='green')

        for robot in robots_pos:
            x = robot[0] * cell_width
            y = robot[1] * cell_height
            canvas.create_text(x, y, text="R", fill='red')

    def get_color(self, radioactivity):
        # Map radioactivity to shades of yellow, orange, and red
        if radioactivity < 0.33:
            # Yellow to orange
            red = 0
            green = int(255 * (radioactivity / 0.33))
            blue = 0
        elif radioactivity < 0.66:
            # Orange to red
            red = 255
            green = int(255 * ((0.66 - radioactivity) / 0.33))
            blue = 0
        else:
            # Red
            red = 255
            green = 0
            blue = 0

        return "#{:02x}{:02x}{:02x}".format(red, green, blue)

if __name__=="__main__":
    root = tk.Tk()
    root.geometry("400x300")
    grid = HazardGrid(root, 15, 15, 15)
    grid.draw([(1, 1), (2, 2)], [(3, 3), (4, 4)])
    root.mainloop()



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