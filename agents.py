from mesa import Agent
import random
import numpy as np
from mesa_com.communication import CommunicatingAgent, MessagePerformative, Message

##########################
###### Robot Agents ######
##########################

class Robot(Agent):
    """
    Carry is a variable that counts the number of wastes carried by the robot (0, 1 or 2)
    Go_east is a boolean that indicates if the robot should go east, its value is True when the robots reaches maximum carrying capacity
    Made_action is a boolean that indicates if the robot has already made an action in the current step
    """

    def __init__(self, unique_id, model, pos):
        Agent.__init__(self, unique_id, model)
        self.inventory = []
        self.pos = pos
        self.border = None
        self.knowledge = {}
        self.percepts = {}
        self.model = model
    
    def update_knowledge(self):
        for k,v in self.percepts.items():
            self.knowledge[k] = v

    def get_new_pos(self, go_east = False):
        if go_east:
            return self.pos[0] + 1, self.pos[1]
        else:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
            possible_steps = [pos for pos in possible_steps if pos[0] <= self.border] # Cannot go further east
            return random.choice(possible_steps)
    
    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge
        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": "move", "pos": pos, "objective": "idle"}
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}"}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if knowledge["pos"][0] < knowledge["border"]:
                action = "move"
                pos = (knowledge["pos"][0] + 1, knowledge["pos"][1])
                return {"action": action, "pos": pos, "objective": "go to the border of the zone"}
            else:
                action = "drop"
                return {"action": action}
    
    def step(self):
        self.update_knowledge()
        decision = self.deliberate(self.knowledge)
        self.percepts = self.model.do(self, **decision)

class GreenRobot(Robot):
    """
    Green Robot:
        ○ walk to pick up 2 initial wastes (i.e. green),
        ○ if possession of 2 green wastes transport them further east,
        ○ if possession of 2 green wastes and at the border of green zone, unload a yellow waste,
        ○ green robot cannot exceed zone z1.
    """

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos=pos)
        self.border = self.model.grid_len//3 -1# frontière de la zone verte
        self.type = "green"

        self.knowledge = {
            "wastes": self.model.grid.get_wastes(),
            "robots": self.model.grid.get_robots(),
            "inventory": [],
            "pos": self.pos,
            "color": self.type,
            "border": self.border,
            "radioactivity": self.model.grid.radioactivity_map,
            "radioactivity_limit": 1/3
        }
        self.percepts = self.knowledge


class CommunicatingGreenRobot(GreenRobot, CommunicatingAgent):
    def __init__(self, unique_id, model, pos):
        GreenRobot.__init__(self, unique_id, model, pos)
        CommunicatingAgent.__init__(self, unique_id, model, f"GreenRobot{unique_id}")

    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge

        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.INFORM_REF:
                content = message.get_content()
                if content in knowledge["wastes"]["green"]:
                    knowledge["wastes"]["green"].remove(content)

        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": "move", "pos": pos, "objective": "idle"}
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                for r in knowledge["robots"]["green"]:
                    self.send_message(Message(self.unique_id, r.unique_id, MessagePerformative.INFORM_REF, closest_waste))
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}", "target": closest_waste}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if knowledge["pos"][0] < knowledge["border"]:
                action = "move"
                pos = (knowledge["pos"][0] + 1, knowledge["pos"][1])
                return {"action": action, "pos": pos, "objective": "go to the border of the zone", "target": None}
            else:
                action = "drop"
                return {"action": action}
    
    def step(self):
        self.update_knowledge()
        decision = self.deliberate(self.knowledge)
        self.percepts = self.model.do(self, **decision)

class YellowRobot(Robot):
    """
    Yellow Robot:
        ○ walk to pick up 2 initial yellow wastes,
        ○ if possession of 2 yellow wastes then transformation into 1 red waste,
        ○ if possession of 1 red waste, transport it further east,
        ○ yellow robot can move in zones z1 and z2.
    """

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos=pos)
        self.border = self.model.grid_len//self.model.grid.n_zones*2 -1 # frontière de la zone jaune
        self.type = "yellow"

        self.knowledge = {
            "wastes": self.model.grid.get_wastes(),
            "robots": self.model.grid.get_robots(),
            "inventory": [],
            "pos": self.pos,
            "color": self.type,
            "border": self.border,
            "radioactivity": self.model.grid.radioactivity_map,
            "radioactivity_limit": 2/3
        }
        self.percepts = self.knowledge

class CommunicatingYellowRobot(YellowRobot, CommunicatingAgent):
    def __init__(self, unique_id, model, pos):
        YellowRobot.__init__(self, unique_id, model, pos)
        CommunicatingAgent.__init__(self, unique_id, model, f"YellowRobot{unique_id}")

    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge

        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.INFORM_REF:
                content = message.get_content()
                if content in knowledge["wastes"]["yellow"]:
                    knowledge["wastes"]["yelow"].remove(content)

        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": "move", "pos": pos, "objective": "idle"}
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                for r in knowledge["robots"]["green"]:
                    self.send_message(Message(self.unique_id, r.unique_id, MessagePerformative.INFORM_REF, closest_waste))
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}", "target": closest_waste}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if knowledge["pos"][0] < knowledge["border"]:
                action = "move"
                pos = (knowledge["pos"][0] + 1, knowledge["pos"][1])
                return {"action": action, "pos": pos, "objective": "go to the border of the zone", "target": None}
            else:
                action = "drop"
                return {"action": action}

class RedRobot(Robot):
    """
    Red Robot:
        ○ walk to pick up 1 red waste,
        ○ if possession of 1 red waste then transport it further east on the “waste
        disposal zone”, the waste is then “put away”,
        ○ red robot can move in zones z1, z2 andz3.    
    """
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos=pos)
        # disposal_zone is where the grid's radioactivity is the highest
        self.disposal_zone = self.model.grid_len - 1, np.argmax(self.model.grid.radioactivity_map[:,-1])
        self.type = "red"
        self.border = self.model.grid_len - 1 # frontière de la zone rouge

        self.knowledge = {
            "wastes": self.model.grid.get_wastes(),
            "robots": self.model.grid.get_robots(),
            "inventory": [],
            "pos": self.pos,
            "color": self.type,
            "disposal_zone": self.disposal_zone
        }
        self.percepts = self.knowledge

    def deliberate(self, knowledge=None):
        if knowledge is None:
            knowledge = self.knowledge
        # red robots pick up red wastes and goest to put them in disposal zone
        if len(self.inventory) < 1:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": "move", "pos": pos, "objective": "idle"}
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}"}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        else:
            if knowledge["pos"] != knowledge["disposal_zone"]:
                action = "move"
                # move one cell towards the disposal zone
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = min(pos, key=lambda p: self.model.grid.get_distance(p, knowledge["disposal_zone"])) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "go to the disposal zone"}
            else:
                action = "drop"
                return {"action": action, "waste": self.inventory[0]}

class RandomGreenRobot(GreenRobot):
    # Has a very limited knowledge of the environment
    # Chooses randomly where to move
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge
        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0:
                action = "move"
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "idle"}
            else:
                closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
                if closest_waste.pos == knowledge["pos"]:
                    action = "pick_up"
                    return {"action": action, "waste": closest_waste}
                else:
                    action = "move"
                    pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                    pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                    pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                    pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                    pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                    pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                    return {"action": "move", "pos": pos, "objective": "idle"}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if self.pos[0] == self.border:
                action = "drop"
                return {"action": action}
            
            else:
                action = "move"
                new_pos = (knowledge["pos"][0] + 1, knowledge["pos"][1])
                return {"action": action, "pos": new_pos, "objective": "go to the border of the zone"}
    
    def step(self):
        self.update_knowledge()
        decision = self.deliberate(self.knowledge)
        self.percepts = self.model.do(self, **decision)

class RandomYellowRobot(YellowRobot):
    # Has a very limited knowledge of the environment
    # Chooses randomly where to move
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge
        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0:
                action = "move"
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "idle"}
            else:
                closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
                if closest_waste.pos == knowledge["pos"]:
                    action = "pick_up"
                    return {"action": action, "waste": closest_waste}
                else:
                    action = "move"
                    pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                    pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
                    pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                    pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                    pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                    pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                    return {"action": action, "pos": pos, "objective": "idle"}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if self.pos[0] == self.border:
                action = "drop"
                return {"action": action}
            
            else:
                action = "move"
                new_pos = (knowledge["pos"][0] + 1, knowledge["pos"][1])
                return {"action": action, "pos": new_pos, "objective": "go to the border of the zone"}
    
    def step(self):
        self.update_knowledge()
        decision = self.deliberate(self.knowledge)
        self.percepts = self.model.do(self, **decision)


class RandomRedRobot(RedRobot):
    """
    Red Robot:
        ○ walk to pick up 1 red waste,
        ○ if possession of 1 red waste then transport it further east on the “waste
        disposal zone”, the waste is then “put away”,
        ○ red robot can move in zones z1, z2 andz3.    
    """
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def deliberate(self, knowledge=None):
        if knowledge is None:
            knowledge = self.knowledge
        # red robots pick up red wastes and goest to put them in disposal zone
        if len(self.inventory) < 1:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0:
                action = "move"
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "idle"}
            else:
                closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
                if closest_waste.pos == knowledge["pos"]:
                    action = "pick_up"
                    return {"action": action, "waste": closest_waste}
                else:
                    action = "move"
                    new_pos = self.get_new_pos(go_east=False) # Randomly choose where to move
                    return {"action": action, "pos": new_pos}
        else:
            if knowledge["pos"] != knowledge["disposal_zone"]:
                action = "move"
                # move one cell towards the disposal zone
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = min(pos, key=lambda p: self.model.grid.get_distance(p, knowledge["disposal_zone"])) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "go to the disposal zone"}
            else:
                action = "drop"
                return {"action": action, "waste": self.inventory[0]}
        

class CommunicatingRedRobot(RedRobot, CommunicatingAgent):
    def __init__(self, unique_id, model, pos):
        RedRobot.__init__(self, unique_id, model, pos)
        CommunicatingAgent.__init__(self, unique_id, model, f"RedRobot{unique_id}")
    
    def deliberate(self, knowledge=None):
        if knowledge is None:
            knowledge = self.knowledge

        # remove all wastes that were broadcasted
        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.INFORM_REF:
                waste = message.get_content()
                if waste in knowledge["wastes"]["red"]:
                    knowledge["wastes"]["red"].remove(waste)
        
        # red robots pick up red wastes and goest to put them in disposal zone
        if len(self.inventory) < 1:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": "move", "pos": pos, "objective": "idle", "target": None}
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                    all_closest_pos = [p for p in all_closest_pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}", "target": closest_waste}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        else:
            if knowledge["pos"] != knowledge["disposal_zone"]:
                action = "move"
                # move one cell towards the disposal zone
                pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
                pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
                pos = min(pos, key=lambda p: self.model.grid.get_distance(p, knowledge["disposal_zone"])) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "go to the disposal zone", "target": "disposal"}
            else:
                action = "drop"
                return {"action": action, "waste": self.inventory[0]}