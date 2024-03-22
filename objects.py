from mesa.space import MultiGrid
from mesa.agent import Agent
import matplotlib.pyplot as plt
import numpy as np

##################
###### Grid ######
##################

class HazardGrid(MultiGrid):
    def __init__(self, width, height, n_zones=3):
        super().__init__(width+1, height, False)
        self.n_zones = n_zones
        self.zone_width = width // n_zones
        self.radioactivity_map = np.ones((height, width+1))
        # last column is the general waste disposal zone

        for i in range(n_zones):
            # for each zone, assign a random radioactivity level (between 0.0 and 0.33 for zone 1, 0.33 and 0.66 for zone 2, 0.66 and 1.0 for zone 3)
            random_values = np.random.uniform(i / n_zones, (i + 1) / n_zones, (self.height, self.zone_width))
            self.radioactivity_map[:, i*self.zone_width:(i+1)*self.zone_width] = random_values

    
    def print(self, wastes_pos, robots_pos):
        """
        Plot the grid with wastes and robots
        """
        fig, ax = plt.subplots()
        ax.imshow(self.radioactivity_map, cmap='winter', interpolation='nearest')
        for waste in wastes_pos:
            # adds a "W" to the waste position
            ax.text(waste[0], waste[1], "W", color='green', fontsize=12)
        for robot in robots_pos:
            # adds a "R" to the robot position
            ax.text(robot[0], robot[1], "R", color='red', fontsize=12)
        plt.show()

if __name__=="__main__":
    grid = HazardGrid(15, 5, 1)
    grid.print([(1, 1), (2, 2)], [(3, 3), (4, 4)])


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