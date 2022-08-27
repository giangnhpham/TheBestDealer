from urllib import response
from xml.etree.ElementInclude import include
import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth

from .models import CarDealer, DealerReview


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    try:
        api_key = kwargs.get('api_key')
        if api_key:
            params = {key: val for key, val in kwargs.items() if key !=
                      'api_key'}
            response = requests.get(url, headers={
                'Content-Type': 'application/json'}, params=params, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(
                url, headers={'Content-Type': 'application/json'}, params=kwargs)
        status_code = response.status_code
        print("GET {} {}".format(url, status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        print('Network execution occured')
        return {'error': True, 'message': 'Something went wrong'}


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    response = requests.post(url, headers={
                'Content-Type': 'application/json'}, params=kwargs, json=payload)
    status_code = response.status_code
    print("POST {} {}".format(url, status_code))
    if status_code == 200 or status_code == 204:
        return {'ok': True, 'message': 'Complete'}
    else:
        return {'ok': False, 'message': 'Error Occured'}

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    result = []
    state = kwargs.get('state')
    # - Call get_request() with specified arguments
    if state:
        json_result = get_request(url, state=state)
    else:
        json_result = get_request(url)
    print(json_result)
    # - Parse JSON results into a CarDealer object list
    if json_result and not json_result.get('error', False):
        dealers = json_result['payload']
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer['address'], city=dealer['city'], full_name=dealer['full_name'],
                                   id=dealer['id'], lat=dealer['lat'], long=dealer['long'], short_name=dealer['short_name'], st=dealer['st'], zip=dealer['zip'])
            result.append(dealer_obj)
    return result


def get_dealer_by_id_from_cf(url, id):
    # - Call get_request() with specified arguments
    json_result = get_request(url, id=id)
    # - Parse JSON results into a CarDealer object list
    if json_result and not json_result.get('error', False):
        dealer = json_result['payload'][0]
        dealer_obj = CarDealer(address=dealer['address'], city=dealer['city'], full_name=dealer['full_name'],
                               id=dealer['id'], lat=dealer['lat'], long=dealer['long'], short_name=dealer['short_name'], st=dealer['st'], zip=dealer['zip'])
    return dealer_obj


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    result = []
    # - Call get_request() with specified arguments
    json_result = get_request(url, dealer_id=dealer_id)
    # - Parse JSON results into a DealerView object list
    if json_result:
        reviews = json_result['payload']
        for review in reviews:
            sentiment = analyze_review_sentiments(review['review'])
            review_obj = DealerReview(dealership=review['dealership'], name=review['name'], purchase=review['purchase'], purchase_date=review.get('purchase_date', None), review=review['review'], car_make=review.get(
                'car_make', None), car_model=review.get('car_model', None), car_year=review.get('car_year', None), sentiment=sentiment, id=review['id'])
            print(review_obj)
            result.append(review_obj)
    return result


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
def analyze_review_sentiments(text):
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/4582c3d9-c6ab-4793-b0f1-4aa176b93183/v1/analyze"
    api_key = "g_BukOtkvDO3-cI-Uu2PhzvKa4kwDx8kb8kvnc_e09OK"
    # Append extra text for preventing not getting a result
    text_to_analyze = '{} hello hello hello'.format(text)

    # - Call get_request() with specified arguments
    json_response = get_request(url, api_key=api_key, version="2022-04-07",
                                text=text_to_analyze, features='sentiment', return_analyzed_text=True)

    # - Get the returned sentiment label such as Positive or Negative
    return json_response['sentiment']['document']['label']
