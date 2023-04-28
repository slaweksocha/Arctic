from config_files.config import Server, User, Password, DataBase, kontahents
from datetime import datetime
import pyodbc
# from config_files.files_check import check_file
# from config_files.move_to_archive import move_file_to_archive
# from config_files.send_webhook import webhook

def export_to_SQL(df, extract_date, extract_sum,kontrahent_name,pdf_name):
    #ustawienie połączenia SQL
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        f'SERVER={Server};'
        f'DATABASE={DataBase};'
        f'UID={User};'
        f'PWD={Password}'
    )

    cursor = conn.cursor()
    # dodanie do tabeli Header
    cursor.execute('''IF NOT EXISTS (SELECT 1 FROM dbo.Milarex_PaymentAdvice_Header WHERE Payment_Value = ? AND Payment_Customer = ?)
                                INSERT INTO dbo.Milarex_PaymentAdvice_Header (Payment_Date, Payment_Value, Payment_File, Payment_Customer)
                                VALUES (?,?,?,?)
                                ''', extract_sum, kontrahent_name, datetime.strptime(extract_date, '%d.%m.%Y'),
                   extract_sum,
                   pdf_name,
                   kontrahent_name

                   )
    #wyodrębnienie ID z tabeli Header
    cursor.execute("SELECT @@IDENTITY")
    Headerid = cursor.fetchone()[0]
    # dodanie do tabeli Items
    for i, row in df.iterrows():
        cursor.execute('''IF NOT EXISTS (SELECT 1 FROM dbo.Milarex_PaymentAdvice_Item WHERE HeaderId = ? AND Document_Date = ? AND Document_Name =? AND Document_Value = ?)
                                    INSERT INTO dbo.Milarex_PaymentAdvice_Item (HeaderId, Document_Date, Document_Name, Document_Value)
                                    VALUES (?,?,?,?)
                                    ''', Headerid, datetime.strptime(row.Document_Date, '%d.%m.%Y'),
                       row.Document_Name,
                       row.Document_Value, Headerid, datetime.strptime(row.Document_Date, '%d.%m.%Y'),
                       row.Document_Name, row.Document_Value
                       )
    conn.commit()