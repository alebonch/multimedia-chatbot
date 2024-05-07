import ast
import os
import time

import openai
import json

import string
from dotenv import load_dotenv

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
# OPEN-AI APIs
load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')
# Set up the model
model_engine = "gpt-4-0125-preview"  # "text-davinci-003""gpt-4"gpt-3.5-turbo-1106  gpt-3.5-turbo-0125
i_dont_know_answer = ["I don't have this information",
                      "The context does not provide any",
                      "The context provided does not",
                      "not specified in the provided",
                      "there is no information"]
i_dont_know_any_language = {
    "English": [
        "I don't have this information",
        "The context does not provide any",
        "The context provided does not",
        "not specified in the provided",
        "there is no information"
    ],
    "Italian": [
        "Non ho queste informazioni",
        "Il contesto non fornisce alcuna informazione",
        "Il contesto fornito non fornisce",
        "non specificato nel fornito",
        "non c'è alcuna informazione"
    ],
    "French": [
        "Je n'ai pas cette information",
        "Le contexte ne fournit aucune information",
        "Le contexte fourni ne fournit pas",
        "non spécifié dans le fourni",
        "il n'y a pas d'information"
    ],
    "German": [
        "Ich habe diese Informationen nicht",
        "Der Kontext liefert keine Informationen",
        "Der bereitgestellte Kontext liefert nicht",
        "nicht im bereitgestellten spezifiziert",
        "es gibt keine Informationen"
    ],
    "Greek": [
        "Δεν έχω αυτές τις πληροφορίες",
        "Ο περιβάλλοντας χώρος δεν παρέχει καμία πληροφορία",
        "Ο παρεχόμενος περιβάλλοντας χώρος δεν παρέχει",
        "δεν προσδιορίζεται στο παρεχόμενο",
        "δεν υπάρχουν πληροφορίες"
    ]
}

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

    def produce_answer(self, question, artwork_title, context):
        if artwork_title != self.last_artwork_title:
            # Reset last_question and last_answer if artwork_title has changed
            self.last_question = ""
            self.last_answer = ""
            print('resetted last question and last answer')

        self.last_artwork_title = artwork_title

        prompt = f"Consider the artwork titled '{artwork_title}' and its Context. " \
                 f"Context: {context}. \n" \
                 f"Question: {question}. \n" \
                 f"Answer:"

        system_prompt = (
            "Follow these steps to answer the user question: "
            "Step 1: Read the question carefully, understand it and remember the language it has been written. "
            "Step 2: Provide a clear and concise answer keeping in mind the following guidelines: "
            "- Answer in the same language as the question. "
            "- Answer within 30 words "
            "- If the question is unrelated to the artwork, please state so. "
            "- If the information is not available in the Context, indicate that you don't have the information, writing in the language of the question 'I don't have this information.' "
            "- If there's difficulty understanding the question, ask the user to clarify the question. "
            "- Never start your answer with 'Answer:' and never use names or information that are not in the 'Context'. "
            "- If the question is in first person singular, respond in second person singular. "
            "Step 3: Translate the produced answer in the same language of the question. "
            "Step 4: Provide the answer to the user in json format with the following keys: question, question language, answer, answer translated. "
        )

        if self.last_question != "" and self.last_answer != "":
            system_prompt += f" - I'll take into account the last question and answer, if they exist: Q: {self.last_question} A: {self.last_answer} \n"

        print(prompt, "\n", system_prompt)
        answer = ""
        retry_count = 0
        max_retries = 3
        retry_delay = 1  # seconds
        while retry_count < max_retries:
            try:
                completion = openai.ChatCompletion.create(
                    model=model_engine,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.25,
                )
                # choices = completion.choices
                answer = completion.choices[0].message["content"]

                if answer.startswith("{"):
                    answer_dic = json.loads(answer)
                    language = answer_dic["question language"]
                else:
                    answer_dic = {"answer": answer}
                    language = "English"

                normalized_question = normalize_question(question)
                # if answer_dic["question language"]:
                #     language = answer_dic["question language"]
                # else:
                #     language = "English"
                unresolved = any(keyword in answer for keyword in i_dont_know_any_language[language])
                if not unresolved:
                    if artwork_title not in self.solved_questions:
                        self.solved_questions[artwork_title] = {"QA_pairs": []}
                    # Check if the question-answer pair already exists
                    qa_pairs = self.solved_questions[artwork_title]["QA_pairs"]
                    if not any(normalize_question(pair["question"]) == normalized_question  for pair in qa_pairs):
                        self.solved_questions[artwork_title]["QA_pairs"].append({
                            "question": question,
                            "answer": answer_dic['answer']
                        })
                else:
                    if artwork_title not in self.unresolved_questions:
                        self.unresolved_questions[artwork_title] = {"unresolved": []}
                    unresolved_q = self.unresolved_questions[artwork_title]["unresolved"]
                    normalized_unresolved_q = [normalize_question(q) for q in unresolved_q]
                    if normalized_question not in normalized_unresolved_q:
                        self.unresolved_questions[artwork_title]["unresolved"].append(question)

                self.last_question = question
                self.last_answer = answer_dic['answer']
                self.save_data()
                break  # Break the loop if the API call is successful
            except openai.error.OpenAIError as e:
                print("An error occurred: {}".format(e))
                self.last_answer = "There's a problem with the OpenAI API, please try again later"

            retry_count += 1
            print("Retrying in {} second(s)...".format(retry_delay))
            time.sleep(retry_delay)

        print('answer', answer)
        print(self.last_answer)
        return self.last_answer


def normalize_question(question):
    # Convert to lowercase
    question = question.lower()
    # Remove punctuation
    question = question.translate(str.maketrans('', '', string.punctuation))
    return question
