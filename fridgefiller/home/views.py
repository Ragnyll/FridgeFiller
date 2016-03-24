from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from lists.models import ShoppingList, UserProfile, Pantry
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

        # get the things in your pantry that will expire in < 1 week
        try:
            pantry_items = Pantry.objects.get(pantry_items=self.request.items)
                    
        except:
            pass
        return context

