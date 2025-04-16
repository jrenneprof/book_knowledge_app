# book-knowledge-app
<<<<<<< HEAD
COT 5930-009: Conversational AI Course Project

Book Knowledge App (Flask Audio App) 

The Book Knowledge App enables users to upload a PDF book and ask audio questions about its content. Using Google Cloud's Speech-to-Text API, the app transcribes the spoken question into text, which is then passed—along with the PDF content—to a Large Language Model (LLM) for contextual understanding and response generation. The generated answer is then converted to speech using Google Cloud Text-to-Speech API and played back to the user.

The application is deployed on Google Cloud Run, providing serverless scalability, high availability, and a public endpoint for ease of access.

