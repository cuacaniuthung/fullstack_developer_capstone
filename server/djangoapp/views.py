from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import json
import os

from .models import CarMake, CarModel
from .populate import initiate

# ================= LOGGER =================
logger = logging.getLogger(__name__)


# ================= LOGIN =================
@csrf_exempt
def login_user(request):
    """Handle user login."""
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    response_data = {"userName": username}

    if user is not None:
        login(request, user)
        response_data["status"] = "Authenticated"

    return JsonResponse(response_data)


# ================= LOGOUT =================
def logout_request(request):
    """Handle user logout."""
    logout(request)
    return JsonResponse({"userName": ""})


# ================= REGISTRATION =================
@csrf_exempt
def registration(request):
    """Handle user registration."""
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    try:
        User.objects.get(username=username)
        return JsonResponse({
            "userName": username,
            "error": "Already Registered"
        })
    except User.DoesNotExist:
        logger.debug("%s is a new user", username)

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        email=email
    )

    login(request, user)
    return JsonResponse({
        "userName": username,
        "status": "Authenticated"
    })


# ================= CARS =================
def get_cars(request):
    """Return car models list and populate DB if empty."""
    count = CarMake.objects.count()
    logger.debug("Total Car Makes: %s", count)

    if count == 0:
        initiate()
        logger.info("Database populated with initial data.")

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {
            "CarModel": car.name,
            "CarMake": car.car_make.name
        }
        for car in car_models
    ]

    return JsonResponse({"CarModels": cars})


# ================= DEALERSHIPS =================
BASE_DIR = settings.BASE_DIR
DEALERSHIP_FILE_PATH = os.path.join(
    BASE_DIR, 'database', 'data', 'dealerships.json'
)


def get_dealerships(request, state="All"):
    """Return dealerships, filtered by state if provided."""
    try:
        with open(DEALERSHIP_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_dealers = data['dealerships']

        if state == "All":
            dealerships_list = all_dealers
        else:
            dealerships_list = [
                dealer for dealer in all_dealers
                if dealer.get('st') == state or dealer.get('state') == state
            ]

        return JsonResponse({
            "status": 200,
            "dealers": dealerships_list
        }, safe=False)

    except FileNotFoundError:
        return JsonResponse({
            "error": f"Dealership file not found at {DEALERSHIP_FILE_PATH}"
        }, status=404)

    except Exception as error:
        return JsonResponse({
            "error": f"Error processing request: {error}"
        }, status=500)


# ================= DEALER REVIEWS =================
def get_dealer_reviews(request, dealer_id):
    """Return reviews of a specific dealer."""
    reviews_file_path = os.path.join(
        settings.BASE_DIR, 'database', 'data', 'reviews.json'
    )

    try:
        with open(reviews_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_reviews = data['reviews']

        dealer_reviews = [
            review for review in all_reviews
            if review.get('dealership') == dealer_id
        ]

        return JsonResponse({
            "status": 200,
            "reviews": dealer_reviews
        }, safe=False)

    except FileNotFoundError:
        return JsonResponse({"error": "Reviews file not found"}, status=404)
    except Exception as error:
        return JsonResponse({
            "error": f"Error processing reviews: {error}"
        }, status=500)


# ================= DEALER DETAILS =================
def get_dealer_details(request, dealer_id):
    """Return details of a dealer by ID."""
    try:
        with open(DEALERSHIP_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)

        all_dealers = data['dealerships']
        dealer_obj = next(
            (dealer for dealer in all_dealers if dealer['id'] == dealer_id),
            None
        )

        if dealer_obj:
            return JsonResponse({
                "status": 200,
                "dealer": [dealer_obj]
            }, safe=False)

        return JsonResponse({"error": "Dealer not found"}, status=404)

    except FileNotFoundError:
        return JsonResponse({"error": "Dealership file not found"}, status=404)
    except Exception as error:
        return JsonResponse({
            "error": f"Error processing request: {error}"
        }, status=500)


# ================= ADD REVIEW =================
@csrf_exempt
def add_review(request):
    """Submit review if user is authenticated."""
    if request.user.is_anonymous:
        return JsonResponse({
            "status": 403,
            "message": "Unauthorized"
        })

    data = json.loads(request.body)

    try:
        _ = save_review_to_file(data)
        return JsonResponse({"status": 200})
    except Exception as error:
        return JsonResponse({
            "status": 401,
            "message": f"Error posting review: {error}"
        })


# ================= SAVE REVIEW =================
def save_review_to_file(new_review_data):
    """Save a new review into reviews.json file."""
    reviews_file_path = os.path.join(
        settings.BASE_DIR, 'database', 'data', 'reviews.json'
    )

    with open(reviews_file_path, 'r', encoding='utf-8') as file:
        reviews_data = json.load(file)

    if new_review_data.get('dealership'):
        new_review_data['dealership'] = int(new_review_data['dealership'])

    all_reviews = reviews_data.get('reviews', [])
    new_id = max([rev.get('id', 0) for rev in all_reviews], default=0) + 1
    new_review_data['id'] = new_id

    all_reviews.append(new_review_data)
    reviews_data['reviews'] = all_reviews

    with open(reviews_file_path, 'w', encoding='utf-8') as file:
        json.dump(reviews_data, file, ensure_ascii=False, indent=4)

    logger.info(
        "Saved new review ID %s for dealer %s",
        new_id,
        new_review_data.get('dealership')
    )

    return True
