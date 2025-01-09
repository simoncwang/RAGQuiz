# RAGQuiz
A personalized quiz system using retrieval augmented generation.

## Instructions

First, **clone this repository** to your local machine:

    git clone https://github.com/simoncwang/RAGQuiz.git

Then, **create a Python environment**

Conda:

    conda create -n rag-quiz python=3.12

**activate the environment** with

Conda:

    conda activate rag-quiz

Next, **install the required packages** with:

    pip install -r requirements.txt

Finally, **launch the app** by running:

    python3 app.py

which should launch a Gradio demo, follow the url given to the web app.

## Usage

Below is a screenshot example of the UI, once running it will contain some instructions to use the app! (detailed instructions will be updated in the future)

![Screenshot 2025-01-09 at 12 31 43 AM](https://github.com/user-attachments/assets/272b0d1f-e6f9-45d4-98f3-1981b1da25da)

NOTE: You can submit multiple files to be stored in the system, and the generate quiz function will randomly select a file from your list to create a question! Files can be uploaded directly from your computer, OR through URL (content is scraped using Selenium).
