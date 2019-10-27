# # This files contains your custom actions which can be used to run
# # custom Python code.
# #
# # See this guide on how to implement these action:
# # https://rasa.com/docs/rasa/core/actions/#custom-actions/
#
#
# # This is a simple example for a custom action which utters "Hello World!"
#
#from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
# import spacy

class ActionDefaultAskAffirmation(Action):
   """Asks for an affirmation of the intent if NLU threshold is not met."""

   def name(self):
       return "action_default_ask_affirmation"

   def __init__(self):
       self.intent_mappings = {}
       # read the mapping from a csv and store it in a dictionary
       file = open('intent_mapping.csv', 'r')
       for line in file:
           values = line
           values = values.strip()
           values = values.split(";")
           self.intent_mappings[values[0].replace('"','')] = values[1].replace('"','')


   def run(self, dispatcher, tracker, domain):
       # get the most likely intent
        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if len(intent_ranking) > 1:
            diff_intent_confidence = intent_ranking[0].get(
                "confidence"
            ) - intent_ranking[1].get("confidence")
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[:2]
            else:
                intent_ranking = intent_ranking[:1]
        first_intent_names = [
            intent.get("name", "")
            for intent in intent_ranking
            if intent.get("name", "") != "out_of_scope"
        ]

       # Create the affirmation message and add two buttons to it.
       # Use '/<intent_name>' as payload to directly trigger '<intent_name>'
       # when the button is clicked.
        message_title = (
            "Sorry, I'm not sure I've understood " "you correctly. Do you mean...")

        buttons = []
        for intent in first_intent_names:
            try: 
                buttons.append(
                    {
                        "title": self.intent_mappings[intent],
                        "payload": "/{}".format(intent),
                    }
                )
            except:
                print("mapping not found for "+ intent)
        if len(buttons) == 0 :
            message_title = ("Sorry, but it seems I'm unable to answer such request")
            buttons.append({"title":"Contact the Support-Team", "payload": "/giveContactSupportTeam"})
            buttons.append({"title":"Ask something else", "payload": "/whatCanIdoForYou"})
            buttons.append({"title": "Try to rephrase", "payload": "/out_of_scope"})
        else:
            buttons.append({"title": "Try to rephrase", "payload": "/out_of_scope"})
        print(tracker.latest_message)

        dispatcher.utter_button_message(message_title, buttons=buttons)

        return []


class ActionDefaultAskRephrase(Action):
   """Asks to rephrase"""

   def name(self):
       return "action_default_ask_rephrase"


   def run(self, dispatcher, tracker, domain):
       
       message = "I am sorry, could you try to rephrase your request ?"
       dispatcher.utter_message(message)
       return []

