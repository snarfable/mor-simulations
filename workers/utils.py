# coding: utf-8

from google.genai.types import GenerateContentResponse

def wrap_by_word_count(text, words_per_line=10):
  words = text.split()
  return [
      " ".join(words[i : i + words_per_line])
      for i in range(0, len(words), words_per_line)
  ]

class GeminiOutputter(object):
    """
    Outputs the candidate responses from Google Gemini.
    """
    def __init__(self, response: GenerateContentReponse):
        for index, candidate in enumerate(response.candidates):
            print(f"Candidate {index}:")
            for pindex, part in enumerate(candidate.content.parts):
                print(f"\tPart {pindex}:")
                lines = wrap_by_word_count(part.text)
                for line in lines:
                    print("\t\t" + line)
