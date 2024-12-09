from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# from .models import 

# Create your views here.


# def detail(request, question_id):
#     return HttpResponse()



# management/views.py
from django.shortcuts import render

def login(request):
    return render(request, 'management/login.html')  # 渲染登录模板
