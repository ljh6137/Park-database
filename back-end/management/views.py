import logging
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, Repository, Lease, Customer, Info
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
# from .models import 
import json
from django.db import transaction
from .utils import generate_timestamp

logger = logging.getLogger('myapp')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

def register(request):
    if request.method == 'GET':
        return render(request, 'management/register.html')

    if request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        contact = request.POST.get('contact', '').strip()

        # 简单校验是否填写所有字段
        if not username or not password or not contact:
            messages.error(request, 'All fields are required.')
            return render(request, 'management/register.html')

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another one.')
            return render(request, 'management/register.html')

        try:
            # 创建用户和客户信息
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
                Customer.objects.create(user=user, ID=username, name=username, contact=contact)

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')

        except Exception as e:
            logger.error(f"Error during registration: {e}")
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'management/register.html')

    return render(request, 'management/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in successfully.")
            return redirect('homepage')  # 登录成功后跳转到用户仪表盘
        else:
            logger.error(f"Failed login attempt for username {username}.")
            messages.error(request, 'Invalid username or password.')
    return render(request, 'management/login.html')

@login_required
def rent_car_view(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        logger.debug(f"Attempting to rent vehicle with ID: {vehicle_id}")
        try:
            # 获取当前登录的用户来查找关联的 Customer 实例
            customer = get_object_or_404(Customer, user=request.user)
        except Customer.DoesNotExist:
            logger.error(f"Vehicle with ID {vehicle_id} not found.")
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
            logger.error(f"Repository entry for vehicle with ID {vehicle_id} not found.")
            messages.error(request, "Repository entry for vehicle not found.")
            return redirect('rent_car')

        if repository.Is_leased:
            logger.warning(f"Vehicle with ID {vehicle_id} is already leased.")
            messages.error(request, "This vehicle is already leased!")
            return redirect('rent_car')

        Lease.objects.create(Car_ID=repository, ID=customer)
        repository.Is_leased = True
        repository.save()
        logger.info(f"Vehicle with ID {vehicle_id} leased successfully to user {request.user.username}.")
        messages.success(request, "Vehicle leased successfully!")
        return redirect('rent_car')

    available_vehicles = Vehicle.objects.filter(info_model__Car_ID__Is_leased=False)
    return render(request, 'management/rent_car.html', {'vehicles': available_vehicles})

def ui(request):
    return render(request, 'management/UI.html')  # 创建并渲染一个主页模

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
            logger.info(f"User {user.username} rented vehicles: {rented_vehicles}")
    else:
        rented_vehicles = []

    return render(request, 'management/rented_vehicles.html', {'rented_vehicles': rented_vehicles})

def home(request):
    return render(request, 'management/UI.html')
 
def get_repository_by_name(request):
    if request.method == "GET":
        name = request.GET.get("name")  # 获取点击的 name 参数
        try:
            # 查询 Vehicle 表中匹配的 name，并关联查询 Repository 表
            vehicle = Vehicle.objects.get(name=name)
            repositories = Repository.objects.filter(model=vehicle)
            # 构建返回数据
            data = list(repositories.values("id", "description", "created_at"))
            return JsonResponse({"status": "success", "data": data})
        except Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Vehicle not found"})
        
def get_vehicles(request):
    vehicles = Vehicle.objects.all()
    if vehicles.exists():
        data = list(vehicles.values("Model"))
        return JsonResponse({"status": "success", "data": data})
    else:
        return JsonResponse({"status": "empty", "message": "暂无车辆信息"})

# 获取具体车辆的详细信息
def get_vehicle_details(request):
    if request.method == "GET":
        car_name = request.GET.get("name")
        if not car_name:
            return JsonResponse({"status": "error", "message": "车辆名称不能为空"})

        # data_object = Repository.objects.get(id=car_name)

        # 时间戳协议检查
        # if transaction_timestamp < data_object.w_timestamp:
            # return JsonResponse({"error": "读操作被拒绝：事务时间戳小于写时间戳"}, status=409)

        # 允许读取操作，更新 R-timestamp(Q)
        # data_object.r_timestamp = max(data_object.r_timestamp, transaction_timestamp)
        # data_object.save()


        # 事务时间戳
        transaction_timestamp = generate_timestamp()  # 当前事务的时间戳
        
        query = """
            SELECT a."Car_ID", a."Is_leased", b."Price"
            FROM management_repository a, management_vehicle b
            JOIN management_info c ON b."Model" = c."Model_id"
            WHERE a."Car_ID" = c."Car_ID_id" AND b."Model" = %s AND %s >= a.w_timestamp
        """
        # update_query = """
        #         UPDATE management_repository
        #         SET r_timestamp = max(r_timestamp, %d)
        #         WHERE "Car_ID" = %s AND r_timestamp < w_timestamp
        #     """
        
        update_query = """
            UPDATE management_repository
            SET r_timestamp = GREATEST(r_timestamp, %s)
            WHERE (%s >= w_timestamp) AND "Car_ID" in (
                SELECT a."Car_ID"
                FROM management_repository a, management_vehicle b
                JOIN management_info c ON b."Model" = c."Model_id"
                WHERE a."Car_ID" = c."Car_ID_id" AND b."Model" = %s
            )
        """

        with connection.cursor() as cursor:
            try:
                # 执行查询语句
                cursor.execute(query, [car_name, transaction_timestamp])
                rows = cursor.fetchall()

                # 检查是否有结果
                if not rows:
                    print("未找到对应的记录或查询失败")
                else:

                    # 执行更新语句
                    
                    # print("qwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqw")
                    cursor.execute(update_query, [transaction_timestamp, transaction_timestamp, car_name])
                    if cursor.rowcount == 0:  # rowcount 检查更新是否成功
                        # print(transaction_timestamp)
                        print("更新失败：r_timestamp >= w_timestamp，操作被拒绝")
                    else:
                        print("更新成功")

            except Exception as e:
                print(f"数据库操作失败: {e}")

            data = [
                {"Car_ID": row[0], "Is_leased": row[1], "Price": row[2]}
                for row in rows
            ]

        if data:
            return JsonResponse({"status": "success", "data": data, "TS": transaction_timestamp})
        else:
            return JsonResponse({"status": "empty", "message": "未找到车辆详情"})
        
@login_required
def homepage(request):
    if request.method == "GET":
    # 获取当前用户的租赁车辆信息
        rented_cars = Lease.objects.filter(ID__user=request.user).select_related('Car_ID')

        rented_cars_data = []
        for lease in rented_cars:
            # 获取关联的 Repository 和 Vehicle 信息
            car = lease.Car_ID
            car_info = car.info_set.first()  # 获取车辆的关联信息
            vehicle = car_info.Model if car_info else None  # 获取车辆的模型（Vehicle）

            # 格式化租赁车辆数据
            rented_cars_data.append({
                "license_plate": car.Car_ID,  # 使用 Repository 表中的 Car_ID 作为车牌号
                "model": vehicle.Model if vehicle else "Unknown",  # 获取车型
                "price": vehicle.Price if vehicle else "Unknown",  # 获取价格
            })

        # 渲染模板并传递租赁车辆数据
        return render(request, 'management/homepage.html', {'rented_cars': rented_cars_data})
    elif request.method == "POST":
        pass


lock_X = 0

@login_required
# @transaction.atomic
def lease_vehicle(request):
    """
    租赁车辆视图：更新车辆状态并创建租赁记录
    """
    if request.method == "POST":
        try:
            # 接收 JSON 数据
            data = json.loads(request.body)
            car_id = data.get("car_id")  # 获取车牌号
            user_id = request.user.username  # 获取当前用户ID
            print("qwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqw")
            if not car_id:
                return JsonResponse({"status": "error", "message": "车辆ID不能为空"})

            data_object = Repository.objects.get(Car_ID=car_id)
            transaction_timestamp = data.get("ts")  # 当前事务的时间戳

            print(transaction_timestamp)

            # 时间戳协议检查
            if transaction_timestamp < data_object.r_timestamp:
                return JsonResponse({"message": "租车失败，车辆租赁信息已更改"}, status=409)

            if transaction_timestamp < data_object.w_timestamp:
                return JsonResponse({"message": "租车失败，车辆租赁信息已更改"}, status=409)

            data_object.w_timestamp = transaction_timestamp
            data_object.save()

            # 更新车辆租赁状态
            update_query = """
                UPDATE management_repository
                SET "Is_leased" = TRUE
                WHERE "Car_ID" = %s
            """
            # 插入租赁记录
            insert_query = """
                INSERT INTO management_lease ("ID_id","Car_ID_id")
                VALUES (%s, %s)
            """
            
            print(car_id)
            with connection.cursor() as cursor:
                cursor.execute(update_query, [car_id])  # 更新车辆状态
                cursor.execute(insert_query, [user_id, car_id])  # 插入租赁记录
            
            # print(1)
            return JsonResponse({"status": "success", "message": "车辆租赁成功！"})

        except Exception as e:
            print(f"Error leasing vehicle: {e}")
            return JsonResponse({"status": "error", "message": "租赁失败，请稍后再试。"})

    return JsonResponse({"status": "error", "message": "无效的请求方法"})


@login_required
def return_vehicle(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')

        if not vehicle_id:
            messages.error(request, "Vehicle ID is required.")
            return redirect('homepage')

        try:
            # 获取当前登录用户的租赁记录
            lease = Lease.objects.get(Car_ID__Car_ID=vehicle_id, ID__user=request.user)
        except Lease.DoesNotExist:
            messages.error(request, "You have not rented this vehicle.")
            return redirect('homepage')

        # 取消租赁并更新仓库的车辆状态
        repository = lease.Car_ID
        repository.Is_leased = False  # 标记车辆为未租赁
        repository.save()

        # 删除租赁记录
        lease.delete()
        logger.info(f"User {request.user.username} returned vehicle with ID {vehicle_id}.")
        messages.success(request, f"You have successfully returned the vehicle: {vehicle_id}.")
        
        # JsonResponse({"status": "success", "message": "车辆租赁成功！"})
        return redirect('homepage')

    return redirect('homepage')