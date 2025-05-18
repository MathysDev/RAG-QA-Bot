import requests
import json
from django.shortcuts import render
from django.http import HttpResponse
from .models import RAGQA


def index(request):
    get_header_info(request)  # Call get_header_info to extract header information
    messages = []  # Initialize messages as an empty list
    if RAGQA.objects.exists():
        userid = request.headers.get('X-MS-CLIENT-PRINCIPAL-ID',1)
        messages = RAGQA.objects.filter(userid=userid)
    print("Inside index view")
    ollama_api_url = "http://localhost:11434/api/pull"  # Replace with your Ollama API endpoint
    payload = {"model": "llama2"}
    response = requests.post(ollama_api_url, json=payload)
    print(response.text)
   
    return render(request, 'chat_window.html', {'messages': messages})

def get_header_info(request):
    print("Inside get_header_info view")
    username = request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME', 'Entwickler')
    userid = request.headers.get('X-MS-CLIENT-PRINCIPAL-ID',1) 
    print(f"Username: {username}, User ID: {userid}")  # Debugging line

def input_box(request):
    print("Inside input_box view")
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        user = request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME', 'Entwickler')
        userid = request.headers.get('X-MS-CLIENT-PRINCIPAL-ID',1)
        
        print(f"User Input: {user_input}")  # Debugging line
        new_message = RAGQA.objects.create(question=user_input, user=user, userid=userid)
        generate_response(new_message)
        messages = RAGQA.objects.filter(userid=userid)
        return render(request, 'chat_window.html', {'messages': messages})
    else:
        if RAGQA.objects.exists():
            messages = RAGQA.objects.all()
        
    if not messages:
        print("No messages found in the database.")
        messages = []
    return render(request, 'chat_window.html', {'messages': messages})


def generate_response(question):
    print("Inside generate_response view")
    ollama_api_url = "http://localhost:11434/api/generate"  # Replace with your Ollama API endpoint
    payload = {"prompt": question.question , "model":"llama2","system":"Du bist ein freundlicher Assistent der immer in deutscher Sprache anwtwortet. Du hälst deine Antworten stets kurz und präzise."}
    response = requests.post(ollama_api_url, json=payload)
 
    
    if response.status_code == 200:
        response_text = response.content.decode('utf-8')  # Decode response as UTF-8
        response_lines = response_text.strip().split('\n')
        responses = [json.loads(line)["response"] for line in response_lines]
        answer = "".join(responses)

    else:
        answer = "Error generating response"
        print(f"Error: {response.text}")
    print(f"Generated Answer: {answer}")  # Debugging line
    RAGQA.objects.filter(id=question.id).update(answer=answer)

def clear_chat(request):
    print("Inside clear_chat view")
    RAGQA.objects.all().delete()
    return index(request)