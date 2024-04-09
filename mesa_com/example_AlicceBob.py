#!/usr/bin/env python3

import random

from mesa_com import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService


class SpeakingAgent(CommunicatingAgent):
    """ """
    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.__v = random.randint(0, 2)

    def step(self):
        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.QUERY_REF:
                self.send_message(Message(self, message.get_exp(), MessagePerformative.INFORM_REF, self.__v))
            elif message.get_performative() == MessagePerformative.INFORM_REF:
                new_v = random.randint(0, 2)
                print("Charles changes value from " + str(self.__v) + " to " + str(new_v))
                self.__v = new_v

class AliceBobAgent(CommunicatingAgent):
    """ """
    def __init__(self, unique_id, model, name, charles):
        super().__init__(unique_id, model, name)
        self.__v = random.randint(0, 2)
        self.charles = charles

    def step(self):
        self.send_message(Message(self.get_name(), self.charles.get_name(), MessagePerformative.QUERY_REF, "Valeur de Charles"))
        messages = self.get_messages_from_exp(self.charles)
        if len(messages) > 0:
            v = messages[0].get_content()
            if self.__v != v:
                self.send_message(Message(self.get_name(), self.charles.get_name(), MessagePerformative.INFORM_REF, "Change value"))
            else:
                print(self.get_name() + " has the same value as Charles")

class SpeakingModel(Model):
    """ """
    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()



if __name__ == "__main__":
    # Init the model and the agents
    speaking_model = SpeakingModel()
    charles = SpeakingAgent(2, speaking_model, "Charles")
    alice = AliceBobAgent(0, speaking_model, "Alice", charles)
    bob = AliceBobAgent(1, speaking_model, "Bob", charles)
    
    speaking_model.schedule.add(alice)
    speaking_model.schedule.add(bob)
    speaking_model.schedule.add(charles)

    # Launch the Communication part 

    step = 0
    while step < 10:
        speaking_model.step()
        step += 1
