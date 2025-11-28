from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import post_review
import os
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request) # Terminate user session
    data = {"userName":""} # Return empty username
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username, 
            first_name=first_name, 
            last_name=last_name,
            password=password, 
            email=email
        )
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

def get_cars(request):
    """
    Hàm lấy danh sách xe và populate dữ liệu nếu cần.
    """
    count = CarMake.objects.filter().count()
    print(f"Total Car Makes: {count}")

    if(count == 0):
        initiate()
        print("Database populated with initial data.")

    car_models = CarModel.objects.select_related('car_make')
    cars = []

    for car_model in car_models:
        # Lưu ý: Cú pháp này yêu cầu CarModel phải có thuộc tính car_make là đối tượng CarMake
        cars.append(
            {
                "CarModel": car_model.name,
                "CarMake": car_model.car_make.name
            }
        )

    return JsonResponse({"CarModels":cars})

#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
BASE_DIR = settings.BASE_DIR
DATA_FILE_PATH = os.path.join(
    BASE_DIR, 'database', 'data', 'dealerships.json'
)

# Giữ tên hàm là get_dealerships theo lựa chọn của bạn
def get_dealerships(request, state="All"):

    try:
        # 1. Đọc toàn bộ dữ liệu từ file JSON
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Lấy danh sách đại lý từ khóa 'dealerships'
        all_dealers = data['dealerships']

        # 3. Lọc theo trạng thái (state)
        if state == "All":
            dealerships_list = all_dealers
        else:
            # Lọc danh sách theo state (sử dụng trường 'st' hoặc 'state' trong JSON)
            dealerships_list = [
                dealer for dealer in all_dealers
                if dealer.get('st') == state or dealer.get('state') == state
            ]

            # 4. Trả về kết quả
        return JsonResponse({"status": 200, "dealers": dealerships_list}, safe=False)

    except FileNotFoundError:
        return JsonResponse(
            {"error": f"Dealerships data file not found at {DATA_FILE_PATH}"},
            status=404
        )
    except Exception as e:
        return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)


# Create a `get_dealer_reviews` view to render the reviews of a dealer
# trong server/djangoapp/views.py
# (Sử dụng lại các import đã có: json, JsonResponse, os, settings, BASE_DIR)

def get_dealer_reviews(request, dealer_id):
    try:
        # 1. Định nghĩa đường dẫn tuyệt đối đến file reviews.json
        REVIEWS_FILE_PATH = os.path.join(
            settings.BASE_DIR, 'database', 'data', 'reviews.json'
        )

        # 2. Đọc toàn bộ dữ liệu từ file JSON
        with open(REVIEWS_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 3. Lấy danh sách đánh giá từ khóa 'reviews'
        all_reviews = data['reviews']

        # 4. Lọc các bài đánh giá theo dealer_id
        # Chú ý: Trường 'dealership' trong JSON là số nguyên (15, 23, 29),
        # nên chúng ta so sánh với dealer_id (cũng là số nguyên).
        dealer_reviews = [
            review for review in all_reviews
            if review.get('dealership') == dealer_id
        ]

        # 5. Trả về kết quả
        return JsonResponse({"status": 200, "reviews": dealer_reviews}, safe=False)

    except FileNotFoundError:
        return JsonResponse({"error": "Reviews data file not found"}, status=404)
    except Exception as e:
        return JsonResponse(
            {"error": f"Error processing reviews: {str(e)}"},
            status=500
        )



# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    try:
        # Đường dẫn file JSON
        DATA_FILE_PATH = os.path.join(
            settings.BASE_DIR, 'database', 'data', 'dealerships.json'
        )
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_dealers = data['dealerships']

        # Tìm đại lý theo ID
        dealer_obj = next((d for d in all_dealers if d['id'] == dealer_id), None)

        if dealer_obj:
            # CHÚ Ý: Frontend mong đợi một MẢNG đại lý
            return JsonResponse({"status": 200, "dealer": [dealer_obj]}, safe=False)
        else:
            return JsonResponse({"error": "Dealer not found"}, status=404)

    except FileNotFoundError:
        return JsonResponse({"error": "Dealerships data file not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)


# Create a `add_review` view to submit a review
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})


DATA_FILE_PATH = os.path.join(
    BASE_DIR, 'database', 'data', 'dealerships.json'
)


@csrf_exempt
def post_review(request):
    if request.method == 'POST':
        try:
            # 1. Định nghĩa đường dẫn file reviews.json
            REVIEWS_FILE_PATH = os.path.join(
                settings.BASE_DIR, 'database', 'data', 'reviews.json'
            )

            # 2. Đọc dữ liệu hiện có
            with open(REVIEWS_FILE_PATH, 'r', encoding='utf-8') as f:
                reviews_data = json.load(f)

            # 3. Nhận dữ liệu đánh giá mới từ request
            new_review_data = json.loads(request.body)

            # *** ĐIỀU CHỈNH KIỂU DỮ LIỆU ***
            # Ép kiểu dealer_id từ chuỗi (từ Frontend) sang số nguyên (để khớp với reviews.json)
            if new_review_data.get('dealership'):
                new_review_data['dealership'] = int(new_review_data['dealership'])

            # 4. Gán ID mới (ID bằng ID lớn nhất hiện tại + 1)
            all_reviews = reviews_data.get('reviews', [])
            new_id = max([r.get('id', 0) for r in all_reviews]) + 1
            new_review_data['id'] = new_id

            # 5. Thêm đánh giá mới vào danh sách
            all_reviews.append(new_review_data)
            reviews_data['reviews'] = all_reviews

            # 6. Ghi lại toàn bộ dữ liệu vào file JSON
            with open(REVIEWS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(reviews_data, f, ensure_ascii=False, indent=4)

            print(f"Successfully saved new review (ID: {new_id}) for dealer ID {new_review_data.get('dealership')}")
            return JsonResponse({"status": 200, "message": "Review submitted and saved successfully"}, status=200)

        except Exception as e:
            print(f"Error during post_review: {e}")
            return JsonResponse({"error": f"Failed to submit review: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
