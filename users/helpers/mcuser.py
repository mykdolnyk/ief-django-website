import requests
import base64
import json


def username_to_mc_uuid(username) -> str | None:
    """Takes the Minecraft username as an argument and returns the user's UUID as `str`
    or `None` if such username was not found"""
    username_check_url = 'https://api.mojang.com/users/profiles/minecraft/'
    
    request_url = f"{username_check_url}{username}"
    response = requests.get(url=request_url).json() # request the uuid 
    
    return response.get('id') # return the id or None if there is no such


def get_minecraft_skin_url(uuid) -> str | None:
    skin_get_url = 'https://sessionserver.mojang.com/session/minecraft/profile/'
    
    request_url = f"{skin_get_url}{uuid}"
    response = requests.get(url=request_url) # request info about the account
    
    if response.status_code == 400:
        # if the error is received
        raise ValueError('Given Minecraft UUID does not exist.')
    
    response = response.json() # convert the response to json
    value_encoded = response.get('properties')[0].get('value') # get the value that has the skin url
    value = json.loads(base64.b64decode(value_encoded)) # decode the value and parse it into json

    try:
        url = value.get('textures').get('SKIN').get('url') # get the skin url
    except ValueError:
        url = None # or None if the user has no custom skin
    
    return url
