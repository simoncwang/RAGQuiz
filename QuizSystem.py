from openai import OpenAI
import random
from util import *
import gradio as gr

# an instance of a quiz system including an OpenAI agent and corresponding vector store
class QuizSystem():
    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.assistant = self.client.beta.assistants.create(
            name="Webpage Assistant",
            instructions="You are an expert assistant at helping users answer questions they have about webpages.",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )

        self.vector_store = self.client.beta.vector_stores.create(name="My Content")

        self.file_ids = []
    
    def addToVectorStore(self, files) -> None:
        for file in files:
             # upload the file to OpenAI
            added_file = self.client.files.create(
                file=open(file, "rb"), purpose="assistants"
            )

            # adding the file ids to our internal list
            self.file_ids.append(added_file.id)

            # add the file to the vector store
            self.client.beta.vector_stores.files.create_and_poll(
            vector_store_id=self.vector_store.id,
            file_id=added_file.id
            )

        # update assitant to use the new vector store
        self.assistant = self.client.beta.assistants.update(
        assistant_id=self.assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [self.vector_store.id]}},
        )
    
    def generateQuestion(self):
        # select a random file from our file list
        file_choice = random.choice(self.file_ids)

        # prompt to enforce structure of response
        json_prompt = """
        Please provide your question and correct answer using the following JSON format:
        {
            "question": "question description"
            "choice1": "answer choice description"
            "choice2": "answer choice description"
            "choice3": "answer choice description"
            "choice4": "answer choice description"
            "correct choice": "<Single Number>"
        }
        """

        # Create a thread and attach the file to the message
        thread = self.client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": "Give me one multiple choice question to test my knowledge of the following content. Please provide your final answer in the following JSON format: " + json_prompt,
            "attachments": [
                { "file_id": file_choice, "tools": [{"type": "file_search"}] }
            ],
            }
        ],
        )

        # Use the create and poll SDK helper to create a run and poll the status of
        # the run until it's in a terminal state.
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )

        # getting the resulting messages
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text

        file_search_output = message_content.value

        ##### use structured outputs to enforce a correct JSON format from this raw text
        
        # setting up instructions for the structured output
        messages=[
            {
            "role": "system",
            "content": "You are gpt-4o, a large language model trained by OpenAI. Given a user submitted text that may or may not be in JSON format, your goal is to output a valid JSON format based on the specified quiz structure with a question description, four possible answer choices with string descriptions, and an integer specifying the SINGLE correct choice."
            },
        ]

        # appending the message
        messages.append(
            {"role": "user", "content": file_search_output},
        )

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=QuizSchema,
        )

        response = completion.choices[0].message

        # If the model refuses to respond, you will get a refusal message
        if (response.refusal):
            print(response.refusal)

        # parse the question (auto parsing from openai)
        response = response.parsed

        # setting up gradio checkboxes for the possible choices
        # choice1 = gr.Checkbox(label=response.choice1, info="Choice 1", value=False)
        # choice2 = gr.Checkbox(label=response.choice2, info="Choice 2", value=False)
        # choice3 = gr.Checkbox(label=response.choice3, info="Choice 3", value=False)
        # choice4 = gr.Checkbox(label=response.choice4, info="Choice 4", value=False)

        # setting gradio markdown element for answer choices
        choiceDisplay = gr.Markdown(
            f"Choice 1: {response.choice1}<br>Choice 2: {response.choice2}<br>Choice 3: {response.choice3}<br>Choice 4: {response.choice4}"
        )

        # empty markdown for answer check section
        choice_check = gr.Markdown("")

        # returning the response
        return response.question, choiceDisplay, response.correct_choice, choice_check