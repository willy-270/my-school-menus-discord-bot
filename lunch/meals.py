from datetime import datetime
from my_school_menus.api import Menus
import json
from .consts import DISTRICT_ID, LUNCH_MENU_ID, BREAKFAST_MENU_ID


class Meal:
    def __init__(self, desc: str, date: datetime):
        self.desc = desc
        self.date = date

class Month_Menu:
    def __init__(self, is_lunch: bool):
        self.is_lunch = is_lunch
        self.menu_month_raw = self.get_month_raw(self.is_lunch)
        self.meals = self.get_meals()

    def get_meals(self):
        meals = []

        for entry in self.menu_month_raw:
            if entry is None:
                continue
            description = ''
            summary = ''
            recipe_count = 0
            category_count = 0
            try:
                for item in json.loads(entry['setting'])['current_display']:
                    if item['type'] == 'recipe' and recipe_count == 0:
                        recipe_count += 1
                        summary = f"Lunch: {item['name']}"
                    if item['type'] == 'category' and category_count == 0:
                        category_count += 1
                        description = f"{description}{item['name']}:\n"
                    elif item['type'] == 'category':
                        description = f"{description}\n{item['name']}:\n"
                    else:
                        description = f"{description}{item['name']}\n"
                if summary == '':
                    continue
            except KeyError:
                continue

            meal = Meal(description, datetime.fromisoformat(entry['day']).date())
            meals.append(meal)
        
        return meals
    
    def get_month_raw(self, lucnh: bool):
        menus = Menus()

        if lucnh is True:
            menu = menus.get(district_id=DISTRICT_ID, menu_id=LUNCH_MENU_ID)
        else:
            menu = menus.get(district_id=DISTRICT_ID, menu_id=BREAKFAST_MENU_ID)

        menu_month_calendar = menu['data']['menu_month_calendar']
        return menu_month_calendar

def get_todays_meal(is_lunch: bool):
    menu = Month_Menu(is_lunch)

    for meal in menu.meals:
        if meal.date == datetime.now().date():
            return meal
        
    return None

def get_meal_by_date(date, is_lunch: bool) -> Meal:
    menu = Month_Menu(is_lunch)

    for meal in menu.meals:
        if meal.date == date:
            return meal
        
    return None


