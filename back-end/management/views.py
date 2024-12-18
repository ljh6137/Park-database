
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, Repository, Lease, Customer, Info
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'GET':
        return render(request, 'management/register.html')
    
    if request.method == 'POST':
        # 获取提交的用户名和密码
        username = request.POST['username']
        password = request.POST['password']
        
        # 检查用户名是否已经存在
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another one.')
            return render(request, 'management/register.html')
        
        # 创建用户并加密密码
        user = User.objects.create_user(username=username, password=password)
        
        # 创建对应的 Customer 实例
        customer = Customer.objects.create(user=user, ID=username, name=username, contact="")  # 可以根据需要设置默认的 contact
        
        # 提示用户注册成功
        messages.success(request, 'Registration successful! Please log in.')
        
        # 注册成功后，跳转到登录页面
        return redirect('login')
    
    return render(request, 'management/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # 登录成功后跳转到用户仪表盘
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'management/login.html')

@login_required
def rent_car_view(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')

        try:
            # 获取当前登录的用户来查找关联的 Customer 实例
            customer = get_object_or_404(Customer, user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "You need to complete your customer profile before renting a car.")
            return redirect('profile')  # 重定向到用户个人资料页面或其他页面

        try:
            vehicle = Vehicle.objects.get(Model=vehicle_id)
        except Vehicle.DoesNotExist:
            messages.error(request, "Vehicle not found.")
            return redirect('rent_car')

        try:
            repository = Repository.objects.get(Car_ID=vehicle_id)
        except Repository.DoesNotExist:
            messages.error(request, "Repository entry for vehicle not found.")
            return redirect('rent_car')

        if repository.Is_leased:
            messages.error(request, "This vehicle is already leased!")
            return redirect('rent_car')

        Lease.objects.create(Car_ID=repository, ID=customer)
        repository.Is_leased = True
        repository.save()

        messages.success(request, "Vehicle leased successfully!")
        return redirect('rent_car')

    available_vehicles = Vehicle.objects.filter(info_model__Car_ID__Is_leased=False)
    return render(request, 'management/rent_car.html', {'vehicles': available_vehicles})

def home_view(request):
    return render(request, 'management/home.html')  # 创建并渲染一个主页模

@login_required
def rented_vehicles_view(request):
    # 获取当前登录的用户
    user = request.user

    try:
        # 获取该用户的 Customer 对象，假设用户模型和 Customer 一对一关联
        customer = Customer.objects.get(ID=user.username)  # 假设用户ID与Customer模型的ID字段匹配
    except Customer.DoesNotExist:
        customer = None

    if customer:
        # 获取该用户租赁的所有车辆
        leases = Lease.objects.filter(ID=customer)
        rented_vehicles = []
        for lease in leases:
            vehicle = lease.Car_ID.Model  # 获取租赁车辆的模型
            rented_vehicles.append(vehicle)
    else:
        rented_vehicles = []

    return render(request, 'management/rented_vehicles.html', {'rented_vehicles': rented_vehicles})