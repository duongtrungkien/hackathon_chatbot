# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import json
import logging
import xlrd
import re
from rasa_sdk.events import AllSlotsReset
from xlutils.copy import copy

logger = logging.getLogger(__name__)


class ValidateNewSupplierForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_new_supplier_form"

    def validate_2_y_tunnus(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if re.match("\d{7}-\d", slot_value):
            return {"2_y_tunnus": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen yritystunnus. Kirjoita uudelleen")
            return {"2_y_tunnus": None}

    @staticmethod
    def check_number_input(input):
        correct = True
        try:
            int(input)
        except ValueError:
            correct = False
        return correct

    def validate_a_millä_euromäärällä_ollaan_tilaamassa(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if self.check_number_input(slot_value):
            return {"a_millä_euromäärällä_ollaan_tilaamassa": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Kirjoita uudelleen")
            return {"a_millä_euromäärällä_ollaan_tilaamassa": None}


class ValidateExamForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_exam_form"

    def validate_1_milloin_aamustartti_alkaa(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        if slot_value in ["a", "b", "c", "A", "B", "C"]:
            return {"1_milloin_aamustartti_alkaa": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A, B tai C")
            return {"1_milloin_aamustartti_alkaa": None}

    def validate_2_kuka_vetää_aamustartin(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in ["a", "b", "c", "A", "B", "C"]:
            return {"1_milloin_aamustartti_alkaa": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A, B tai C")
            return {"1_milloin_aamustartti_alkaa": None}

    def validate_3_Mille_Neptonin_taskille(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in ["a", "b", "c", "A", "B", "C"]:
            return {"1_milloin_aamustartti_alkaa": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A, B tai C")
            return {"1_milloin_aamustartti_alkaa": None}

    def validate_4_Saako_lounaalle(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in ["a", "b", "A", "B"]:
            return {"1_milloin_aamustartti_alkaa": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A tai B")
            return {"1_milloin_aamustartti_alkaa": None}

    def validate_5_Saako_saapuneet_kansioon(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in ["a", "b", "A", "B"]:
            return {"1_milloin_aamustartti_alkaa": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A tai B")
            return {"1_milloin_aamustartti_alkaa": None}


class ActionSubmitExamForm(Action):
    def name(self) -> Text:
        return "action_submit_exam_form"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        point = 0
        q1 = tracker.get_slot('1_milloin_aamustartti_alkaa')
        if q1.lower() == "b":
            point = point + 1
        q2 = tracker.get_slot('2_kuka_vetää_aamustartin')
        if q2.lower() == "a":
            point = point + 1
        q3 = tracker.get_slot('3_Mille_Neptonin_taskille')
        if q3.lower() == "c":
            point = point + 1
        q4 = tracker.get_slot('4_Saako_lounaalle')
        if q4.lower() == "b":
            point = point + 1
        q5 = tracker.get_slot('5_Saako_saapuneet_kansioon')
        if q5.lower() == "a":
            point = point + 1
        if point <= 3:
            dispatcher.utter_message(
                text="Sinulla on {}/5. Et läpäissyt testiä. Lue asiakirja uudelleen".format(point))
        if point > 3:
            dispatcher.utter_message(
                text="Onnittelut! Sinulla on {}/5. Olet läpäissyt testin.".format(point))
        return_events = [SlotSet("1_milloin_aamustartti_alkaa", None), SlotSet("2_kuka_vetää_aamustartin", None), SlotSet(
            "3_Mille_Neptonin_taskille", None), SlotSet("4_Saako_lounaalle", None), SlotSet("5_Saako_saapuneet_kansioon", None)]
        return return_events


class ActionSubmitNewSupplierForm(Action):
    def name(self) -> Text:
        return "action_submit_new_supplier_form"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        yrityksen_nimi = tracker.get_slot('1_yrityksen_nimi')
        y_tunnus = tracker.get_slot('2_y_tunnus')
        mitä_tavaraa_tai_palvelua_tilataan = tracker.get_slot(
            '9_mitä_tavaraa_tai_palvelua_tilataan')
        millä_euromäärällä_ollaan_tilaamassa = tracker.get_slot(
            'a_millä_euromäärällä_ollaan_tilaamassa')
        read_book = xlrd.open_workbook(
            "/Users/kien1/Documents/Projects/hackathon_demo/instructions/Yleiset_ohjeet/Toimittajatiedot/Toimittajan_perustietolomake_2020.xlsx")  # Make Readable Copy
        write_book = copy(read_book)  # Make Writeable Copy
        write_sheet_0 = write_book.get_sheet(0)
        write_sheet_0.write(7, 1, yrityksen_nimi)
        write_sheet_0.write(8, 1, y_tunnus)
        write_sheet_0.write(17, 1, mitä_tavaraa_tai_palvelua_tilataan)
        write_sheet_0.write(18, 1, millä_euromäärällä_ollaan_tilaamassa)
        write_book.save(
            "/Users/kien1/Documents/Projects/hackathon_demo/instructions/Toimittajan_perustietolomake_2020.xls")
        dispatcher.utter_message(
            text="Lomake on tallennettu. [Lataa tästä napsauttamalla tätä](https://8f31d4c87743.ngrok.io/Toimittajan_perustietolomake_2020.xls)")
        message = "Haluatko tallentaa tämän lomakkeen?"
        buttons = [{'title': 'Joo',
                    'payload': '/save_new_supplier_form'},
                   {'title': 'Ey',
                    'payload': '/delete_new_supplier_form'}]
        dispatcher.utter_button_message(text=message, buttons=buttons)
        return []


class ActionDeleteNewSupplierForm(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self):
        return "action_delete_new_supplier_form"

    def run(self, dispatcher, tracker, domain):

        message = "Kiitos. Puhdistan lomakkeen sinulle. Haluatko täyttää lomakkeen uudelleen?"
        buttons = [{'title': 'Joo',
                    'payload': '/activate_new_supplier_form'},
                   {'title': 'Ey',
                    'payload': '/deny'}]
        dispatcher.utter_button_message(text=message, buttons=buttons)
        return [AllSlotsReset()]


class ActionDefaultAskAffirmation(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self):
        return "action_default_ask_affirmation"

    def __init__(self):
        self.intent_mappings = {}
        # read the mapping from a csv and store it in a dictionary
        with open('intent_mapping.json') as file:
            data = json.load(file)
            self.intent_mappings = data

    def run(self, dispatcher, tracker, domain):
        predicted_intent_info = tracker.latest_message["intent_ranking"][1]
        # get the most likely intent name
        intent_name = predicted_intent_info["name"]
        # get the prompt for the intent
        intent_prompt = self.intent_mappings[intent_name]

        # Create the affirmation message and add two buttons to it.
        # Use '/<intent_name>' as payload to directly trigger '<intent_name>'
        # when the button is clicked.
        message = "Tarkoititko '{}'?".format(intent_prompt)
        buttons = [{'title': 'Joo',
                    'payload': '/{}'.format(intent_name)},
                   {'title': 'Ey',
                    'payload': '/out_of_scope'}]
        dispatcher.utter_button_message(text=message, buttons=buttons)

        return []
