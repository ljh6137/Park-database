from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
# from .models import 

# Create your views here.


# def detail(request, question_id):
#     return HttpResponse()



# management/views.py
from django.shortcuts import render

def register(request):
    if request.method == 'GET':
        return render(request, 'management/register.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print(1)
        # create user
        
        messages.success(request, 'Registration successful!')
        return render(request, 'management/register.html')
        # return redirect('login')
    # return render(request, 'management/register.html')  # 渲染登录模板
