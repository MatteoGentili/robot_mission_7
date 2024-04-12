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

    def __init__(self, unique_id, model, pos, **kwargs):
        Agent.__init__(self, unique_id, model)
        self.inventory = []
        self.go_east = False
        self.pos = pos
        self.left_border = 0
        self.right_border = self.model.grid_len - 1
        self.knowledge = {}
        self.percepts = {}
        self.model = model
    
    def update_knowledge(self):
        for k,v in self.percepts.items():
            self.knowledge[k] = v

    def get_new_pos(self):
        if self.go_east:
            return self.pos[0] + 1, self.pos[1]
        else:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
            possible_steps = [pos for pos in possible_steps if pos[0] < self.border] # Cannot go further east
            return random.choice(possible_steps)
        
    def get_accessible_pos(self, knowledge):
        pos = self.model.grid.get_neighborhood(self.pos, moore = False, include_center = False)
        pos = [p for p in pos if knowledge["radioactivity"].T[p] <= knowledge["radioactivity_limit"]]
        pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["green"]]]
        pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["yellow"]]]
        pos = [p for p in pos if p not in [r.pos for r in knowledge["robots"]["red"]]]
        return pos
    
    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge
        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                pos = self.get_accessible_pos(knowledge)
                pos = random.choice(pos) if len(pos) > 0 else knowledge["pos"]
                return {"action": "move", "pos": pos, "objective": "idle"}
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.get_accessible_pos(knowledge)
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}"}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if knowledge["pos"][0] < knowledge["right_border"]:
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

    def __init__(self, unique_id, model, pos, **kwargs):
        super().__init__(unique_id, model, pos=pos)
        self.right_border = self.model.grid_len//self.model.grid.n_zones -1# frontière de la zone verte
        self.left_border = 0
        self.type = "green"

        self.knowledge = {
            "wastes": self.model.grid.get_wastes(),
            "robots": self.model.grid.get_robots(),
            "inventory": [],
            "pos": self.pos,
            "color": self.type,
            "right_border": self.right_border,
            "left_border": self.left_border,
            "radioactivity": self.model.grid.radioactivity_map,
            "radioactivity_limit": 1/3
        }
        self.percepts = self.knowledge


class CommunicatingGreenRobot(GreenRobot, CommunicatingAgent):
    def __init__(self, unique_id, model, pos):
        GreenRobot.__init__(self, unique_id=unique_id, model=model, pos=pos)
        CommunicatingAgent.__init__(self, unique_id=unique_id, model=model, name=f"GreenRobot{unique_id}")
        self.argued = False

    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge

        messages = self.get_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.INFORM_REF:
                content = message.get_content()
                if content in knowledge["wastes"][knowledge["color"]]:
                    knowledge["wastes"][knowledge["color"]].remove(content)
        # print(knowledge["wastes"][knowledge["color"]])
        
        for message in messages:
            if message.get_performative() == MessagePerformative.ARGUE and not self.argued:
                self.argued = True
                self.target_robot = message.get_content()
                break
    
        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                if len(self.inventory)==0:
                    pos = self.get_accessible_pos(knowledge)
                    distances = [self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) for p in pos] if len(pos) > 0 else None
                    if distances is not None:
                        all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) == min(distances)]
                        pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                    else:
                        pos = knowledge["pos"]
                    return {"action": "move", "pos": pos, "objective": "idle", "target": None}
                else:
                    if not self.argued:
                    # broadcast the fact that he has one waste, and can't find any other
                        for r in knowledge["robots"][knowledge["color"]]:
                            if r != self:
                                self.send_message(Message(self.get_name(), r.get_name(), MessagePerformative.ARGUE, self))
                        # print(f"{self.get_name()} broadcasted the fact that he has one waste, and can't find any other")
                        return {"action": "move", "pos": knowledge["pos"], "objective": "idle"}
                    else:
                        if self.model.grid.get_distance(knowledge["pos"], self.target_robot.pos) > 1:
                            # move one cell towards the target pos
                            pos = self.get_accessible_pos(knowledge)
                            distances = [self.model.grid.get_distance(p, self.target_robot.pos) for p in pos] if len(pos) > 0 else None
                            if distances is not None:
                                all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, self.target_robot.pos) == min(distances)]
                                pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                            else:
                                pos = knowledge["pos"]
                            self.send_message(Message(self.get_name(), self.target_robot.get_name(), MessagePerformative.ARGUE, self))
                            # print(f"{self.get_name()} told {self.target_robot.get_name()} that he is going to regroup with him")
                            return {"action": "move", "pos": pos, "objective": "regroup", "target": self.target_robot.pos}
                        else:
                            # take if ok
                            if len(self.target_robot.inventory) > 0:
                                return {"action": "take", "waste": self.inventory[0], "src": self.target_robot}
                            else:
                                # idle if not
                                return {"action": "move", "pos": knowledge["pos"], "objective": "idle"}

            # closest = []
            # for waste in wastes:
            #     self_distance = self.model.grid.get_distance(self.pos, waste.pos)
            #     distances = [self.model.grid.get_distance(r.pos, waste.pos) > self_distance for r in knowledge["robots"][knowledge["color"]] if r != self and len(r.inventory) < 2]
            #     if all(distances):
            #         closest.append(waste)
            # if len(closest) == 0:
            #     pos = self.get_accessible_pos(knowledge)
            #     distances = [self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) for p in pos] if len(pos) > 0 else None
            #     if distances is not None:
            #         all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) == min(distances)]
            #         pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
            #     else:
            #         pos = knowledge["pos"]
            #     return {"action": "move", "pos": pos, "objective": "idle", "target": None}
            # closest_waste = min(closest, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.get_accessible_pos(knowledge)
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                for r in knowledge["robots"][knowledge["color"]]:
                    if r != self:
                        self.send_message(Message(self.get_name(), r.get_name(), MessagePerformative.INFORM_REF, closest_waste))
                # print(f"{self.get_name()} broadcasted the fact that he is going to pick up the closest waste which is in {closest_waste.pos}") 
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}", "target": closest_waste}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if knowledge["pos"][0] < knowledge["right_border"]:
                action = "move"
                pos = (knowledge["pos"][0] + 1, knowledge["pos"][1])
                return {"action": action, "pos": pos, "objective": "go to the border of the zone", "target": None}
            else:
                action = "drop"
                return {"action": action}

class YellowRobot(Robot):
    """
    Yellow Robot:
        ○ walk to pick up 2 initial yellow wastes,
        ○ if possession of 2 yellow wastes then transformation into 1 red waste,
        ○ if possession of 1 red waste, transport it further east,
        ○ yellow robot can move in zones z1 and z2.
    """

    def __init__(self, unique_id, model, pos, **kwargs):
        super().__init__(unique_id, model, pos=pos)
        self.right_border = self.model.grid_len//self.model.grid.n_zones*2 -1 # frontière de la zone jaune
        self.left_border = self.model.grid_len//self.model.grid.n_zones
        self.type = "yellow"

        self.knowledge = {
            "wastes": self.model.grid.get_wastes(),
            "robots": self.model.grid.get_robots(),
            "inventory": [],
            "pos": self.pos,
            "color": self.type,
            "right_border": self.right_border,
            "left_border": self.left_border,
            "radioactivity": self.model.grid.radioactivity_map,
            "radioactivity_limit": 2/3
        }
        self.percepts = self.knowledge

class CommunicatingYellowRobot(YellowRobot, CommunicatingAgent):
    def __init__(self, unique_id, model, pos):
        YellowRobot.__init__(self, unique_id=unique_id, model=model, pos=pos)
        CommunicatingAgent.__init__(self, unique_id=unique_id, model=model, name=f"YellowRobot{unique_id}")
        self.argued = False

    def deliberate(self, knowledge=None): ### ONLY FOR GREEN AND YELLOW ROBOTS
        if knowledge is None:
            knowledge = self.knowledge

        messages = self.get_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.INFORM_REF:
                content = message.get_content()
                if content in knowledge["wastes"][knowledge["color"]]:
                    knowledge["wastes"][knowledge["color"]].remove(content)
        # print(knowledge["wastes"][knowledge["color"]])
        
        for message in messages:
            if message.get_performative() == MessagePerformative.ARGUE and not self.argued:
                self.argued = True
                self.target_robot = message.get_content()
                break
    
        # if not carrying 2 wastes, move towards (1 cell at a time) the closest waste of its color if not already on it
        if len(self.inventory) < 2:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                if len(self.inventory)==0:
                    pos = self.get_accessible_pos(knowledge)
                    distances = [self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) for p in pos] if len(pos) > 0 else None
                    if distances is not None:
                        all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) == min(distances)]
                        pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                    else:
                        pos = knowledge["pos"]
                    return {"action": "move", "pos": pos, "objective": "idle", "target": None}
                else:
                    if not self.argued:
                    # broadcast the fact that he has one waste, and can't find any other
                        for r in knowledge["robots"][knowledge["color"]]:
                            if r != self:
                                self.send_message(Message(self.get_name(), r.get_name(), MessagePerformative.ARGUE, self))
                        # print(f"{self.get_name()} broadcasted the fact that he has one waste, and can't find any other")
                        return {"action": "move", "pos": knowledge["pos"], "objective": "idle"}
                    else:
                        if self.model.grid.get_distance(knowledge["pos"], self.target_robot.pos) > 1:
                            # move one cell towards the target pos
                            pos = self.get_accessible_pos(knowledge)
                            distances = [self.model.grid.get_distance(p, self.target_robot.pos) for p in pos] if len(pos) > 0 else None
                            if distances is not None:
                                all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, self.target_robot.pos) == min(distances)]
                                pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                            else:
                                pos = knowledge["pos"]
                            self.send_message(Message(self.get_name(), self.target_robot.get_name(), MessagePerformative.ARGUE, self))
                            # print(f"{self.get_name()} told {self.target_robot.get_name()} that he is going to regroup with him")
                            return {"action": "move", "pos": pos, "objective": "regroup", "target": self.target_robot.pos}
                        else:
                            # take if ok
                            if len(self.target_robot.inventory) > 0:
                                return {"action": "take", "waste": self.inventory[0], "src": self.target_robot}
                            else:
                                # idle if not
                                return {"action": "move", "pos": knowledge["pos"], "objective": "idle"}

            # closest = []
            # for waste in wastes:
            #     self_distance = self.model.grid.get_distance(self.pos, waste.pos)
            #     distances = [self.model.grid.get_distance(r.pos, waste.pos) > self_distance for r in knowledge["robots"][knowledge["color"]] if r != self and len(r.inventory) < 2]
            #     if all(distances):
            #         closest.append(waste)
            # if len(closest) == 0:
            #     pos = self.get_accessible_pos(knowledge)
            #     distances = [self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) for p in pos] if len(pos) > 0 else None
            #     if distances is not None:
            #         all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) == min(distances)]
            #         pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
            #     else:
            #         pos = knowledge["pos"]
            #     return {"action": "move", "pos": pos, "objective": "idle", "target": None}
            # closest_waste = min(closest, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.get_accessible_pos(knowledge)
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                for r in knowledge["robots"][knowledge["color"]]:
                    if r != self:
                        self.send_message(Message(self.get_name(), r.get_name(), MessagePerformative.INFORM_REF, closest_waste))
                # print(f"{self.get_name()} broadcasted the fact that he is going to pick up the closest waste which is in {closest_waste.pos}") 
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}", "target": closest_waste}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        # if carrying 2 wastes, if not at the border of the zone, move east, else drop a yellow waste
        else:
            if knowledge["pos"][0] < knowledge["right_border"]:
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
    def __init__(self, unique_id, model, pos, **kwargs):
        super().__init__(unique_id, model, pos=pos)
        # disposal_zone is where the grid's radioactivity is the highest
        self.disposal_zone = self.model.grid_len - 1, np.argmax(self.model.grid.radioactivity_map[:,-1])
        self.type = "red"
        self.right_border = self.model.grid_len - 1 # frontière de la zone rouge
        self.left_border = self.model.grid_len//self.model.grid.n_zones*2

        self.knowledge = {
            "wastes": self.model.grid.get_wastes(),
            "robots": self.model.grid.get_robots(),
            "inventory": [],
            "pos": self.pos,
            "color": self.type,
            "disposal_zone": self.disposal_zone,
            "right_border": self.right_border,
            "left_border": self.left_border,
            "radioactivity": self.model.grid.radioactivity_map,
            "radioactivity_limit": 3
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
                pos = self.get_accessible_pos(knowledge)
                pos = min(pos, key=lambda p: self.model.grid.get_distance(p, knowledge["disposal_zone"])) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "go to the disposal zone"}
            else:
                action = "drop"
                return {"action": action, "waste": self.inventory[0]}

class CommunicatingRedRobot(RedRobot, CommunicatingAgent):
    def __init__(self, unique_id, model, pos):
        RedRobot.__init__(self, unique_id=unique_id, model=model, pos=pos)
        CommunicatingAgent.__init__(self, unique_id=unique_id, model=model, name=f"RedRobot{unique_id}")
    
    def deliberate(self, knowledge=None):
        if knowledge is None:
            knowledge = self.knowledge

        # remove all wastes that were broadcasted
        messages = self.get_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.INFORM_REF:
                waste = message.get_content()
                if waste in knowledge["wastes"]["red"]:
                    knowledge["wastes"]["red"].remove(waste)
        # print(knowledge["wastes"]["red"])
        
        # red robots pick up red wastes and goest to put them in disposal zone
        if len(self.inventory) < 1:
            self.action = "move"
            wastes = knowledge["wastes"][knowledge["color"]]
            if len(wastes) == 0: # No waste of its color, then idle : move to a random cell
                pos = self.get_accessible_pos(knowledge)
                distances = [self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) == min(distances)]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                return {"action": "move", "pos": pos, "objective": "idle", "target": None}

            # closest = []
            # for waste in wastes:
            #     self_distance = self.model.grid.get_distance(self.pos, waste.pos)
            #     distances = [self.model.grid.get_distance(r.pos, waste.pos) > self_distance for r in knowledge["robots"][knowledge["color"]] if r != self and len(r.inventory) < 2]
            #     if all(distances):
            #         closest.append(waste)
            # if len(closest) == 0:
            #     pos = self.get_accessible_pos(knowledge)
            #     distances = [self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) for p in pos] if len(pos) > 0 else None
            #     if distances is not None:
            #         all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, (knowledge["left_border"], knowledge["pos"][1])) == min(distances)]
            #         pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
            #     else:
            #         pos = knowledge["pos"]
            #     return {"action": "move", "pos": pos, "objective": "idle", "target": None}
            # closest_waste = min(closest, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            closest_waste = min(wastes, key=lambda w: self.model.grid.get_distance(self.pos, w.pos))
            if closest_waste.pos != knowledge["pos"]:
                action = "move"
                # move one cell towards the closest waste
                pos = self.get_accessible_pos(knowledge)
                distances = [self.model.grid.get_distance(p, closest_waste.pos) for p in pos] if len(pos) > 0 else None
                if distances is not None:
                    all_closest_pos = [p for p in pos if self.model.grid.get_distance(p, closest_waste.pos) == min(distances)]
                    pos = random.choice(all_closest_pos) if len(all_closest_pos) > 0 else knowledge["pos"]
                else:
                    pos = knowledge["pos"]
                return {"action": action, "pos": pos, "objective": f"pick up the closest waste which is in {closest_waste.pos}", "target": closest_waste}
            else:
                action = "pick_up"
                return {"action": action, "waste": closest_waste}
        else:
            if knowledge["pos"] != knowledge["disposal_zone"]:
                # print(f"{knowledge['pos']} != {knowledge['disposal_zone']}")
                action = "move"
                # move one cell towards the disposal zone
                pos = self.get_accessible_pos(knowledge)
                pos = min(pos, key=lambda p: self.model.grid.get_distance(p, knowledge["disposal_zone"])) if len(pos) > 0 else knowledge["pos"]
                return {"action": action, "pos": pos, "objective": "go to the disposal zone", "target": "disposal"}
            else:
                action = "drop"
                return {"action": action, "waste": self.inventory[0]}