import time

import requests
from config_files.graph import get_access_token
from config_files.config import driveID
from config_files.logs import log_add_line
from config_files.move_to_SQL import export_to_SQL
import json
from datetime import datetime
import io
from config_files.all_extracts import extract_data_lidl, extract_data_norma, extract_data_aldi_nord, \
    extract_data_kaufland, extract_data_hoferAT, extract_data_aldi_sued, extract_data_aldi_sued_2, extract_data_lidl_it, \
    extract_data_lidl_rs,extract_data_lidl_fr,extract_data_lidl_nl,extract_data_lidl_at_si_es_lt_cz_int,extract_data_lidl_hr
from config_files.move_to_archive import move_file_to_archive
from config_files.send_webhook import webhook


def check_file(kontarhent_folderID_list, kontrahent_extract_data, kontrahent_name, kontarhent_backup_folderID):
    # ID folderów są w liście: dla każdego elementu..
    for kontarhent_folderID in kontarhent_folderID_list:
        # url do folderu na sharepoincie, pokazujący pliki w środku(children)
        url = f"https://graph.microsoft.com/v1.0/drives/{driveID}/items/{kontarhent_folderID}/children"
        headers = {
            'Authorization': get_access_token()}
        # Make a GET request to the provided url, passing the access token in a header
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # wyszukuje wszystkie pliki w folderze
        files = json.loads(response.content)['value']
        # dla każdego pliku..
        for file in files:
            # pominięcie polderu
            if file.get('folder') is not None:
                print('pomijam folder')
                continue
            elif file.get('name').find('Beleg') != -1 or file.get('name').find('Rechnung') != -1:
                file_id = file.get("id")
                move_file_to_archive(file_id, file.get('name'), kontarhent_backup_folderID)
                continue
            else:
                # url do pliku
                download_url = file.get("@microsoft.graph.downloadUrl")
                # wyciągnięcie nazwy pliku
                pdf_name = file.get("name")
                log_add_line(f'próba przetworzenia pliku:{pdf_name} od {kontrahent_name}')
                # sprawdzenie czy plik jest w formacie pdf
                if pdf_name.endswith('.PDF') or pdf_name.endswith('.pdf'):
                    print(f'file found: {pdf_name}')
                    # obługa wyjątków związanych z połaczeniem Graph
                    for i in range(20):
                        try:
                            response = requests.get(download_url, headers=headers)
                            response.raise_for_status()
                            # wybranie odpowiedniej funkcji wyciągania danych
                            try:
                                if kontrahent_extract_data == 'extract_data_hoferAT':
                                    df = extract_data_hoferAT(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_aldi_sued' and (
                                        pdf_name.find('Attachment') != -1):
                                    df = extract_data_aldi_sued(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_aldi_sued' and (
                                        pdf_name.find('Attachment') == -1):
                                    df = extract_data_aldi_sued_2(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_aldi_nord':
                                    df = extract_data_aldi_nord(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_lidl':
                                    df = extract_data_lidl(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_kaufland':
                                    df = extract_data_kaufland(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_norma':
                                    df = extract_data_norma(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_lidl_it':
                                    df = extract_data_lidl_it(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_lidl_hr':
                                    df = extract_data_lidl_hr(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_lidl_nl':
                                    df = extract_data_lidl_nl(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_lidl_fr':
                                    df = extract_data_lidl_fr(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_lidl_at_si_es_lt_cz_int':
                                    df = extract_data_lidl_at_si_es_lt_cz_int(io.BytesIO(response.content))
                                    break
                                elif kontrahent_extract_data == 'extract_data_lidl_rs':
                                    df = extract_data_lidl_rs(io.BytesIO(response.content))
                                    break
                                # if kontrahent_extract_data == 'extract_data_markant':
                                #     df = extract_data_markant(io.BytesIO(response.content))
                                # df = dd(io.BytesIO(response.content))
                                if len(df) == 0:
                                    # If no tables were found, skip the file
                                    print(f"No tables found in {pdf_name}, skipping...")
                                    continue
                            except Exception as e:
                                # If an error occurs during table extraction, skip the file
                                print(f"Error extracting tables from {pdf_name}: {e}")
                                continue
                        except requests.exceptions.HTTPError as http:
                            print(f'error: {http}')
                            time.sleep(5)
                        except requests.exceptions.SSLError as ssl:
                            print(f'error: {ssl}')
                            time.sleep(5)
                        except requests.exceptions.ConnectionError as con:
                            print(f'error: {con}')
                            time.sleep(5)
                    else:
                        print('Maximum number of retries (20) exceeded. Could not download file.')
                    # wyciąganie daty z pliku
                    extract_date = datetime.strptime(file.get("createdDateTime")[0:10], '%Y-%m-%d').strftime('%d.%m.%Y')
                    # wyliczenie sumy z columny Document_Value
                    extract_sum = df.iloc[:, 2].sum()
                    # wyciągnięcie ID pliku
                    file_id = file.get("id")
                    # SQL
                    export_to_SQL(df, extract_date, extract_sum, kontrahent_name, pdf_name)
                    # Archive
                    move_file_to_archive(file_id, pdf_name, kontarhent_backup_folderID)
                    # webhook
                    webhook(pdf_name, extract_date, kontrahent_name)
