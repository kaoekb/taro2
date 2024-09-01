from openai import OpenAI
import os
from settings import prompt_1, prompt_2, prompt_3, prompt_final


def prediction(layout: list[dict], question: str) -> None:
    """
        This function adds prediction from chatGPT into 'prediction' "layout" dict element for each card

    """

    messages = []

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", None))

    for num, card in enumerate(layout):
        match num:
            case 0:
                prompt = prompt_1.replace("$CARD", card['name']).replace("$ASK", question)
                card['prediction'] = openai_handler(client=client, messages=messages, prompt=prompt)

            case 1:
                prompt = prompt_2.replace("$CARD", card['name'])
                card['prediction'] = openai_handler(client=client, messages=messages, prompt=prompt)

            case 2:
                prompt = prompt_3.replace("$CARD", card['name'])
                card['prediction'] = openai_handler(client=client, messages=messages, prompt=prompt)

    layout[0]['final_prediction'] = openai_handler(client=client, messages=messages, prompt=prompt_final)


def openai_handler(client: OpenAI, messages: list[dict], prompt: str) -> str:
    """
        Request to ChatGPT

    """

    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(model=os.getenv("OPENAPI_MODEL"),
                                                messages=messages)
    chat_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": chat_response})

    return chat_response
