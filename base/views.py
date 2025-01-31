from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ShoppingList
from django.contrib.auth.models import User

# To track user's deletion confirmation state (using a global variable for simplicity)
user_confirmation_state = {}

@csrf_exempt
def handle_whatsapp_message(request):
    # Get the message from the request
    incoming_msg = request.POST.get('Body', '').lower()

    # Initialize a Twilio MessagingResponse object
    response = MessagingResponse()

    # If user is authenticated, use request.user. If not, set it to None
    user = request.user if request.user.is_authenticated else None  # Leave user as None for anonymous users

    # Fetch the phone number of the sender
    sender_number = request.POST.get('From')

    # Check if the user is awaiting confirmation for deletion
    if sender_number in user_confirmation_state and user_confirmation_state[sender_number] == "awaiting_deletion_confirmation":
        if 'yes' in incoming_msg:
            # Proceed with deleting all items from the shopping list
            ShoppingList.objects.all().delete()
            response.message("Your shopping list has been cleared.")
            # Reset the confirmation state after the action
            del user_confirmation_state[sender_number]
        elif 'no' in incoming_msg:
            response.message("Deletion cancelled. Your shopping list is safe.")
            # Reset the confirmation state after cancellation
            del user_confirmation_state[sender_number]
        else:
            response.message("Please reply with 'yes' to confirm deletion or 'no' to cancel.")

    else:
        # Command: Add item
        if 'add' in incoming_msg:
            parts = incoming_msg.split(" ", 2)  # ['add', '3', 'packs of milk']
            
            if len(parts) >= 3:
                quantity = parts[1]  # Get the quantity
                item = parts[2]  # Get the item
                
                # Save the item to the database, leave user as None if anonymous
                shopping_item = ShoppingList.objects.create(
                    user=user,  
                    item=item,
                    quantity=quantity
                )
                
                response.message(f"Added {quantity} ({item}) to your shopping list!")
            else:
                # If no quantity is specified, default it to 1
                parts = incoming_msg.split(" ", 1)
                if len(parts) >= 2:
                    item = parts[1]
                    quantity = '1'  # Default to 1 if no quantity is specified

                    # Save the item with default quantity
                    shopping_item = ShoppingList.objects.create(
                        user=user,  
                        item=item,
                        quantity=quantity
                    )

                    response.message(f"Added 1 ({item}) to your shopping list!")
                else:
                    response.message("Invalid format. Please try: add <quantity> <item>")
        
        # Command: Show list
        elif 'show list' in incoming_msg:
            shopping_items = ShoppingList.objects.all()
            items = [f" - x{item.quantity} {item.item}" for item in shopping_items]
            list_message = "\n".join(items) if items else "Your shopping list is empty."
            response.message(f"Here is your shopping list:\n{list_message}")
        
        # Command: Delete item
        elif 'delete' in incoming_msg:
            item_to_delete = incoming_msg.replace('delete', '').strip()

            if item_to_delete:
                deleted_items = ShoppingList.objects.filter(item__icontains=item_to_delete)  # Case-insensitive match
                
                if deleted_items.exists():
                    deleted_items.delete()
                    response.message(f"Deleted {item_to_delete} from your shopping list.")
                else:
                    response.message(f"Could not find {item_to_delete} in your shopping list.")
            else:
                response.message("Please specify an item to delete. Try: delete <item>")

        # Command: Clear list with confirmation
        elif 'clear list' in incoming_msg:
            # Ask for confirmation to clear the list
            user_confirmation_state[sender_number] = "awaiting_deletion_confirmation"
            response.message("Are you sure you want to clear your shopping list? Type 'yes' to confirm, or 'no' to cancel.")

        # Command: Help command to display available commands
        elif 'help' in incoming_msg:
            help_message = (
                "Here are the available commands:\n"
                "- add <quantity> <item>: Add an item to your shopping list\n"
                "- show list: View all items in your shopping list\n"
                "- delete <item>: Delete an item from your shopping list\n"
                "- clear list: Clear your entire shopping list (requires confirmation)\n"
                "- help: Display this help message"
            )
            response.message(help_message)

        else:
            response.message("Sorry, I didn’t understand that command.")

    # Return the response to Twilio
    return HttpResponse(str(response), content_type='application/xml')
