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

app = Flask(__name__)

client = MongoClient(port=27017)
db=client.local

sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Welcome to the Alexa Skills Kit, you can say hello giresse!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class StoreNameRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("StoreName")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        name = slots["name"].value



        nameDoc = {
            'name': name
        }

        db.names.insert(nameDoc)

        speech_text = "Der Name wurde gespeichert."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Name gespeichert", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response



class StoreEventRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("StoreEvent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        event = slots["event"].value
        day = slots["dayofweek"].value

        todoDoc = {
            'Day': day,
            'even': event
        }
        x = db.names.col.find_one()
        print(x)
        db.names.insert(todoDoc)
        todolist = db.my_TodoList
        # Insert Data
        rec_id1 = todolist.insert_one(todoDoc)

        speech_text = "Das Event und der Tag wurden gespeichert."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Name und Event gespeichert", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class GetEventAnwserHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetEventAnwser")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots

        dayValue = slots["dayofweek"].value
        eventValue = ""

        x = db.my_TodoList.find()
        for data in x:
            if data["Day"] == dayValue:

                eventValue +=  data["even"] + ", "


                print("event in montag :" + str(eventValue))

        speech_text = "Am "+ dayValue + " hast du: " + eventValue

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Name und Event gespeichert", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response




class DeleteEventHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("DeleteEvent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots

        dayValue = slots["dayofweek"].value
        eventValue = slots["event"].value


        x = db.my_TodoList

        myquery = {"Day": dayValue, "even": eventValue }

        currentIntent =handler_input.request_envelope.request.intent
        if currentIntent.confirmationStatus == "DENIED":
            handlerInput.requestEnvelope.request.intent.tent.confirmationStatus = "NONE"
            speech_text = "ok alles klar"

        else:
            x.delete_one(myquery)
            speech_text = "das Event wurde gelöscht"




        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Event gelöscht", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response




class YesIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = ""

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(" Yes intent", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response




class NoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = ""

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(" NO intent", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response



class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Hello Python World from Classes!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "You can say hello to me!"

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """
    This handler will not be triggered except in supported locales,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The Hello World skill can't help you with that.  "
            "You can say hello!!")
        reprompt = "You can say hello!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        app.logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


x = db.my_TodoList

myquery = {"Day": "montag", "even": "DSA"}

x.delete_one(myquery)

speech_text = "das Event wurde gelöscht"
print(speech_text)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StoreNameRequestHandler())
sb.add_request_handler(StoreEventRequestHandler())
sb.add_request_handler(GetEventAnwserHandler())
sb.add_request_handler(DeleteEventHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

skill_adapter = SkillAdapter(
    skill=sb.create(), skill_id=1, app=app)


@app.route('/', methods=['GET', 'POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()


if __name__ == '__main__':
    app.run()
