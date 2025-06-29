import io
import PIL.Image
import PIL.ImageFile
import requests
import base64
import json


def username_to_mc_uuid(username) -> str | None:
    """Takes the Minecraft username as an argument and returns the user's UUID as `str`
    or `None` if such username was not found"""
    username_check_url = 'https://api.mojang.com/users/profiles/minecraft/'
    
    request_url = f"{username_check_url}{username}" # TODO: Implement caching at this stage
    response = requests.get(url=request_url).json() # request the uuid 
    
    return response.get('id') # return the id or None if there is no such


def get_minecraft_skin_url(uuid) -> str | None:
    profile_info_get_url = 'https://sessionserver.mojang.com/session/minecraft/profile/'
    
    request_url = f"{profile_info_get_url}{uuid}" # TODO: Implement caching at this stage
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


def create_pfp(uuid: str) -> bytes:
    """A function that creates a Minecraft profile picture.

    Args:
        uuid (str): The Minecraft UUID string.

    Returns:
        bytes: Bytes representing the profile picture.
    """

    mc_skin_link = get_minecraft_skin_url(uuid)
    
    # Get the raw skin data and convert it
    mc_skin_bytes = io.BytesIO(
        requests.get(mc_skin_link).content
        )

    # Open it as an ImageFile object
    mc_skin = PIL.Image.open(mc_skin_bytes)
    pfp_layer_1 = mc_skin.crop((8, 8, 16, 16))
    pfp_layer_2 = mc_skin.crop((40, 8, 48, 16))
    
    # Compose the pfp
    pfp_final = PIL.Image.alpha_composite(pfp_layer_1, pfp_layer_2)
    
    # Convert to bytes
    pfp_byte_array = io.BytesIO() # Create a byte array that will store the file
    pfp_final.save(pfp_byte_array, format='PNG') # Save the PFP into that byte array

    return pfp_byte_array.getvalue() # Get the value (bytes) from that array and return it
