import json


def reload_database(user_id=None):
    # TODO user id
    with open("database.json") as f:
        data = json.load(f)
    menu_state = data["menu"]
    return menu_state, data


def save_to_database(menu_state, data):
    data["menu"]= menu_state
    with open("database.json", "w") as file:  # write new price values to file
        json.dump(data, file)

