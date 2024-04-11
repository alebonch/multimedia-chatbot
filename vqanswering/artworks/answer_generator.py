import ast
import os
import time

import openai
import json

import requests
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
                      "not specified in the provided"]

class AnswerGenerator:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnswerGenerator, cls).__new__(cls)
            cls._instance.last_question = ""
            cls._instance.last_answer = ""
            cls._instance.last_artwork_title = ""
            cls._instance.unresolved_questions = {}
        return cls._instance

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
        # system_prompt = (
        #     "I want you to act as an art expert. Answer in user's language as concisely as possible. "
        #     # "Provide a clear and concise answer in the same question's language within 30 words. "
        #     "Creating your answer pay attention to the following rules: "
        #     "If the question is unrelated to the artwork, please state so. "
        #     "If the information is not available in the Context, indicate that you don't have the information, writing in the language of the question 'I don't have this information.' "
        #     "If there's difficulty understanding the question, ask the user to clarify the question. "
        #     "Never start your answer with 'Answer:' and never use names or information that are not in the 'Context'. "
        #     "If the question is in first person singular, respond in second person singular. "
        #     # "If the translated answer is longer than the limit of 30 words, rephrase it to stay in that limit. "
        #     "If the Context is not enough to answer, respond with your internal knowledge, saying that the answer could be imprecise. "
        #     # "Remember to answer in the same language as the question. "
        #     "It's very important that the answer is in the same language of the question "
        # )
        system_prompt = (
            "I will act as an art and language expert and respond in the same language as your question as concisely as possible within 30 words. "
            "I will translate the answer in the same language as your question."
            "I'll keep in mind the following guidelines: "
            "- If your question is unrelated to artwork, I will let you know. "
            "- If I don't have the information you're asking for, I'll indicate that by saying 'I don't have this information' in the language of your question. "
            "- If I find it difficult to understand your question, I'll ask you to clarify. "
            "- I won't start my response with 'Answer:' and will only use information available in our conversation. "
            "- If I can't answer based on our conversation, I may provide an answer based on my internal knowledge, but it could be imprecise."
            "- If the answer is longer than 30 words, I'll rephrase it to stay within the limit. ")
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
            # "- If the answer is not in the same language as the question, translate it. "
            "Step 3: Translate the produced answer in the same language of the question. "
            # "Step 4: Write in a json format the question, the question language, the answer and the translated answer. "
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
                # print('choices', choices)
                result_found = True
                if any(keyword in answer for keyword in i_dont_know_answer):
                    result_found = False
                if not result_found:
                    if artwork_title not in self.unresolved_questions:
                        self.unresolved_questions[artwork_title] = {"unresolved": []}

                    self.unresolved_questions[artwork_title]["unresolved"].append(question)
                    with open("static/assets/json/unresolved_questions.json", "w") as json_file:
                        json.dump(self.unresolved_questions, json_file, indent=2)

                self.last_question = question
                self.last_answer = answer
                break  # Break the loop if the API call is successful
            except openai.error.OpenAIError as e:
                print("An error occurred: {}".format(e))
                answer = "There's a problem with the OpenAI API, please try again later"

            retry_count += 1
            print("Retrying in {} second(s)...".format(retry_delay))
            time.sleep(retry_delay)
        # prompt_translate = (f"Consider the question '{question}' and the provided answer '{answer} "
        #                     f"Question: 'Translate the answer in the language of the question. \n"
        #                     f"Answer:")
        # system_prompt_translate = (
        #     "I will act as an art expert and able language translator. "
        #     "I will translate the answer in the same language as your question. "
        # )
        # translation = openai.ChatCompletion.create(
        #     model=model_engine,
        #     messages=[
        #         {"role": "system", "content": system_prompt_translate},
        #         {"role": "user", "content": prompt_translate},
        #     ],
        #     temperature=0.25,
        # )
        # answer_translated = translation.choices[0].message["content"]
        answer_dic = json.loads(answer)
        print('answer', answer)
        print(answer_dic['answer'])
        return answer_dic['answer']
