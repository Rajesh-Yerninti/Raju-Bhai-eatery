from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic

app = FastAPI()

inprogress_orders = {}
@app.get("/")
def home():
    return {
        "status": "API is running",
        "message": "Welcome to Raju Bhai Eatery API"
    }
@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = generic.extract_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        "track.order - context: ongoing-tracking": track_order,
        "order.add - context: ongoing-order": add2order,
        "order.remove - context: ongoing-order":remove_from_order,
        "order.complete - context: ongoing-order": complete_order,
        "new.order":new_order
    }
    if intent =="track.order - context: ongoing-tracking":
        return intent_handler_dict[intent](parameters)
    return intent_handler_dict[intent](parameters, session_id)

def new_order(parameters:dict,session_id: str):
    if session_id in inprogress_orders:
        del inprogress_orders[session_id]
def save_to_db(order:dict):
    next_order_id = db_helper.get_next_order_id()
    for food_item , quantity in order.items():
        recode=db_helper.insert_order_item(food_item, quantity, next_order_id )
        if recode==-1:
            return -1
    db_helper.insert_order_tracking(next_order_id,"in progress")
    return next_order_id

def complete_order(parameters:dict,session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text=f"I'm having trouble finding your order. Try again later."
    else:
        order=inprogress_orders[session_id]
        order_id=save_to_db(order)

        if order_id==-1:
            fulfillment_text="Sorry! I couldn't process your order."  \
                              "Please place new order again."
        else:
            order_total=db_helper.get_total_order_price(order_id)
            fulfillment_text=f"Awesome! we have placed your order."\
                            f"here is your order ID: {order_id}"\
                            f"Your order total is {order_total} which you can pay at the time of delivery"
        del inprogress_orders[session_id]
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
def add2order(parameters: dict, session_id: str):
    food_items = parameters['food-item']
    quantities = parameters['number']
    if len(food_items) != len(quantities):
        fullfillment_text = f"Sorry! The number of food items and quantities provided are not the same"
    else:
        new_food_dict=dict(zip(food_items, quantities))
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict
        order_str=generic.get_str_from_food_dict(inprogress_orders[session_id])
        fullfillment_text =f"so far you have {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fullfillment_text
    })
#inprogress_orders={
#session_id_1': {"pizza": 2, "mango lassi": 1},
#session_id_2': {"chole": 5, "vada pav": 3, "mango lassi": 1}
#}

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText":"I'm having trouble finding your order. Try again later."
        })
    current_order=inprogress_orders[session_id]
    food_items = parameters['food-item']

    removed_items=[]
    not_found_items=[]
    for item in food_items:
        if item not in current_order:
            not_found_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]
    if len(removed_items)>0:
        fulfillment_text=f"Removed {''.join(removed_items)} from your order"
    if len(not_found_items)>0:
        fulfillment_text=f"Your current order does not have{''.join(not_found_items)} items"
    if len(current_order.keys())==0:
        fulfillment_text+="Your order is empty"
    else:
        order_str=generic.get_str_from_food_dict(current_order)
        fulfillment_text+=f"here is what is left in your order: {order_str}. Anything else?"

    return JSONResponse(content={
        "fulfillment_text":fulfillment_text
    })

def track_order(parameters: dict):
    order_id = int(parameters['orderId'])
    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
#4 biryani, 2 Mango lassi, 4 coke, 3 pizza, 1 masala dosa, one vada pav, two rava dosa, 5 samo hhjsa and three bhaji
