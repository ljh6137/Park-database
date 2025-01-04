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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        contact = request.POST.get('contact', '').strip()
        if not username or not password or not contact:
            messages.error(request, 'All fields are required.')
            return render(request, 'management/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another one.')
            return render(request, 'management/register.html')

        try:
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
            return redirect('homepage') 
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
            customer = get_object_or_404(Customer, user=request.user)
        except Customer.DoesNotExist:
            logger.error(f"Vehicle with ID {vehicle_id} not found.")
            messages.error(request, "You need to complete your customer profile before renting a car.")
            return redirect('profile') 

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
    return render(request, 'management/UI.html') 

@login_required
def rented_vehicles_view(request):
    user = request.user

    try:
        customer = Customer.objects.get(ID=user.username) 
    except Customer.DoesNotExist:
        customer = None

    if customer:
        leases = Lease.objects.filter(ID=customer)
        rented_vehicles = []
        for lease in leases:
            vehicle = lease.Car_ID.Model 
            rented_vehicles.append(vehicle)
            logger.info(f"User {user.username} rented vehicles: {rented_vehicles}")
    else:
        rented_vehicles = []

    return render(request, 'management/rented_vehicles.html', {'rented_vehicles': rented_vehicles})

def home(request):
    return render(request, 'management/UI.html')
 
def get_repository_by_name(request):
    if request.method == "GET":
        name = request.GET.get("name")  
        try:
            vehicle = Vehicle.objects.get(name=name)
            repositories = Repository.objects.filter(model=vehicle)
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

def get_vehicle_details(request):
    if request.method == "GET":
        car_name = request.GET.get("name")
        if not car_name:
            return JsonResponse({"status": "error", "message": "车辆名称不能为空"})

        transaction_timestamp = generate_timestamp() 
        
        query = """
            SELECT a."Car_ID", a."Is_leased", b."Price"
            FROM management_repository a, management_vehicle b
            JOIN management_info c ON b."Model" = c."Model_id"
            WHERE a."Car_ID" = c."Car_ID_id" AND b."Model" = %s AND %s >= a.w_timestamp
        """
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
                cursor.execute(query, [car_name, transaction_timestamp])
                rows = cursor.fetchall()

                if not rows:
                    print("未找到对应的记录或查询失败")
                else:

                    cursor.execute(update_query, [transaction_timestamp, transaction_timestamp, car_name])
                    if cursor.rowcount == 0: 
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
        rented_cars = Lease.objects.filter(ID__user=request.user).select_related('Car_ID')

        rented_cars_data = []
        for lease in rented_cars:
            car = lease.Car_ID
            car_info = car.info_set.first()
            vehicle = car_info.Model if car_info else None 

            rented_cars_data.append({
                "license_plate": car.Car_ID,  
                "model": vehicle.Model if vehicle else "Unknown", 
                "price": vehicle.Price if vehicle else "Unknown",
            })

        return render(request, 'management/homepage.html', {'rented_cars': rented_cars_data})
    elif request.method == "POST":
        pass


lock_X = 0

@login_required
def lease_vehicle(request):
    """
    租赁车辆视图：更新车辆状态并创建租赁记录
    """
    if request.method == "POST":
        try:

            data = json.loads(request.body)
            car_id = data.get("car_id")  
            user_id = request.user.username  
            print("qwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqwqw")
            if not car_id:
                return JsonResponse({"status": "error", "message": "车辆ID不能为空"})

            data_object = Repository.objects.get(Car_ID=car_id)
            transaction_timestamp = data.get("ts")  

            print(transaction_timestamp)


            if transaction_timestamp < data_object.r_timestamp:
                return JsonResponse({"message": "租车失败，车辆租赁信息已更改"}, status=409)

            if transaction_timestamp < data_object.w_timestamp:
                return JsonResponse({"message": "租车失败，车辆租赁信息已更改"}, status=409)

            data_object.w_timestamp = transaction_timestamp
            data_object.save()

            update_query = """
                UPDATE management_repository
                SET "Is_leased" = TRUE
                WHERE "Car_ID" = %s
            """

            insert_query = """
                INSERT INTO management_lease ("ID_id","Car_ID_id")
                VALUES (%s, %s)
            """
            
            print(car_id)
            with connection.cursor() as cursor:
                cursor.execute(update_query, [car_id])  
                cursor.execute(insert_query, [user_id, car_id])  
            
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
            lease = Lease.objects.get(Car_ID__Car_ID=vehicle_id, ID__user=request.user)
        except Lease.DoesNotExist:
            messages.error(request, "You have not rented this vehicle.")
            return redirect('homepage')


        repository = lease.Car_ID
        repository.Is_leased = False  
        repository.save()


        lease.delete()
        logger.info(f"User {request.user.username} returned vehicle with ID {vehicle_id}.")
        messages.success(request, f"You have successfully returned the vehicle: {vehicle_id}.")
        
        return redirect('homepage')

    return redirect('homepage')