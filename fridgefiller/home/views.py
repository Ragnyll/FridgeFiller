from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from lists.models import ShoppingList, UserProfile, Pantry, Item, ItemDetail, Party

from datetime import datetime
from datetime import timedelta

class HomePageView(TemplateView):
    """
    This view displays all the info being used on a users homepage
    """
       
    template_name = 'home/home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        
        # get the most recently accessed list
        try:       
            user = UserProfile.objects.get(user=self.request.user)
            owned_lists = ShoppingList.objects.filter(owners__in=[user])
            most_recent_list = owned_lists.order_by('-updated')
            most_recent_list = most_recent_list[0] 
            context['most_recent_list'] = most_recent_list
        except:
            pass

        # find expired and soon to expire items and add them to the context
        try:
            # these are all the items that are def expired
            expired_items = []
            # these are all the items that will expire in < 1 week
	    warning_items = []
            user_party = Party.objects.get(owner=user)
            user_pantry = Pantry.objects.get(party=user_party)
            user_pantry_items = user_pantry.items.all()
            
            for item_detail in user_pantry_items:
                # a datetime object is constructed instead of using django datetime because django datetime is really strange and wont run timedeltas correctly
                datetime_expiration = datetime(item_detail.expiration_date.year, item_detail.expiration_date.month, item_detail.expiration_date.day, 0, 0)
                
                datetime_current = datetime.now()
                datetime_delta = datetime_expiration - datetime_current
                
                # see if item_detail is expired
                if datetime_delta.days <= 0:
                    expired_items.append(item_detail)
                # see if item_detail will expire in less than a week
                elif datetime_delta.days <= 7:
                    warning_items.append(item_detail)
            
            # stick the two lists into the context dictionary
            context['expired_items'] = expired_items
            context['warning_items'] = warning_items
        except:
            pass

        return context

