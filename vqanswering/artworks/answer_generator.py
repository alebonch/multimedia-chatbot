import ast
import base64
import os
import re
import time

import openai
import json

import string
from dotenv import load_dotenv
from langdetect import detect
from .models import Artwork, Chat, Metadata
from django.templatetags.static import static
from django.utils.html import escape

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
# OPEN-AI APIs
load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')
# Set up the model
model_engine = "gpt-4o-mini"# "gpt-4o-2024-05-13"  # "gpt-4-0125-preview""text-davinci-003""gpt-4"gpt-3.5-turbo-1106  gpt-3.5-turbo-0125


# i_dont_know_answer = ["I don't have this information",
#                       "The context does not provide any",
#                       "The context provided does not",
#                       "not specified in the provided",
#                       "there is no information"]
#
# i_dont_know_any_language = {
#     "English": [
#         "I don't have this information",
#         "The context does not provide any",
#         "The context provided does not",
#         "not specified in the provided",
#         "there is no information"
#     ],
#     "Italian": [
#         "Non ho queste informazioni",
#         "Il contesto non fornisce alcuna informazione",
#         "Il contesto fornito non fornisce",
#         "non specificato nel fornito",
#         "non c'è alcuna informazione"
#     ],
#     "French": [
#         "Je n'ai pas cette information",
#         "Le contexte ne fournit aucune information",
#         "Le contexte fourni ne fournit pas",
#         "non spécifié dans le fourni",
#         "il n'y a pas d'information"
#     ],
#     "German": [
#         "Ich habe diese Informationen nicht",
#         "Der Kontext liefert keine Informationen",
#         "Der bereitgestellte Kontext liefert nicht",
#         "nicht im bereitgestellten spezifiziert",
#         "es gibt keine Informationen"
#     ],
#     "Greek": [
#         "Δεν έχω αυτές τις πληροφορίες",
#         "Ο περιβάλλοντας χώρος δεν παρέχει καμία πληροφορία",
#         "Ο παρεχόμενος περιβάλλοντας χώρος δεν παρέχει",
#         "δεν προσδιορίζεται στο παρεχόμενο",
#         "δεν υπάρχουν πληροφορίες"
#     ]
# }


def load_i_dont_know_any_language():
    with open("static/assets/json/i_dont_know_any_language.json", "r", encoding='utf-8') as json_file:
        i_dont_know_any_language = json.load(json_file)
    return i_dont_know_any_language


def load_json_file(file):
    with open(file, "r", encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


i_dont_know_any_language = load_json_file("static/assets/json/i_dont_know_any_language.json")
languages = load_json_file("static/assets/json/languages.json")


class AnswerGenerator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnswerGenerator, cls).__new__(cls)
            cls._instance.last_question = ""
            cls._instance.last_answer = ""
            cls._instance.last_artwork_title = ""
            cls._instance.unresolved_questions = {}
            cls._instance.solved_questions = {}
            cls._instance.load_existing_data()
        return cls._instance

    def load_existing_data(self):
        if os.path.exists("static/assets/json/qa_pairs.json"):
            with open("static/assets/json/qa_pairs.json", "r", encoding='utf-8') as json_file:
                self.solved_questions = json.load(json_file)
        if os.path.exists("static/assets/json/unresolved_questions.json"):
            with open("static/assets/json/unresolved_questions.json", "r", encoding='utf-8') as json_file:
                self.unresolved_questions = json.load(json_file)

    def save_data(self):
        with open("static/assets/json/qa_pairs.json", "w", encoding='utf-8') as json_file:
            json.dump(self.solved_questions, json_file, indent=2, ensure_ascii=False)
        with open("static/assets/json/unresolved_questions.json", "w", encoding='utf-8') as json_file:
            json.dump(self.unresolved_questions, json_file, indent=2, ensure_ascii=False)

    def produce_answer(self, question, language, artwork, metadata = None):
        context = (artwork.description + " year: " + str(artwork.year) + " subject: " + artwork.subject +
                   " type of object: " + artwork.type_of_object +
                   " materials and techniques: " + artwork.materials_and_techniques +
                   " measurament: " + artwork.measurement + " maker: " + artwork.maker+"\n")
        title = artwork.title
        image_path = artwork.thumb_image
        if title != self.last_artwork_title:
            # Reset last_question and last_answer if artwork_title has changed
            self.last_question = ""
            self.last_answer = ""
            print('resetted last question and last answer')
        self.last_artwork_title = title
        base64_image = encode_image(image_path)
        # portare in json

        #prendere metadati se ci sono facendo query

        with open("artworks/prompts/prompts.json", 'r') as json_file:
            prompts = json.load(json_file)

        system_prompt = prompts['system_prompt']
        prompt_template = prompts['prompt_template']
        
        if self.last_question != "" and self.last_answer != "":
            system_prompt += (f" - If the current question is the same as the last question, generate a different "
                              f"response to avoid repetition. Last Q: {self.last_question} Last A: {self.last_answer} \n "
                              f"- If the current question is similar to the last question, generate a different response ")
            #checker metadati

        if metadata is not None:
            metadata_types = set()  
            i = 0
            metadata_context = "//////////////// METADATAs divider \\\\\\\\\\\\\\\\ \n Number of metadatas: "+str(len(metadata))+"\n"
            for value in metadata:
                i += 1
                metadata_context += (" | description of "+ str(i) +"° metadata ("+ value.type +"): "
                            +value.description+"\n  metadata_id: "+str(value.id)+"\n")
                meta_type = value.type if value.type else "Unknown type"
                metadata_types.add(meta_type)
            prompt_template += prompts['prompt_metadata']
            if 'audio' in metadata_types:
                system_prompt += prompts['prompt_audio']
            if 'video' in metadata_types:
                system_prompt += prompts['prompt_video']
            if 'link' in metadata_types:
                system_prompt += prompts['prompt_link']
            prompt = prompt_template.format(title=title, context=context, metadatas=metadata_context, question=question)
        else:
            prompt = prompt_template.format(title=title, context=context, metadatas="null", question=question)
        
        print(language)

        print('context: ',context)
        retry_count = 0
        max_retries = 3
        retry_delay = 1  # seconds
        while retry_count < max_retries:
            try:
                completion = openai.ChatCompletion.create(
                    model=model_engine,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"}
                             }
                        ]},
                    ],
                    temperature=0.55,
                )
                # choices = completion.choices
                answer = completion.choices[0].message["content"]
                json_dict = extract_json(answer)
                html = ""
                if json_dict['metadata']["metadata_id"] != "None":
                    metadata_id = json_dict['metadata']["metadata_id"]
                    metadata = Metadata.objects.get(id=metadata_id)
                    if metadata.type == 'audio':
                        # Use static to construct the correct URL
                        audio_url = static(metadata.link)  
                        html = f'<audio controls class= "custom-audio"><source src="{escape(audio_url)}" type="audio/mpeg"></audio>'
                    
                    elif metadata.type == 'video':
                        # Use static to construct the correct URL for video
                        video_url = static(metadata.link)  
                        html = f'<video controls class= "custom-video"><source src="{escape(video_url)}" type="video/mp4"></video>'
                    
                    elif metadata.type == 'link':
                        # Escape the link properly
                        weblink = escape(metadata.weblink)
                        html = f'<button class="custom-button" onclick="window.open(\'{weblink}\', \'_blank\');">Click me!</button>'
                chat = analyze_answer(answer, question, language, artwork)
                self.last_question = question
                if chat is not None:
                    self.last_answer = chat.answer
                else:
                    self.last_answer = answer 

                self.save_data()
                break  # Break the loop if the API call is successful
            except openai.error.OpenAIError as e:
                print("An error occurred: {}".format(e))
                self.last_answer = "There's a problem with the OpenAI API, please try again later"

            retry_count += 1
            print("Retrying in {} second(s)...".format(retry_delay))
            time.sleep(retry_delay)

        print('answer: ', self.last_answer)
        return self.last_answer, html


def encode_image(image_path):
    print(image_path)
    base_dir = os.path.dirname(__file__)
    print(base_dir)  # get the directory of the current script
    full_path = os.path.join(base_dir, '..', image_path.lstrip('/'))  # construct the full path
    print(full_path)
    with open(full_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def is_english(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except:
        # If langdetect encounters an error (e.g., short input), return False
        return False


def find_lang(text):
    try:
        print(text)
        lang = detect(text)
        print(lang)
        if lang.startswith('zh'):
            lang_name = 'Chinese'
        else:
            for language in languages:
                print(languages[language][0])
                if languages[language][0].startswith(lang):

                    lang_name = language
                    return lang_name
                else:
                    lang_name = 'English (United Kingdom)'

        return lang_name
    except:
        # If langdetect encounters an error (e.g., short input), return False
        return False


def extract_json(answer):
    # Check if the answer contains JSON content
    if "{" in answer:
        start_index = answer.index("{")
        end_index = answer.rindex("}") + 1
        json_part = answer[start_index:end_index]
        json_part = json_part.replace(': True', ': true').replace(': False', ': false')
        print('Answer:', answer)
        print('JSON content found:', repr(json_part))
        try:
            return json.loads(json_part)
        except json.JSONDecodeError as e:
            print('Invalid JSON content:', json_part)
            print('Error:', repr(e))
            return None
    else:
        return None


def handle_keyword_responses(answer, question, language):
    # Check if the answer starts with any predefined keywords
    for keyword in i_dont_know_any_language:
        for phrase in i_dont_know_any_language[keyword]:
            if answer.startswith(phrase):
                print("No information available for:", answer)
                q_lan = find_lang(question)
                print(q_lan)
                translated_answer = i_dont_know_any_language[q_lan][0] if q_lan else \
                    i_dont_know_any_language['English (United Kingdom)'][0]

                return {
                    "answer": translated_answer,
                    "question": question,
                    "question language": "English (United Kingdom)" if is_english(question) else language,
                    "answer translated": translated_answer
                }
    return None


def analyze_answer(answer, question, language, artwork):
    # Extract JSON content
    json_dict = extract_json(answer)
    if json_dict:
        if check_existing_qa(artwork, question, json_dict['answer'], json_dict['resolved']):
            print('Similar Q&A already exists in the database.')
            return None
        else:
            chat = Chat.objects.create(
                artwork=artwork,
                question=question,
                answer=json_dict['answer'],
                question_language=json_dict['question language'],
                resolved=json_dict['resolved']
            )
            return chat

    print('Handle keyword-based responses')
    keyword_response = handle_keyword_responses(answer, question, language)
    if keyword_response:
        if check_existing_qa(artwork, question, keyword_response['answer'], False):
            print('Similar Q&A already exists in the database.')
            return None
        else:
            chat = Chat.objects.create(
                artwork=artwork,
                question=question,
                answer=keyword_response['answer'],
                question_language=keyword_response['question language'],
                resolved=False
            )
            return chat

    print(' Default case: No JSON content or keyword match')
    translated_answer = answer if is_english(question) else i_dont_know_any_language.get(language, [answer])[0]
    if check_existing_qa(artwork, question, translated_answer, True):
        print('Similar Q&A already exists in the database.')
        return None
    else:
        chat = Chat.objects.create(
            artwork=artwork,
            question=question,
            answer=translated_answer,
            question_language="English (United Kingdom)" if is_english(question) else language,
            resolved=True
        )
        return chat


def check_existing_qa(artwork, question, answer, resolved):
    existing_chat = Chat.objects.filter(
        artwork=artwork,
        question=question,
        answer=answer,
        resolved=resolved
    )
    return existing_chat.exists()