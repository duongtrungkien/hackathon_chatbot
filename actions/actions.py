# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, ConversationPaused
import json
import logging
import openpyxl
import re
import requests
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
            float(input)
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

    def validate_9_mitä_tavaraa_tai_palvelua_tilataan(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"9_mitä_tavaraa_tai_palvelua_tilataan": slot_value}


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
            return {"2_kuka_vetää_aamustartin": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A, B tai C")
            return {"2_kuka_vetää_aamustartin": None}

    def validate_3_Mille_Neptonin_taskille(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in ["a", "b", "c", "A", "B", "C"]:
            return {"3_Mille_Neptonin_taskille": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A, B tai C")
            return {"3_Mille_Neptonin_taskille": None}

    def validate_4_Saako_lounaalle(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in ["a", "b", "A", "B"]:
            return {"4_Saako_lounaalle": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A tai B")
            return {"4_Saako_lounaalle": None}

    def validate_5_Saako_saapuneet_kansioon(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in ["a", "b", "A", "B"]:
            return {"5_Saako_saapuneet_kansioon": slot_value}
        else:
            dispatcher.utter_message(
                text="Virheellinen syöte. Napsauta painiketta tai kirjoita A tai B")
            return {"5_Saako_saapuneet_kansioon": None}


class ActionSubmitExamForm(Action):
    def name(self) -> Text:
        return "action_submit_exam_form"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        point = 0
        wrongs = []
        q1 = tracker.get_slot('1_milloin_aamustartti_alkaa')
        if q1.lower() == "b":
            point = point + 1
        else:
            wrongs.append(["Milloin aamustartti alkaa?", q1])

        q2 = tracker.get_slot('2_kuka_vetää_aamustartin')
        if q2.lower() == "a":
            point = point + 1
        else:
            wrongs.append(["Kuka vetää aamustartin?", q2])

        q3 = tracker.get_slot('3_Mille_Neptonin_taskille')
        if q3.lower() == "c":
            point = point + 1
        else:
            wrongs.append(["Koska ideat käsitellään?", q3])

        q4 = tracker.get_slot('4_Saako_lounaalle')
        if q4.lower() == "b":
            point = point + 1
        else:
            wrongs.append(["Saako lounaalle mennä kysymättä kaverilta?", q4])

        q5 = tracker.get_slot('5_Saako_saapuneet_kansioon')
        if q5.lower() == "a":
            point = point + 1
        else:
            wrongs.append(
                ["Saako saapuneet kansioon jättää luettuja viestejä?", q5])

        return_events = [SlotSet("1_milloin_aamustartti_alkaa", None), SlotSet("2_kuka_vetää_aamustartin", None), SlotSet(
            "3_Mille_Neptonin_taskille", None), SlotSet("4_Saako_lounaalle", None), SlotSet("5_Saako_saapuneet_kansioon", None), SlotSet("exam_score", point)]
        if point <= 3:
            dispatcher.utter_message(
                text="Sait {}/5 pistettä. Et läpäissyt testiä. [Lue asiakirja uudelleen](https://b76834b76650.ngrok.io/Yleiset_ohjeet/Perehdytysohje/Frontin_työskentelyohje_v0.2.docx)".format(point))
        if point > 3:
            dispatcher.utter_message(
                text="Onnittelut! Sait {}/5 pistettä. Olet läpäissyt testin.".format(point))
            return_events.append(SlotSet("new_employee_exam_passed", True))
        if point < 5:
            dispatcher.utter_message(
                "Sait väärän vastauksen seuraaviin kysymyksiin:")
            for wrong in wrongs:
                dispatcher.utter_message(
                    "{}: vastauksesi oli {}".format(wrong[0], wrong[1]))
        return return_events


class ActionSubmitNewSupplierForm(Action):
    def name(self) -> Text:
        return "action_submit_new_supplier_form"

    @staticmethod
    def get_data_from_prh(y_tunnus):
        """Function to fetch data from the PRH Open data API using the company ID.

        Args:
            y_tunnus: Company ID string. Company IDs have the following format: '1234567-8'
        """
        return_company_info_dict = dict()
        response = requests.get(
            'https://avoindata.prh.fi/tr/v1/{}'.format(y_tunnus))
        if not response.ok:
            return False

        json_response = response.json()
        results_list = json_response['results']
        received_data_to_extract_dict = results_list[0]
        return_company_info_dict['name'] = received_data_to_extract_dict['name']
        # Based on initial experimentation. The relevant address is always in position 0.
        first_address_dict = received_data_to_extract_dict['addresses'][0]
        address_info_dict = {
            'street': first_address_dict['street'], 'postCode': first_address_dict['postCode'], 'city': first_address_dict['city']
        }
        return_company_info_dict['address'] = address_info_dict

        return return_company_info_dict

    @staticmethod
    def edit_task4_xlsx(input_xlsx_path,
                        output_xlsx_path,
                        company_name,
                        y_tunnus,
                        address_street,
                        address_postal_code,
                        address_city,
                        product_or_service_name,
                        euro_price):
        """Function to edit an xlsx file for the taks for of the Espoo hackathon.

        Args:
            input_xlsx_path: Path to the xlsx file to edit. Changes will not be saved to this file.
            output_xlsx_path: Path to the new xlsx file where the changes will be saved.
            company_name: Name of the company to insert. To be edited in sheet 'Taulu1':B8
            y_tunnus: Company ID to insert. To be edited in sheet 'Taulu1':B9
            product_or_service_name: Product or sevice name to insert. To be edited in sheet 'Taulu1':B18
            euro_price: Euro price to edit. To be edited in sheet 'Taulu1':B19
        """

        xlsx_file = openpyxl.load_workbook(input_xlsx_path)
        sheet_to_change = xlsx_file['Taul1']
        sheet_to_change['B8'].value = company_name
        sheet_to_change['B9'].value = y_tunnus
        sheet_to_change['B12'].value = address_street
        sheet_to_change['B13'].value = address_postal_code
        sheet_to_change['B14'].value = address_city
        sheet_to_change['B18'].value = product_or_service_name
        sheet_to_change['B19'].value = euro_price
        xlsx_file.save(output_xlsx_path)

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        y_tunnus = tracker.get_slot('2_y_tunnus')
        product_or_service_name = tracker.get_slot(
            '9_mitä_tavaraa_tai_palvelua_tilataan')
        euro_price = tracker.get_slot(
            'a_millä_euromäärällä_ollaan_tilaamassa')
        company_info = self.get_data_from_prh(y_tunnus)
        if company_info:
            self.edit_task4_xlsx(input_xlsx_path="/Users/kien1/Documents/Projects/hackathon_demo/instructions/Yleiset_ohjeet/Toimittajatiedot/Toimittajan_perustietolomake_2020.xlsx",
                                 output_xlsx_path="/Users/kien1/Documents/Projects/hackathon_demo/instructions/Toimittajan_perustietolomake_2020.xlsx",
                                 company_name=company_info["name"],
                                 y_tunnus=y_tunnus,
                                 address_street=company_info["address"]["street"],
                                 address_city=company_info["address"]["city"],
                                 address_postal_code=company_info["address"]["postCode"],
                                 product_or_service_name=product_or_service_name,
                                 euro_price=euro_price)

            dispatcher.utter_message(
                text="Lomake on tallennettu. [Lataa se itsellesi napsauttamalla tätä](https://b76834b76650.ngrok.io/Toimittajan_perustietolomake_2020.xlsx)")
            message = "Haluatko tallentaa tämän lomakkeen?"
            buttons = [{'title': 'Joo',
                        'payload': '/save_new_supplier_form'},
                       {'title': 'Ei',
                        'payload': '/delete_new_supplier_form'}]

            dispatcher.utter_button_message(text=message, buttons=buttons)
        else:
            dispatcher.utter_message(
                text="Valitettavasti emme löydä yritystäsi")
            return[AllSlotsReset()]
        return [AllSlotsReset()]


class ActionHandOff(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self):
        return "action_hand_off"

    def run(self, dispatcher, tracker, domain):

        message = "kollegani on tulossa. Voit keskustella kanssani odottaessasi"
        dispatcher.utter_message(text=message)

        return []


class ActionDeleteNewSupplierForm(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self):
        return "action_delete_new_supplier_form"

    def run(self, dispatcher, tracker, domain):

        message = "Kiitos. Tyhjennän lomakkeen. Haluatko täyttää lomakkeen uudelleen?"
        buttons = [{'title': 'Joo',
                    'payload': '/activate_new_supplier_form'},
                   {'title': 'Ei',
                    'payload': '/Thank'}]
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
                   {'title': 'Ei',
                    'payload': '/out_of_scope'}]
        dispatcher.utter_button_message(text=message, buttons=buttons)

        return []
