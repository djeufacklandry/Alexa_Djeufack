from flask import Flask
from pymongo import MongoClient
from ask_sdk_core.skill_builder import SkillBuilder
from flask_ask_sdk.skill_adapter import SkillAdapter
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from ask_sdk_core.attributes_manager import AbstractPersistenceAdapter
import ask_sdk_core.utils as ask_utils
import datetime
#from ask_sdk_model.dialog import ElicitSlotDirective
#from ask_sdk_model import Intent

app = Flask(__name__)

client = MongoClient(port=27017)
db = client.local

sb = SkillBuilder()


class LaunchRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attributes = handler_input.attributes_manager.session_attributes

        entry = db.eintraege.find_one()

       ## if entry is not None:
       #     session_attributes["prevIntent"] = "Return"
       #     speech_text = "Willkommen zurück, was möchtest du heute tun? Für eine Übersicht der Sprachbefehle sage 'Befehle anzeigen'."

       #     handler_input.response_builder.speak(speech_text).ask("Für eine Übersicht der Sprachbefehle sage 'Befehle anzeigen'.")
      #  else:
        session_attributes["prevIntent"] = "Launch"
        speech_text = "Willkommen bei Just Do It! Dieser Skill dient zum Verwalten eines Kalenders sowie zum Erstellen" \
                      " von Erinnerungen. Möchtest du deinen ersten Kalendereintrag anlegen?"

        handler_input.response_builder.speak(speech_text).ask("Möchtest du deinen ersten Kalendereintrag anlegen?")
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("Help")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speech_text = "Mögliche Sprachbefehle sind 'Eintrag erstellen', um einen " \
                      "neuen Kalendereintrag zu machen, 'Eintrag löschen', um " \
                      "vorhandene Kalendereinträge zu löschen, 'Eintrag ändern', " \
                      "um einen Eintrag zu ändern und 'Termine anzeigen', um eine" \
                      " aktuelle Übersicht der 5 nächsten Termine im Kalender zu " \
                      "bekommen."

        session_attriutes = handler_input.attributes_manager.session_attributes

        session_attriutes["prevIntent"] = "Help"

        handler_input.response_builder.speak(speech_text).ask("Um die Befehle noch einmal zu hören, sage 'Befehle anzeigen'.")
        return handler_input.response_builder.response


class CreateEntryIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CreateEntry")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speech_text = "Wie möchtest du diesen Kalendereintrag benennen? Sage 'Nenne ihn'"

        session_attriutes = handler_input.attributes_manager.session_attributes

        session_attriutes["prevIntent"] = "CreateEntry"

        handler_input.response_builder.speak(speech_text).ask("Sage 'Nenne ihn'.")
        return handler_input.response_builder.response


class DeleteEntryIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("DeleteEntry")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speech_text = "Um welchen Eintrag handelt es sich, den du löschen möchtest? Sage 'Lösche'"

        session_attriutes = handler_input.attributes_manager.session_attributes

        session_attriutes["prevIntent"] = "DeleteEntry"

        handler_input.response_builder.speak(speech_text).ask("Sage 'Lösche'.")
        return handler_input.response_builder.response


class CheckEntryIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CheckEntry")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots

        name = slots["eventname"].value
        eintrag = db.eintraege.find_one({"name": name})
        datum = eintrag["date"]

        speech_text = " Der Termin " + name + " ist am " + datum + ". Was möchtest du als Nächstes tun?"

        session_attriutes = handler_input.attributes_manager.session_attributes

        session_attriutes["prevIntent"] = "Idle"

        handler_input.response_builder.speak(speech_text).ask("Was möchtest du als Nächstes tun?")
        return handler_input.response_builder.response


class ShowEntryIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ShowEntry")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speech_text = "Die nächsten 5 Termine sind: "

        eintraege = list(db.eintraege.find({}))
        naechste_eintraege = [("Eintrag 1", datetime.datetime(9999, 1, 1)),
                              ("Eintrag 2", datetime.datetime(9999, 1, 1)),
                              ("Eintrag 3", datetime.datetime(9999, 1, 1)),
                              ("Eintrag 4", datetime.datetime(9999, 1, 1)),
                              ("Eintrag 5", datetime.datetime(9999, 1, 1))]


        for eintrag in eintraege:
            if datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d") < naechste_eintraege[0][1]:
                # paste and move up
                naechste_eintraege[1] = naechste_eintraege[0]
                naechste_eintraege[2] = naechste_eintraege[1]
                naechste_eintraege[3] = naechste_eintraege[2]
                naechste_eintraege[4] = naechste_eintraege[3]

                new_pair = (eintrag["name"], datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d"))
                naechste_eintraege[0] = new_pair
                continue
            if datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d") < naechste_eintraege[1][1]:
                # paste and move up
                naechste_eintraege[2] = naechste_eintraege[1]
                naechste_eintraege[3] = naechste_eintraege[2]
                naechste_eintraege[4] = naechste_eintraege[3]

                new_pair = (eintrag["name"], datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d"))
                naechste_eintraege[1] = new_pair
                continue
            if datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d") < naechste_eintraege[2][1]:
                # paste and move up
                naechste_eintraege[3] = naechste_eintraege[2]
                naechste_eintraege[4] = naechste_eintraege[3]

                new_pair = (eintrag["name"], datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d"))
                naechste_eintraege[2] = new_pair
                continue
            if datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d") < naechste_eintraege[3][1]:
                # paste and move up
                naechste_eintraege[4] = naechste_eintraege[3]

                new_pair = (eintrag["name"], datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d"))
                naechste_eintraege[3] = new_pair
                continue
            if datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d") < naechste_eintraege[4][1]:
                # paste
                new_pair = (eintrag["name"], datetime.datetime.strptime(eintrag["date"], "%Y-%m-%d"))
                naechste_eintraege[4] = new_pair
                continue

        for pair in naechste_eintraege:
            speech_text = speech_text + pair[0] + " am " + pair[1].strftime("%d-%m-%Y") + ", "

        session_attriutes = handler_input.attributes_manager.session_attributes

        session_attriutes["prevIntent"] = "ShowEntry"

        handler_input.response_builder.speak(speech_text).ask("Wie kann ich dir sonst noch helfen?")
        return handler_input.response_builder.response



class ChangeEntryIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ChangeEntry")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speech_text = "Welchen Termin möchtest du ändern? Sage 'Ändere'"

        session_attriutes = handler_input.attributes_manager.session_attributes

        session_attriutes["prevIntent"] = "ChangeEntry"

        handler_input.response_builder.speak(speech_text).ask("Welchen Termin möchtest du ändern?")
        return handler_input.response_builder.response


class ChangeValueIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ChangeValue")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attributes = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        name = session_attributes["EntryToChange"]

        if slots["Change"].value == "name":
            # -> EntryName
            speech_text = "In was möchtest du " + name + " umbenennen?"

            handler_input.response_builder.speak(speech_text).ask("In was möchtest du " + name + " umbenennen?")
        elif slots["Change"].value == "datum":
            # -> EntryTime
            speech_text = "An welchem Tag soll " + name + " jetzt stattfinden?"

            handler_input.response_builder.speak(speech_text).ask("An welchem Tag soll " + name + " jetzt stattfinden?")
        elif slots["Change"].value == "uhrzeit":
            # -> EntryTime
            speech_text = "Zu welcher Uhrzeit soll " + name + " jetzt stattfinden?"

            handler_input.response_builder.speak(speech_text).ask("Zu welcher Uhrzeit soll " + name + " jetzt stattfinden?")
        elif slots["Change"].value == "wiederholung":
            # -> Repeat
            speech_text = "Soll das Wiederholungsverhalten von " + name + " geändert werden?"

            handler_input.response_builder.speak(speech_text).ask("Soll das Wiederholverhalten von " + name + " geändert werden?")

        session_attributes["prevIntent"] = "EntryToChange"
        return handler_input.response_builder.response

class YesIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attriutes = handler_input.attributes_manager.session_attributes
        if session_attriutes["prevIntent"] == "Launch":
            speech_text = "Wie möchtest du diesen Kalendereintrag benennen? Sage 'Nenne ihn'"

            handler_input.response_builder.speak(speech_text).ask("Sage 'Nenne ihn'")
            session_attriutes["prevIntent"] = "Yes"
        elif session_attriutes["prevIntent"] == "EntryTime":
            speech_text = "Soll dieses Ereignis täglich, wöchentlich, monatlich oder jährlich wiederholt werden?"

            handler_input.response_builder.speak(speech_text).ask("Soll dieses Ereignis täglich, wöchentlich, monatlich oder jährlich wiederholt werden?")
        elif session_attriutes["prevIntent"] == "Repeat":
            speech_text = "Nenne mir ein bestimmtes Datum, wann ich das Ereignis beenden soll."
            session_attriutes["prevIntent"] = "RepeatYes"

            handler_input.response_builder.speak(speech_text).ask("Nenne mir ein bestimmtes Datum, wann ich das Ereignis beenden soll.")
        elif session_attriutes["prevIntent"] == "DeleteRepeat":
            name = session_attriutes["toDelete"]
            delete_result = db.eintraege.delete_one({"name": name})
            if delete_result:
                speech_text = "Eintrag " + name + " wurde gelöscht. Kann ich dir sonst noch behilflich sein?"
            else:
                speech_text = "Eintrag " + name + " konnte nicht gelöscht werden. Kann ich dir sonst noch behilflich sein?"

            handler_input.response_builder.speak(speech_text).ask("Kann ich dir sonst noch behilflich sein?")

        return handler_input.response_builder.response


class NoIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attriutes = handler_input.attributes_manager.session_attributes
        if session_attriutes["prevIntent"] == "Launch":
            speech_text = "Okay! Um einen Kalendereintrag zu erstellen sage 'Eintrag erstellen'." \
                          " Möchtest du weitere Optionen dieses Skills hören?."

            handler_input.response_builder.speak(speech_text).ask("Möchtest du weitere Optionen dieses Skills hören?")
            session_attriutes["prevIntent"] = "No"
        elif session_attriutes["prevIntent"] == "No" or session_attriutes["prevIntent"] == "SaveEntry":
            speech_text = "Bis zum nächsten Mal."
            # TODO
            session_attriutes["prevIntent"] = "No"
        elif session_attriutes["prevIntent"] == "EntryTime" or session_attriutes["prevIntent"] == "Repeat":
            speech_text = "Das Ereignis " + session_attriutes["name"] + " wurde erstellt. Möchtest du noch etwas tun?"
            if session_attriutes["prevIntent"] == "Repeat":
                session_attriutes["repeat"] = True
            else:
                session_attriutes["repeat"] = False
            session_attriutes["repeatTime"] = False

            ### save entry
            slots = handler_input.request_envelope.request.intent.slots
            name = session_attriutes["name"]
            if "date" in session_attriutes:
                date = session_attriutes["date"]
            else:
                date = datetime.date.today().strftime("%Y-%m-%d")
            if "time" in session_attriutes:
                time = session_attriutes["time"]
            else:
                time = "00:00:00"
            repeat = session_attriutes["repeat"]
            repeatTime = session_attriutes["repeatTime"]
            entryDoc = {
                'name': name,
                'date': date,
                'time': time,
                'repeat': repeat,
                'repeatTime': repeatTime
            }
            # clear session entry
            session_attriutes["name"] = False
            session_attriutes["date"] = False
            session_attriutes["time"] = False
            session_attriutes["repeat"] = False
            session_attriutes["repeatTime"] = False

            db.eintraege.insert(entryDoc)
            ###

            handler_input.response_builder.speak(speech_text).ask("Möchtest du noch etwas tun?")
            session_attriutes["prevIntent"] = "SaveEntry"

        elif session_attriutes["prevIntent"] == "DeleteRepeat":
            speech_text = "An welchem Datum möchtest du dieses Ereignis aus dem Kalender löschen?"

            session_attriutes["prevIntent"] = "DeleteRepeat"

            handler_input.response_builder.speak(speech_text).ask("An welchem Datum möchtest du dieses Ereignis aus dem Kalender löschen?")

        return handler_input.response_builder.response


class EntryNameIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("EntryName")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        session_attributes = handler_input.attributes_manager.session_attributes
        if session_attributes.get("prevIntent") is None:
            print("session_atttributes is None")
            return
        elif session_attributes["prevIntent"] == "Yes" or session_attributes["prevIntent"] == "CreateEntry":
            speech_text = "Wann soll das Ereignis stattfinden?"
            session_attributes["name"] = slots["eventname"].value

            session_attributes["prevIntent"] = "EntryName"

            handler_input.response_builder.speak(speech_text).ask("Wann soll das Ereignis stattfinden?")
        elif session_attributes["prevIntent"] == "DeleteEntry":
            name = slots["eventname"].value

            eintrag = db.eintraege.find_one({'name': name})
            if eintrag is not None:
                if eintrag["repeat"] is True:
                    speech_text = "Dies ist ein wiederholendes Ereignis. Möchtest" \
                                  "du dieses komplett aus dem Kalender löschen?"
                    session_attributes["prevIntent"] = "DeleteRepeat"
                    session_attributes["toDelete"] = name

                    handler_input.response_builder.speak(speech_text).ask("Möchtest du dieses komplett löschen?")
                else:
                    session_attributes["prevIntent"] = "DeleteEntry"
                    delete_result = db.eintraege.delete_one({"name": name})
                    if delete_result:
                        speech_text = "Ereignis " + name + " wurde gelöscht. Kann ich sonst noch etwas für dich tun?"

                    else:
                        speech_text = "Ereignis " + name + " konnte nicht gelöscht werden. "


                    handler_input.response_builder.speak(speech_text).ask("Kann ich sonst noch etwas für dich tun?")
            else:
                speech_text = "Diesen Eintrag gibt es nicht."
                session_attributes["prevIntent"] = "EntryName"

                handler_input.response_builder.speak(speech_text).ask("Kann ich sonst noch etwas für dich tun?")

        elif session_attributes["prevIntent"] == "EntryToChange":
            name = session_attributes["EntryToChange"]
            new_name = slots["eventname"].value
            change_result = db.eintraege.update_one({"name": name}, {"$set": {"name": new_name}})
            if change_result:
                speech_text = "Ereignis " + name + " wurde in " + new_name + " umbenannt. Möchtest du noch etwas tun?"
            else:
                speech_text = "Ereignis " + name + " konnte nicht geändert werden."

            handler_input.response_builder.speak(speech_text).ask("Kann ich noch etwas für dich tun?")
            session_attributes["prevIntent"] = "EntryChanged"
        elif session_attributes["prevIntent"] == "ChangeEntry":
            speech_text = "Was möchtest du ändern?"
            session_attributes["EntryToChange"] = slots["eventname"].value

            session_attributes["prevIntent"] = "EntryToChange"
            handler_input.response_builder.speak(speech_text).ask("Was möchtest du ändern?")

        return handler_input.response_builder.response


class EntryTimeIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("EntryTime")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attriutes = handler_input.attributes_manager.session_attributes

        if session_attriutes["prevIntent"] == "RepeatYes":
            slots = handler_input.request_envelope.request.intent.slots
            speech_text = "Das Ereignis " + session_attriutes["name"] + " wurde erstellt. Möchtest du noch etwas tun?"
            session_attriutes["repeat"] = True
            session_attriutes["endRepeatTime"] = slots["Datum"].value

            ### save entry
            name = session_attriutes["name"]
            if "date" in session_attriutes:
                date = session_attriutes["date"]
            else:
                date = datetime.date.today().strftime("%Y-%m-%d")
            if "time" in session_attriutes:
                time = session_attriutes["time"]
            else:
                time = "00:00:00"
            if "repeat" in session_attriutes:
                repeat = session_attriutes["repeat"]
            else:
                repeat = True

            if "repeatTime" in session_attriutes:
                repeat_time = session_attriutes["repeatTime"]
            else:
                repeat_time = False

            end_repeat_time = session_attriutes["endRepeatTime"]
            entryDoc = {
                'name': name,
                'date': date,
                'time': time,
                'repeat': repeat,
                'repeatTime': repeat_time,
                'endRepeatTime': end_repeat_time
            }
            # clear session entry
            session_attriutes["name"] = False
            session_attriutes["date"] = False
            session_attriutes["time"] = False
            session_attriutes["repeat"] = False
            session_attriutes["repeatTime"] = False
            session_attriutes["endRepeatTime"] = False

            db.eintraege.insert(entryDoc)
            ###

            handler_input.response_builder.speak(speech_text).ask("Möchtest du noch etwas tun?")
            session_attriutes["prevIntent"] = "SaveEntry"
        elif session_attriutes["prevIntent"] == "DeleteRepeat":
            slots = handler_input.request_envelope.request.intent.slots
            name = session_attriutes["toDelete"]
            eintrag = db.eintraege.find_one({"name": name})

            # tatsächliches Datum berechnen
            datum = eintrag["date"]
            repeat_time = session_attriutes["repeatTime"]
            date_time = datetime.datetime.strptime(datum, "%Y-%m-%d")
            new_date = "9999-0-0"
            while (date_time < eintrag["endRepeatTime"] and date_time < new_date) if eintrag["endRepeatTime"] else date_time < new_date:
                if repeat_time == "täglich":
                    repeat_time_add = "0-0-1"
                elif repeat_time == "wöchentlich":
                    repeat_time_add = "0-0-7"
                elif repeat_time == "monatlich":
                    repeat_time_add = "0-1-0"
                elif repeat_time == "jährlich":
                    repeat_time_add = "1-0-0"
                print(new_date)                          

                new_date = datum + repeat_time_add
                if new_date == date_time:
                    db.eintraege.update_one({"name": name}, {"$set": {"deleted": new_date}} )
                    break

            speech_text = "Ereignis " + name + " am " + new_date + " wurde gelöscht. "
            handler_input.response_builder.speak(speech_text).ask("Möchtest du noch etwas tun?")
        elif session_attriutes["prevIntent"] == "EntryToChange":

            slots = handler_input.request_envelope.request.intent.slots

            name = session_attriutes["EntryToChange"]
            eintrag = db.eintraege.find_one({"name": name})

            date = eintrag["date"]
            new_date = slots["Datum"].value

            change_result = db.eintraege.update_one({"name": name}, {"$set": {"date": new_date}})

            if change_result:
                speech_text = "Ereignis " + name + " wurde vom " + date + " auf den " + new_date + " gelegt. Möchtest du noch etwas tun?"
            else:
                speech_text = "Ereignis " + name + " konnte nicht geändert werden."

            handler_input.response_builder.speak(speech_text).ask("Kann ich noch etwas für dich tun?")
        else:
            speech_text = "Soll Ereignis " + session_attriutes["name"] + " sich wiederholen?"

            # merke vorherigen intent
            session_attriutes = handler_input.attributes_manager.session_attributes
            session_attriutes["prevIntent"] = "EntryTime"

            slots = handler_input.request_envelope.request.intent.slots
            uhrzeit = slots["Uhrzeit"].value
            datum = slots["Datum"].value
            session_attriutes["Uhrzeit"] = uhrzeit
            session_attriutes["Datum"] = datum


            handler_input.response_builder.speak(speech_text).ask("Soll sich dieses Ereignis wiederholen?")

        return handler_input.response_builder.response


class RepeatIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("Repeat")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attriutes = handler_input.attributes_manager.session_attributes

        speech_text = "Okay, soll ich das wiederholende Ereignis an einem bestimmten Zeitpunkt beenden?"

        # merke vorherigen intent
        session_attriutes = handler_input.attributes_manager.session_attributes
        session_attriutes["prevIntent"] = "Repeat"

        slots = handler_input.request_envelope.request.intent.slots
        spanne = slots["Spanne"].value
        session_attriutes["repeatTime"] = spanne
        session_attriutes["repeat"] = True

        handler_input.response_builder.speak(speech_text).ask("Soll sich das Ereignis an einem bestimmten Zeitpunkt beenden?")

        return handler_input.response_builder.response


class SaveEntryIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SaveEntry")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speech_text = "Okay, das Ereignis wurde erstellt. Möchtest du noch etwas tun?"

        handler_input.response_builder.speak(speech_text).ask("Möchtest du noch etwas tun?")
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Bis zum nächsten Mal!"

        handler_input.response_builder.speak(speech_text)

        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "Der Just Do It Skill kann dir dabei leider nicht helfen. Um Befehle angezeigt zu bekommen, sage 'Befehle anzeigen'.")

        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        app.logger.error(exception, exc_info=True)

        speech = "Deine Antwort ist ungültig. Bitte starte den Skill erneut."

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(EntryNameIntentHandler())
sb.add_request_handler(EntryTimeIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(CreateEntryIntentHandler())
sb.add_request_handler(DeleteEntryIntentHandler())
sb.add_request_handler(ChangeEntryIntentHandler())
sb.add_request_handler(ChangeValueIntentHandler())
sb.add_request_handler(ShowEntryIntentHandler())
sb.add_request_handler(CheckEntryIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

skill_adapter = SkillAdapter(
    skill=sb.create(), skill_id=1, app=app)

@app.route('/', methods=['GET', 'POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()


if __name__ == '__main__':
    app.run()

