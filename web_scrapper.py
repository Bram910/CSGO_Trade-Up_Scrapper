import requests
from bs4 import BeautifulSoup as bs
import Case_Skins as cls
from PIL import Image

#region Extracting case link and name

def extract_case_link_name(data):
    """
    Extracts the case link and name from the provided HTML data.

    Parameters:
    data (BeautifulSoup element): The HTML data to extract from.

    Returns:
    tuple: A tuple containing the link and the name of the case.
    """
    return (data.find('a').get('href'), data.find('img').get('alt'))

# Filter out non-case entries and specific unwanted cases
def filter_cases(case_text):
    """
    Filters out entries that are not cases or are unwanted cases.

    Parameters:
    case_text (BeautifulSoup element): The HTML data to filter.

    Returns:
    bool: True if the entry is a valid case, False otherwise.
    """
    img_stat = case_text.find('img') is not None
    if not img_stat:
        return False

    case_name = case_text.find('img').get('alt')
    except_1 = case_name != 'All Skin Cases'
    except_2 = case_name != 'Souvenir Packages'
    except_3 = case_name != 'Gift Packages'

    return except_1 and except_2 and except_3

def extract_data(data):
    """
    Extracts and filters case data from the provided HTML data.

    Parameters:
    data (list): The HTML data to extract from.

    Returns:
    set: A set of tuples containing the link and name of the cases.
    """
    data_filtered = set(filter(filter_cases, data))
    return set(map(extract_case_link_name, data_filtered))

#endregion

def extract_skin_from(URL, ObjCase, text_Var, window):
    """
    Extracts skin information from a given case URL and updates the ObjCase.

    Parameters:
    URL (str): The URL of the case.
    ObjCase (Case): The case object to update.
    text_Var (tkinter.StringVar): The text variable to update the log.
    window (tkinter.Tk): The Tkinter window to update.
    """
    page = requests.get(URL)
    soup = bs(page.content, features='html.parser')

    case_name = soup.find('h1', {'class': 'margin-top-sm'}).text
    skin_boxes = soup.findAll('div', {'class': 'col-lg-4 col-md-6 col-widen text-center'})

    # Skip the first box (usually contains knives, which can't be traded)
    for box in skin_boxes[1:]:
        ObjSkin = cls.Skin()

        # Extract the name and weapon separately
        ObjSkin.weapon = box.find('h3').text.split(" | ")[0]
        ObjSkin.name = box.find('h3').text.split(" | ")[1]
        ObjSkin.rarity = box.find('p', {'class': 'nomargin'}).text.split(' ')[0]
        ObjCase.Skins.append(ObjSkin)

        # Save the skin image for interface use
        image = box.find('img')
        image_url = image['src']
        image_final = Image.open(requests.get(image_url, stream=True).raw)
        image_final.save('Files/Skins/' + ObjSkin.weapon + ' ' + ObjSkin.name + '.png', 'PNG')

        # Log details about the extracted skin
        print_to_log(f'Extracted skin: {ObjSkin.name} | {ObjSkin.weapon} from case: {ObjCase.name}', text_Var, window)

def print_to_log(text, text_Var, window):
    """
    Adds text to the log viewer and updates the Tkinter window.

    Parameters:
    text (str): The text to add to the log.
    text_Var (tkinter.StringVar): The text variable to update the log.
    window (tkinter.Tk): The Tkinter window to update.
    """
    text_Var.set(text_Var.get() + '\n' + text)
    window.update()

def extract_from_cases(URL, text_Var, window):
    """
    Extracts case and skin information from a given URL.

    Parameters:
    URL (str): The URL to extract from.
    text_Var (tkinter.StringVar): The text variable to update the log.
    window (tkinter.Tk): The Tkinter window to update.

    Returns:
    list: A list of extracted case objects.
    """
    page = requests.get(URL)
    soup = bs(page.content, features='html.parser')

    menu = soup.find('div', {'id': 'navbar-expandable'}).find('ul')
    all_buttons = menu.findAll('li', {'class': 'dropdown'})

    ok = 0
    for button in all_buttons:
        menu = button.findAll('a', {'href': '#'})

        # Stop the loop when 'Cases' button is found
        for row in menu:
            if row.contents[0] == 'Cases':
                ok = 1
                break

        if ok == 1:
            break

    elem_menu = button.findAll('li')  # Access list of elements in the dropdown menu
    elem_menu_set = set(elem_menu)

    print_to_log("Menu extraction complete", text_Var, window)

    Cases = []
    for case_Link, case_Name in extract_data(elem_menu_set):
        ObjCase = cls.Case()
        ObjCase.name = case_Link.split('/')[5].replace('-', ' ')
        ObjCase.link = case_Link
        extract_skin_from(ObjCase.link, ObjCase, text_Var, window)
        Cases.append(ObjCase)

    print_to_log("Case extraction complete", text_Var, window)

    return Cases
