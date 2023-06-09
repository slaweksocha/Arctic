from config_files.config import driveID
from datetime import datetime
import requests
from config_files.graph import get_access_token
import json
from config_files.logs import log_add_line

def move_file_to_archive(file_id, file_name, backup_folderID):
    #url do folderu backup
    url = f"https://graph.microsoft.com/v1.0/drives/{driveID}/items/{backup_folderID}/children"
    headers = {
        'Authorization': get_access_token(),
        "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    children = response.json()["value"]
    year_folder_id = []
    month_folder_id = []
    today_folder_id = []
    # sprawdzenie czy istnieje już folder z dziejszą datą
    for child in children:
        if child["name"] == str(datetime.now().year) and child.get("folder") is not None:
            year_folder_id = child["id"]
            break
        else:
            year_folder_id = []
            continue
    # tworzenie folderu, jeśli go nie ma
    if year_folder_id == []:
        year_folder = {
            "name": str(datetime.now().year),
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        create_year_folder = requests.post(url, headers=headers, data=json.dumps(year_folder))
        year_folder_id = json.loads(create_year_folder.content).get('id')

    url = f"https://graph.microsoft.com/v1.0/drives/{driveID}/items/{year_folder_id}/children"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    children = response.json()["value"]
    for child in children:
        if child["name"] == str(datetime.now().month) and child.get("folder") is not None:
            month_folder_id = child["id"]
            break
        else:
            month_folder_id = []
            continue

    # tworzenie folderu, jeśli go nie ma
    if month_folder_id == []:
        month_folder = {
            "name": str(datetime.now().month),
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        create_month_folder = requests.post(url, headers=headers, data=json.dumps(month_folder))
        month_folder_id = json.loads(create_month_folder.content).get('id')
    url = f"https://graph.microsoft.com/v1.0/drives/{driveID}/items/{month_folder_id}/children"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    children = response.json()["value"]
    for child in children:
        if child["name"] == str(datetime.now().day) and child.get("folder") is not None:
            today_folder_id = child["id"]
            break
        else:
            today_folder_id = []
            continue
    # tworzenie folderu, jeśli go nie ma
    if today_folder_id == []:
        todays_folder = {
            "name": str(datetime.now().day),
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        create_todays_folder = requests.post(url, headers=headers, data=json.dumps(todays_folder))
        today_folder_id = json.loads(create_todays_folder.content).get('id')

    # url do pliku
    file_url = f"https://graph.microsoft.com/v1.0/drives/{driveID}/items/{file_id}"

    # zmiana w jsonie, która zmieni folder do backupu
    data = {
        "parentReference": {
            "id": today_folder_id
        },
        "name": file_name
    }
    #uruchomienie
    response = requests.patch(file_url, headers=headers, data=json.dumps(data))

    #sprawdzanie połączenia
    if response.status_code == 200:
        log_add_line(f"plik {file_name} przeprocesowany oraz przeniesiony do archiwum")
    else:
        print("Error changing file name:", response.status_code, response.text)
