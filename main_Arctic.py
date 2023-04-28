from config_files.config import kontahents
from config_files.files_check import check_file

def run():
    # sprawdz każdą pozycje w słowniku kontrahents
    for i, value in kontahents.items():
        kontarhent_folderID_list = value['folderID_list']
        kontrahent_extract_data = value['extract_data']
        kontrahent_name = value['name']
        kontarhent_backup_folderID = value['backupID']
        try:
            #odpal skrypt sprawdzający czy są pliki w folderze
            check_file(kontarhent_folderID_list, kontrahent_extract_data, kontrahent_name, kontarhent_backup_folderID)

        except TypeError as e:
            #obsługa błędu pustego folderu
            print(f'pusto. błaD:{e}')
            continue

run()