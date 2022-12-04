import json


def reload_database(user_id: int = None):
    user_id = str(user_id)
    with open("database.json") as f:
        data = json.load(f)
    if not user_id:
        usr_data = {"crypto": {"setup": False, "coins": {}, "notifications": 0}, "menu": 0}
        menu_state = 0
    else:
        if user_id not in data:
            data[user_id] = {"crypto": {"setup": False, "coins": {}, "notifications": 0}, "menu": 0}
            with open("database.json", "w") as file:  # write new price values to file
                json.dump(data, file)
        usr_data = data[user_id]
        menu_state = usr_data["menu"]

    return menu_state, usr_data


def save_to_database(menu_state, usr_data, user_id: int = None):
    user_id = str(user_id)
    with open("database.json") as f:
        data = json.load(f)
    data[user_id] = usr_data
    data[user_id]["menu"] = menu_state
    with open("database.json", "w") as file:  # write new price values to file
        json.dump(data, file, indent=6)
