from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ShoppingList
from django.contrib.auth.models import User

@csrf_exempt
def handle_whatsapp_message(request):
    # Get the message from the request
    incoming_msg = request.POST.get('Body', '').lower()

    # Initialize a Twilio MessagingResponse object
    response = MessagingResponse()

    # If user is authenticated, use request.user. If not, set it to None
    user = request.user if request.user.is_authenticated else None  # Leave user as None for anonymous users

    # Check if the message contains the "add" command
    if 'add' in incoming_msg:
        # Split the message into parts to extract quantity and item
        parts = incoming_msg.split(" ", 2)  # ['add', '3', 'packs of milk']
        
        # Check if the format is correct (command, quantity, item)
        if len(parts) >= 3:
            quantity = parts[1]
            item = parts[2]
            
            # Save the item to the database, leave user as None if anonymous
            shopping_item = ShoppingList.objects.create(
                user=user,  # Leave as None if no user
                item=item,
                quantity=quantity
            )
            
            response.message(f"Added {quantity} ({item}) to your shopping list!")
        else:
            response.message("Invalid format. Please try: add <quantity> <item>")
    
    # Check if the message contains the "show list" command
    elif 'show list' in incoming_msg:
        # Retrieve all items from the shopping list
        shopping_items = ShoppingList.objects.all()
        items = [f"{item.item} ({item.quantity})" for item in shopping_items]
        list_message = "\n".join(items) if items else "Your shopping list is empty."
        
        response.message(f"Here is your shopping list:\n{list_message}")
    
    else:
        response.message("Sorry, I didn’t understand that command.")
    
    # Return the response to Twilio
    return HttpResponse(str(response), content_type='application/xml')