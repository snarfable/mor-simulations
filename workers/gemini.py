# coding: utf-8

import sys
from json import load
from google import genai
from utils import GeminiOutputter

def main():
    with open("/home/rpdaly/.config/apikeys.json") as fp:
        apikeys = load(fp)
        if "apikeys" in apikeys \
            and "google" in apikeys["apikeys"] \
            and "aistudio" in apikeys["apikeys"]["google"] \
            and "key" in apikeys["apikeys"]["google"]["aistudio"][0]:
            client = genai.Client(api_key=apikeys["apikeys"]["google"]["aistudio"][0]["key"])
        else:
            raise KeyError("Cannot find API key in JSON data")

        # Generate content using a standard model like gemini-2.5-flash
        response = client.models.generate_content(
            model='gemini-4-argon',
            contents='Explain quantum computing in one simple sentence.',
        )

        GeminiOutputter(response)

sys.exit(main())

