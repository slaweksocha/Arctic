from config_files.config import driveID
from datetime import datetime
import requests
from config_files.graph import get_access_token
import json

def move_file_to_archive(file_id, file_name, backup_folderID):
    #url do folderu backup
    url = f"https://graph.microsoft.com/v1.0/drives/{driveID}/items/{backup_folderID}/children"
    headers = {
        'Authorization': get_access_token(),
        "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    children = response.json()["value"]
    # sprawdzenie czy istnieje już folder z dziejszą datą
    for child in children:
        if child["name"] == str(datetime.date(datetime.today())) and child.get("folder") is not None:
            today_folder_id = child["id"]
            break
        else:
            #tworzenie folderu, jeśli go nie ma
            todays_folder = {
                "name": str(datetime.date(datetime.today())),
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            create_todays_folder = requests.post(url, headers=headers, data=json.dumps(todays_folder))
            today_folder_id = json.loads(create_todays_folder.content).get('id')
            break
            # print(today_folder_id)

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
        print("File name changed successfully.")
    else:
        print("Error changing file name:", response.status_code, response.text)
