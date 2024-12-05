from openai import OpenAI
import random

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
    
    def generateQuestion(self) -> str:
        # select a random file from our file list
        file_choice = random.choice(self.file_ids)

        # prompt to enforce structure of response
        json_prompt = """
        Please provide your question and correct answer using the following JSON format:
        {
            "question": "<Question>"
            "correct answer": "<Single Letter>"
        }
        """

        # Create a thread and attach the file to the message
        thread = self.client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": "Give me one multiple choice question to test my knowledge of the following content. Also provide the correct answer choice in a single letter." + json_prompt,
            # Attach the new file to the message.
            "attachments": [
                { "file_id": file_choice, "tools": [{"type": "file_search"}] }
            ],
            }
        ]
        )

        # Use the create and poll SDK helper to create a run and poll the status of
        # the run until it's in a terminal state.
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )

        # getting the resulting messages
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text

        # returning the response
        return message_content.value