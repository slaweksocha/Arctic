# Dane do MSSQL
Server = 'SWALTUMARCTIC2\ALTUM'
DataBase = 'arctic_seafood_gmbh'
User = 'sa'
Password = '5%$9Gqs&7XT9z*ZRm$wa'

#webhook
webhook_url = 'https://milarex.webhook.office.com/webhookb2/3b8a292d-67e2-427b-a66f-679ad5e6c890@35f0bfd2-54a7-4a76-bad8-f169d5d01bb9/IncomingWebhook/637ace825c2c4076bfe859b6453df008/e3a88a78-1cb7-4736-8c35-ee5fb08071e5'

#Graph folder ID
driveID = 'b!kxF0fAkRRUOcJzSUIuqGzAYqX9q36DVDgQc-EvmRkW-ail_2LRrnQLQKmhaow8Zk'
# lidl_folderID = '014ESGVDCDPQ5V2V4KPZAIXWTMGYI4RP45'
# norma_folderID = '014ESGVDGHAWNT4ZZEENDKDQD3OYYHFTE6'
# kaufland_folderID = '014ESGVDB4ANY4HFF33VFZ5DSYKZH4EAIS'
# aldi_nord_folderID_list = ['014ESGVDDKM6YTMDZ7DNAITEONLTKQSOYL', '014ESGVDHCAJ2QLKDRENC2NLDFMVWWY27B', '014ESGVDECL5JLVXE54ZCI2DBJ3ESF4EMM',
#                            '014ESGVDDAQQPMSJS7IZCZ2ZGXUTEVYHLQ', '014ESGVDCXO6HF5UUIDNH2JIWCZOBRO5RI', '014ESGVDFNCFTHTTK5ZBD3FSS6F2J4CMPB']
# aldi_sued_folderID = '014ESGVDED7HHLOMG73ZCID6IZMH57WQR2'
# hoferAT_folderID = '014ESGVDBA62TQVHCAVZEYAGQEYJIFCR34'
# aldi_uk_folderID = '014ESGVDBKPK2QHDGQDZGKM76SIBCBFAVX'
#słownik z kontrahentami
kontahents = {
    'aldi_sued': {
    'name': 'Aldi SE & Co.KG Mülheim ',
    'folderID_list': ['014ESGVDED7HHLOMG73ZCID6IZMH57WQR2'],
    'backupID': '014ESGVDHG3MNEPGYTIJBJFOCVXYLJVY2T',
    'extract_data': 'extract_data_aldi_sued'
    },
    'aldi_nord': {
    'name': 'Aldi SE & Co.KG Mülheim ',
    'folderID_list': ['014ESGVDDKM6YTMDZ7DNAITEONLTKQSOYL', '014ESGVDHCAJ2QLKDRENC2NLDFMVWWY27B', '014ESGVDECL5JLVXE54ZCI2DBJ3ESF4EMM',
                    '014ESGVDDAQQPMSJS7IZCZ2ZGXUTEVYHLQ', '014ESGVDCXO6HF5UUIDNH2JIWCZOBRO5RI', '014ESGVDFNCFTHTTK5ZBD3FSS6F2J4CMPB'],
    'backupID': '014ESGVDDGXOELDZSEFRAIQNSREGK5WAQC',
    'extract_data': 'extract_data_aldi_nord'
    },
    'kaufland': {
    'name': 'Kaufland Dienstleistung GmbH & Co.KG',
    'folderID_list': ['014ESGVDHSBODURC2AGNBZC56GDV66JDRN'],
    'backupID': '014ESGVDAXVCYACKLXRNBZ7ZHKIBJ2B6LP',
    'extract_data': 'extract_data_kaufland'
    },
    'lidl': {
    'name': 'LIDL Dienstleistung GmbH & Co. KG',
    'folderID_list': ['014ESGVDCDPQ5V2V4KPZAIXWTMGYI4RP45'],
    'backupID': '014ESGVDBY7EZIEOMN5JCIKS5VEYVWFLAT',
    'extract_data': 'extract_data_lidl'
    },
    'norma': {
    'name': 'NORMA Aichach',
    'folderID_list': ['014ESGVDGHAWNT4ZZEENDKDQD3OYYHFTE6'],
    'backupID': '014ESGVDARECLVFHO7UZD3VDCIZ2YRZGGY',
    'extract_data': 'extract_data_norma'
    },
    'hoferAT': {
    'name': 'Hofer KG Zentraleinkauf',
    'folderID_list': ['014ESGVDBA62TQVHCAVZEYAGQEYJIFCR34'],
    'backupID': '014ESGVDELNAZWP4HU2BHYZXKXBIXHYA6Y',
    'extract_data': 'extract_data_hoferAT'
    }
    # 'markant':{
    # 'name': 'Kaufland Dienstleistung GmbH & Co.KG',
    # 'folderID_list': ['014ESGVDB4ANY4HFF33VFZ5DSYKZH4EAIS'],
    # 'backupID': '014ESGVDELNAZWP4HU2BHYZXKXBIXHYA6Y',
    # 'extract_data': 'extract_data_markant'
    # }
}
# for i, value in kontahents.items():
#     if value['extract_data'] == 'extract_data_hoferAT':
#         print(value['extract_data'])
#graph backup folder ID
# aldi_nord_backup_folderID = '014ESGVDDGXOELDZSEFRAIQNSREGK5WAQC'
# aldi_sued_backup_folderID = '014ESGVDHG3MNEPGYTIJBJFOCVXYLJVY2T'
# kaufland_backup_folderID = '014ESGVDAXVCYACKLXRNBZ7ZHKIBJ2B6LP'
# norma_backup_folderID = '014ESGVDARECLVFHO7UZD3VDCIZ2YRZGGY'
# lidl_backup_folderID = '014ESGVDBY7EZIEOMN5JCIKS5VEYVWFLAT'
# hoferAT_backup_folderID = '014ESGVDELNAZWP4HU2BHYZXKXBIXHYA6Y'
# aldi_uk_backup_folderID = '014ESGVDG7NBWTAWISBZC3VSBGDAWLPBP2'



