from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'chat_window.html')


def input_box(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        return render(request, 'chat_window.html')
    return render(request, 'input_box.html')
