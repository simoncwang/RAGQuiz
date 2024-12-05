from util import *
import gradio as gr
from QuizSystem import QuizSystem
import os
import re

class QuizApp:
    def __init__(self):
        self.quiz_system = None
        self.file_set = set([])

    def initSystem(self, api_key):
        self.quiz_system = QuizSystem(api_key)
        gr.Info("Valid API key submitted!")

    def add_files(self, files):
        if self.quiz_system is None:
            gr.Error("Error: Please provide a valid API key first!")
        self.quiz_system.addToVectorStore(files)

        # update the internal set of files
        for file in files:
            file_name = os.path.basename(file)
            self.file_set.add(file_name)

        gr.Info("Files added successfully!")

        return self.updateFileList()

    def generate_question(self):
        if self.quiz_system is None:
            gr.Error("Error: Please provide a valid API key first!")
        return self.quiz_system.generateQuestion()
    
    def add_url(self, url):
        url_content = scrapeURL(url)
        gr.Info("URL scraped successfully!")

        # cleaning url of invalid path names
        clean_url = re.sub(r'[\\/*?:"<>|]', '_', url)

        # saving the scraped contents to a text file
        file_path = f"{clean_url}.txt"
        with open(file_path, "w") as f:
            f.write(url_content)

        # adding this file to the vector store
        self.add_files([file_path])

        # remove the file since it should already be added to the vector store
        os.remove(file_path)

        # update file list
        return self.updateFileList()
    
    def updateFileList(self):
        output = ""
        for file in self.file_set:
            output += f"- {file}\n"
        
        return output

# Create an instance of the app
quiz_app = QuizApp()

# Creating Gradio demo
with gr.Blocks() as demo:
    gr.Markdown(
        """
        **Please enter your OpenAI API Key here. Must be completed before using the app!**
        """
    )
    api_key = gr.Textbox(label="OpenAI API Key", placeholder="Your API key here")
    api_key_btn = gr.Button("Submit")

    with gr.Row():
        with gr.Column():
            gr.Markdown(
            """
            # Instructions
            Upload any documents or URLs below to be used as your personal quiz library!
            """)
            url = gr.Textbox(label="url", placeholder="Enter a URL here")
            url_btn = gr.Button("Submit URL")

            upload_btn = gr.UploadButton("Click to upload files!", file_count="multiple")

            file_list = gr.Textbox(label="My Files", placeholder="No files uploaded yet")
        with gr.Column():
            gr.Markdown(
            """
            # Your Custom Quiz
            Below is a question designed to test your knowledge on a random file from your uploads!
            """)
            question = gr.Markdown(
            """
            *Your Question*
            """
            )
            generate_btn = gr.Button("Generate Question")
            

    # Button behaviors
    api_key_btn.click(quiz_app.initSystem, inputs=[api_key])
    upload_btn.upload(quiz_app.add_files, inputs=[upload_btn], outputs=file_list)
    url_btn.click(quiz_app.add_url, inputs=[url], outputs=file_list)
    generate_btn.click(quiz_app.generate_question, outputs=question)

if __name__ == "__main__":
    demo.launch(server_name='0.0.0.0')
