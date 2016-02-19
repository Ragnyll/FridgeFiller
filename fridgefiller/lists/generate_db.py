
import sys, os
file_path = __file__

app_loc = os.path.dirname(os.path.abspath(file_path))
sys.path.append(app_loc)

setting_loc = os.path.join(os.path.join(os.path.dirname(app_loc), "fridgefiller"), "settings.py")

print setting_loc

os.environ['DJANGO_SETTINGS_MODULE'] = setting_loc

from django.conf import settings

settings.configure()

import django
django.setup()

from django.contrib.auth.models import User
from models import UserProfile, Party, ShoppingList, Pantry, Item, ItemDetail

# pre: The database is empty
# post: fills up the database with model entries
def generate_db():
    codex_u = User.objects.create(username="codex", first_name="Cyd")
    zaboo_u = User.objects.create(username="zaboo", first_name="Sujan")
    tink_u = User.objects.create(username="tinkerballa", first_name="April")
    vork_u = User.objects.create(username="vork", first_name="Herman")
    bladezz_u = User.objects.create(username="bladezz", first_name="Simon")
    clara_u = User.objects.create(username="clara", first_name="clara")
    
    users = [codex_u, zaboo_u, tink_u, vork_u, bladezz_u, clara_u]

    codex_up = UserProfile.objects.get(name="codex")
    codex_up.description = "timid, priest"
    
    zaboo_up = UserProfile.objects.get(name="zaboo")
    zaboo_up.description = "annoying, warlock"

    tink_up = UserProfile.objects.get(name="tinkerballa")
    tink_up.description = "entitled, ranger"

    vork_up = UserProfile.objects.get(name="vork")
    vork_up.description = "cheap and pendantic, warrior"

    bladezz_up = User.objects.create(name="bladezz")
    bladezz_up.description = "immature, rogue"

    clara_up = User.objects.create(name="clara")
    clara_up.description = "mother, mage"

    user_profiles = [codex_up, zaboo_up, tink_up, vork_up, bladezz_up, clara_up]
    for i in user_profiles:
        i.save()

    p = Party.objects.create(name="Knights Of Good")
    p.owner = vork_up
    for i in [codex_up, zaboo_up, tink_up, bladezz_up, clara_up]:
        p.users.add(i)

    shoplist = ShoppingList.objects.create(name="Raid Potions", owner=codex_up)
    

if __name__ == "__main__":
    print "Generating the database!"
    generate_db()
