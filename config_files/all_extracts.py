import tabula
import PyPDF2
import pandas as pd
import re


def extract_data_lidl(pdf_file):
    # użycie tabuli
    df_col = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})
    #jeżeli wartość
    if df_col == []:
        with pdf_file as pdf:
            pdf_reader = PyPDF2.PdfFileReader(pdf)
            # pdf = io.open(pdf_file, 'rb', buffering=0)
            start_marker = 'Beleg'
            end_marker = '_\nÜbertrag'

            intervals = [(0, 7), (9, 25), (26, 36), (37, 55), (56, 68)]

            # Create a PDF reader object
            # pdf_reader = PyPDF2.PdfFileReader(pdf)
            data = []

            for page_num in range(pdf_reader.getNumPages()):
                # Get the page object
                page = pdf_reader.getPage(page_num)

                # Extract the text from the page
                text = page.extract_text()

                # Find the start and end positions of the relevant text
                start_pos = text.find(start_marker)
                end_pos = text.find(end_marker)

                # Extract the relevant text
                relevant_text = text[start_pos:end_pos]

                # Split the text into rows
                rows = relevant_text.split('\n')
                for row in rows:
                    if row.startswith(start_marker) or row.startswith(end_marker):
                        continue
                    row_data = []
                    for interval in intervals:
                        row_data.append(row[interval[0]:interval[1]].strip())
                    data.append(row_data)

            # Create a Pandas DataFrame from the extracted data
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            df = pd.DataFrame(data)
            df = df.rename(columns={1: 'Document_Name', 2: 'Document_Date', 4: 'Document_Value'})
            df = df.drop(columns=[0, 3])
            df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
            df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
            df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3',
                                                              regex=True)
            df = df.drop(df.index[-4:])
            df = df.drop_duplicates()
            df = df.replace(' ', pd.NA).replace('', pd.NA)
            df = df.dropna(how='all')
            df = df.reset_index(drop=True)
            for i, value in enumerate(df['Document_Value']):

                value = value.strip()

                # Check if the string ends with '-' and starts with a number
                if value.endswith('-') and value[0].isdigit():
                    # Swap the positions of the '-' sign and the number using string slicing and concatenation
                    value = '-' + value[:-1]

                    # Update the value in the DataFrame
                    df.at[i, 'Document_Value'] = value

            df = df[['Document_Name', 'Document_Date', 'Document_Value']]
            df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
            df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))

            # print(len(df['Document_Value']))
            return df
    else:
        # łączenie wszystkich DataFrame ze wszystkich stron
        df = pd.concat(df_col)
        # usuwanie wierszy, kiedy jest jakaś pusta pozycja
        df = df.dropna()
        # usuwa duplikaty - nagłówki ze stron
        df = df.drop_duplicates()
        # usuwa nagłówek
        df = df.drop(0)
        #
        df[['temp', 'Document_Name']] = df[0].str.split(' ', n=2, expand=True)
        df = df.drop(columns=[0, 'temp', 2])
        # zmiana nazwy na prowidłową
        df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3', regex=True)

        df = df.rename(columns={1: 'Document_Date', 3: 'Document_Value'})
        df = df.reset_index(drop=True)
        #przeniesienie minusa na początek kwoty
        for i, value in enumerate(df['Document_Value']):

            value = value.strip()

            # Check if the string ends with '-' and starts with a number
            if value.endswith('-') and value[0].isdigit():
                # Swap the positions of the '-' sign and the number using string slicing and concatenation
                value = '-' + value[:-1]

                # Update the value in the DataFrame
                df.at[i, 'Document_Value'] = value
        #ustawienie porządanej kolejności kolumn
        df = df[['Document_Name', 'Document_Date', 'Document_Value']]
        #doprowadzenie kolumny z kwotami do porządanego formatu
        df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
        print(df)
        return df


def extract_data_hoferAT(pdf_file):
    # Use Tabula to extract data from PDF file
    df_col = tabula.read_pdf(pdf_file, encoding="ISO-8859-1", pages='all', multiple_tables=True)[1]
    df = pd.DataFrame(df_col)

    # df = pd.concat(df)

    df = df.rename(
        columns={'Datum': 'Document_Date', 'Ihre Rechnungsnummer': 'Document_Name', 'Betrag': 'Document_Value'})
    df = df.dropna()
    #
    df = df.drop(columns=['Unsere Referenz', 'Währung', 'Skonto'])
    df = df.reset_index(drop=True)
    for i, value in enumerate(df['Document_Value']):

        value = value.strip()

        # Check if the string ends with '-' and starts with a number
        if value.endswith('-') and value[0].isdigit():
            # Swap the positions of the '-' sign and the number using string slicing and concatenation
            value = '-' + value[:-1]

            # Update the value in the DataFrame
            df.at[i, 'Document_Value'] = value

    df = df[['Document_Name', 'Document_Date', 'Document_Value']]
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    # print(df)

    return df


def extract_data_norma(pdf_file):
    df = tabula.read_pdf(pdf_file, pages='all', pandas_options={'header': None})
    df = pd.concat(df)

    df = df.rename(columns={0: 'Document_Name', 1: 'Document_Date', 4: 'Document_Value'})
    df = df.reset_index(drop=True)
    for i, value in enumerate(df['Document_Value']):

        value = value.strip()

        # Check if the string ends with 's' and starts with a number
        if value.endswith(' s') and value[0].isdigit():
            value = '-' + value[:-2]

            # Update the value in the DataFrame
            df.at[i, 'Document_Value'] = value
        else:
            value = value[:-2]
            df.at[i, 'Document_Value'] = value

    df = df.drop(columns=[2, 3, 5])
    df = df.dropna()
    df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    return df

def extract_data_aldi_sued(pdf_file):
    # Use Tabula to extract data from PDF file
    df = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})
    df = pd.concat(df)
    df = df.rename(
        columns={1: 'Document_Date', 2: 'Document_Name', 5: 'Document_Value'})
    df = df.dropna()

    df = df[['Document_Name', 'Document_Date', 'Document_Value']]
    df = df.reset_index(drop=True)
    for i, value in enumerate(df['Document_Value']):
        if value.startswith('Zahlbetrag'):
            df.drop(i, inplace=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR (\d{4}) (\d{2}) (\d{5})$', r'VR/\1/\2/\3', regex=True)
    df = df.reset_index(drop=True)
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    return df

def extract_data_aldi_sued_2(pdf_file):
    df_list = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", guess=True)

    df = df_list[1]
    df = pd.DataFrame(df)
    df = [df]
    df = pd.concat(df)
    df = df.rename(columns={'Datum': 'Document_Date', 'BetragRechnungsnummer': 'Document_Name',
                            'Unnamed: 0': 'Document_Value'})
    df = df.drop(columns=['Ihre Buchungskreis Unsere Referenz', 'Währung', 'Skonto'])
    df = df.dropna()
    df = df.reset_index(drop=True)
    for i, value in enumerate(df['Document_Value']):
        # Remove any whitespace from beginning and end of string
        value = value.strip()

        # Check if the string ends with '-' and starts with a number
        if value.endswith('-') and value[0].isdigit():
            # Swap the positions of the '-' sign and the number using string slicing and concatenation
            value = '-' + value[:-1]

            # Update the value in the DataFrame
            df.at[i, 'Document_Value'] = value
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    print(df)
    return df


def extract_data_kaufland(pdf_file):
    # Use Tabula to extract data from PDF file
    df_col = tabula.read_pdf(pdf_file, pages='all', pandas_options={'header': None}, multiple_tables=True, encoding="ISO-8859-1")
    if df_col == []:
        df = pd.concat(df_col)
        print(df)
        return df
    else:
        df = pd.concat(df_col)
        df[[0, 'Document_Name', 'Document_Date']] = df[0].str.split(' ', n=2, expand=True)
        df = df.drop(columns=[0,2])
        df = df.rename(columns={3: 'Document_Value', 1: 'temp'})
        df = df.drop(0)
        df = df[['Document_Name', 'Document_Date', 'temp', 'Document_Value']]
        df['temp'] = df['temp'].astype(str)
        df['Document_Name'] = df['Document_Name'].astype(str)
        df['Document_Date'] = df['Document_Date'].astype(str)
        for i, row in df.iterrows():
            if re.match('S.', row['Document_Name']):
                df.at[i, 'Document_Name'] = 'S. KOMPENSATION'
                df.at[i, 'Document_Date'] = row['temp']
                df.at[i, 'temp'] = None
        df = df.drop(columns=['temp'])
        df = df.dropna()
        df = df.reset_index(drop=True)
        df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
        # print(df)
        return df

def extract_data_aldi_nord(pdf_file):
    # Use Tabula to extract data from PDF file
    df = tabula.read_pdf(pdf_file, pages='all', pandas_options={'header': None}, encoding="ISO-8859-1")
    #łączenie DataFrame z wszystkich stron
    df = pd.concat(df)
    #zmiana nazw kolumn
    df = df.rename(columns={1: 'Document_Date', 0: 'Document_Name', 2: 'Document_Value'})
    #usuwanie niepotrzebnych kolumn
    df = df.drop(columns=[3, 4])
    #Różnie są wpisywane nazwy faktur. sprowadzam wszystkie do jednakowego formatu
    df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    #usunięcie wierszy, gdzie conajmniej jedna wartość jest None
    df = df.dropna()
    #usuwam wiersz z  nagłówkami
    df = df.drop(0)
    #reset indeksowania
    df = df.reset_index(drop=True)
    # z kwoty usuwam EUR oraz wszystkie znaki/ kwoty są różnie wpisywane
    df["Document_Value"] = df["Document_Value"].str.replace(" EUR", "")
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = df.iloc[:, 2].str.replace(',', '')
    #dodaje fo kwoty kropkę przed drugą liczbą
    for i, value in enumerate(df['Document_Value']):
        value = value.strip()
        value = value[:-2] + '.' + value[-2:]

        # Update the value in the DataFrame
        df.at[i, 'Document_Value'] = value
    # sprowadzam kwotę do postaci liczbowej
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2])
    return df


# def extract_data_markant(pdf_file):
#     try:
#         df = tabula.read_pdf(pdf_file, pages='all', pandas_options={'header': None}, encoding="ISO-8859-1", guess=False)[1:]
#         df = pd.concat(df)
#         pd.set_option('display.max_rows', None)
#         pd.set_option('display.max_columns', None)
#
#         df = df[[0,1,9, 10]]
#         df = df.rename(columns={0: 'Document_Name', 1: 'Document_Date',  9: 'temp',10: 'temp_value'})
#         df = df.reset_index(drop=True)
#         # print(df)
#
#         df.replace({np.inf: np.nan, -np.inf: np.nan}, inplace=True)
#         df = df.replace(' ', pd.NA).replace('', pd.NA)
#         df = df.dropna(subset=['Document_Date'])
#         mask_summe = df[df.iloc[:, 0].str.contains('Summenwerte auf Listen-Ebene', na=False)]
#         for i, value in mask_summe.iterrows():
#             vr_date = value.iloc[2]
#             t_r = i-2
#             df.loc[t_r, 'Document_Value'] = vr_date
#             # df.drop(i, inplace=True)
#         df = df.reset_index(drop=True)
#         mask_summe1 = df[df.iloc[:, 0].str.contains('Summenwerte auf Listen-Ebene', na=False)]
#         for i, value in mask_summe1.iterrows():
#             vr_date = value.iloc[3]
#             t_r = i-2
#             if pd.isna(df.loc[t_r, 'Document_Value']):
#                 df.at[t_r, 'Document_Value'] = vr_date
#                 df.drop(i, inplace=True)
#         df = df.reset_index(drop=True)
#
#         mask_null = df[df['Document_Name'].isna()]
#         # print(mask_null)
#         for index, row in mask_null.iterrows():
#             d_v = row.iloc[2]
#
#             t_r = index -1
#             if pd.isna(df.loc[t_r, 'Document_Value']):
#                 df.at[t_r, 'Document_Value'] = d_v
#                 # print('ss')
#
#             # df.drop(index, inplace=True)
#
#         df = df.reset_index(drop=True)
#         mask_vrs = df['Document_Name'].str.contains('VR/', na=False)
#
#         df = df[mask_vrs]
#
#         df = df.reset_index(drop=True)
#         for i, value in enumerate(df['Document_Date']):
#             if value is not None:
#                 index_date = value.index('2023')+4
#                 # value = value.strip()
#                 value = value[:index_date].strip()
#                 df.at[i, 'Document_Date'] = value
#
#         for i, value in enumerate(df['Document_Value']):
#             value = value.strip()
#             if value.endswith('-'):
#                 value = '-' + value[:-1]
#                 df.at[i, 'Document_Value'] = value
#             else:
#                 df.at[i, 'Document_Value'] = value
#         df = df.reset_index(drop=True)
#         df = df.drop(columns={'temp_value', 'temp'})
#         # print(df)
#         df['Document_Date'] = df['Document_Date'].replace('^(\d{2}) .(\d{2}).(\d{4})$', r'\3-\2-\1', regex=True)
#         df['Document_Date'] = df['Document_Date'].replace('^(\d{2}).(\d{2}) .(\d{4})$', r'\3-\2-\1', regex=True)
#         df['Document_Date'] = df['Document_Date'].replace('^(\d{2}).(\d{2}).(\d{4})$', r'\3-\2-\1', regex=True)
#         df['Document_Date'] = df['Document_Date'].replace('^(\d{2}) .(\d{2}) .(\d{4})$', r'\3-\2-\1', regex=True)
#         df = df[['Document_Name', 'Document_Date', 'Document_Value']]
#
#         df.iloc[:, -1] = df.iloc[:, -1].str.replace('.', '')
#         df.iloc[:, -1] = pd.to_numeric(df.iloc[:, -1].str.replace(',', '.'))
#         # extract_sum = df.iloc[:,-1].sum()
#         # print(df)
#         #
#         # print(extract_sum)
#         return df
#
#         # df.to_excel('markant_test.xlsx', index=False)
#         # for i, value in df.iterrows():
#         #     if 'Summenwerte auf Listen-Ebene' in value['Document_name']:
#     except ValueError as e:
#         print('to inny plik')

def extract_data_lidl_at_si_es_lt_cz_int(pdf_file):
    # użycie tabuli
    df = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})
    # #jeżeli wartość
    if df == []:
            # with pdf_file as pdf:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        # pdf = io.open(pdf_file, 'rb', buffering=0)
        start_marker = 'Beleg'
        end_marker = '_\nGesamt-Summe'

        intervals = [(0, 68)]

        # Create a PDF reader object
        # pdf_reader = PyPDF2.PdfFileReader(pdf)
        data = []
        # print('dupa')
        for page_num in range(pdf_reader.getNumPages()):
            # Get the page object
            page = pdf_reader.getPage(page_num)

            # Extract the text from the page
            text = page.extract_text()

            # Find the start and end positions of the relevant text
            start_pos = text.find(start_marker)
            end_pos = text.find(end_marker)

            # Extract the relevant text
            relevant_text = text[start_pos:end_pos]

            # Split the text into rows
            rows = relevant_text.split('\n')
            for row in rows:
                if row.startswith(start_marker) or row.startswith(end_marker):
                    continue
                row_data = []
                for interval in intervals:
                    row_data.append(row[interval[0]:interval[1]].strip())
                data.append(row_data)

    # Create a Pandas DataFrame from the extracted data
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        df = pd.DataFrame(data)
        df[0] = df[0].str.replace(' +', ' ').str.replace('_', '')
        df = df[df[0].str.match(r'^\d{8}')]
        df = df.dropna()
        # print(df)
        # df = df[df[1].str.match(r'^\d{1,3}(?:\.\d{3})*(?:,\d{2})$')]
        df[['temp', 'Document_Name', 'Document_Date', 'temp1', 'Document_Value']] = df[0].str.split(' ', n=5, expand=True)

        df = df.drop(columns=['temp', 'temp1'])
        df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3',
                                                          regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^VR[^/](\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3',
                                                          regex=True)
        # df = df.drop(df.index[-4:])
        df = df.drop_duplicates()
        df = df.replace(' ', pd.NA).replace('', pd.NA)
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        for i, value in enumerate(df['Document_Value']):

            value = str(value).strip()

            # Check if the string ends with '-' and starts with a number
            if value.endswith('-') and value[0].isdigit():
                # Swap the positions of the '-' sign and the number using string slicing and concatenation
                value = '-' + value[:-1]

                # Update the value in the DataFrame
                df.at[i, 'Document_Value'] = value

        df = df[['Document_Name', 'Document_Date', 'Document_Value']]
        df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
        print(df)
        return df
    else:
        # łączenie wszystkich DataFrame ze wszystkich stron
        df = pd.concat(df)
        # print(df)
        # usuwanie wierszy, kiedy jest jakaś pusta pozycja
        # df = df.dropna()
        # usuwa duplikaty - nagłówki ze stron
        # df = df.drop_duplicates()
        # usuwa nagłówek
        df = df[df[0].str.match(r'^\d{8}')]
        #
        df[['temp', 'Document_Name', 'Document_Date']] = df[0].str.split(' ', n=2, expand=True)
        df = df.drop(columns=[0, 'temp', 2])
        # zmiana nazwy na prowidłową
        df = df.rename(columns={3: 'Document_Value'})
        df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3', regex=True)
        df['Document_Name'] = df['Document_Name'].replace('^VR(\d{1})(\d{4})/(\d{2})/(\d{5})$', r'VR/\2/\3/\4', regex=True)


        df = df.reset_index(drop=True)
        #przeniesienie minusa na początek kwoty
        for i, value in enumerate(df['Document_Value']):

            value = str(value).strip()

            # Check if the string ends with '-' and starts with a number
            if value.endswith('-') and value[0].isdigit():
                # Swap the positions of the '-' sign and the number using string slicing and concatenation
                value = '-' + value[:-1]

                # Update the value in the DataFrame
                df.at[i, 'Document_Value'] = value
        #ustawienie porządanej kolejności kolumn
        df = df[['Document_Name', 'Document_Date', 'Document_Value']]
        df = df.dropna()
        #doprowadzenie kolumny z kwotami do porządanego formatu
        df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
        print(df)
        return df

def extract_data_lidl_fr(pdf_file):
    # użycie tabuli
    df = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})

    # łączenie wszystkich DataFrame ze wszystkich stron
    df = pd.concat(df)

    df = df[df[0].str.match(r'^\d{8}')]
    df = df.reset_index(drop=True)


    df[['temp', 'Document_Name1', 'Document_Date1']] = df[0].str.split(' ', n=2, expand=True)
    date_regex = r'\d{2}\.\d{2}\.\d{4}'

    # sprawdzanie, które wartości nie pasują do wzorca daty
    not_matching = ~df['Document_Date1'].str.match(date_regex, na=False)
    is_matching1 = df['Document_Date1'].str.match(date_regex, na=False)
    is_matching2 = df[1].str.match(date_regex, na=False)

    # przenoszenie wartości niepasujących do nowej kolumny 'Niepoprawne dane'
    df.loc[not_matching, 'Document_Name2'] = df.loc[not_matching, 'Document_Date1']
    df.loc[is_matching1, 'Document_Date3'] = df.loc[is_matching1, 'Document_Date1']
    df.loc[is_matching2, 'Document_Date2'] = df.loc[is_matching2, 1]
    df = df.fillna('')
    df['Document_Name'] = df[['Document_Name1', 'Document_Name2']].agg(' '.join, axis=1)
    df['Document_Date'] = df[['Document_Date3', 'Document_Date2']].agg(''.join, axis=1)
    df = df.rename(columns={3: 'Document_Value'})
    df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR(\d{1})(\d{4})/(\d{2})/(\d{5})$', r'VR/\2/\3/\4', regex=True)
    df['Document_Name'] = df['Document_Name'].str.strip()

    df = df.reset_index(drop=True)
    #przeniesienie minusa na początek kwoty
    for i, value in enumerate(df['Document_Value']):

        value = str(value).strip()

        # Check if the string ends with '-' and starts with a number
        if value.endswith('-') and value[0].isdigit():
            # Swap the positions of the '-' sign and the number using string slicing and concatenation
            value = '-' + value[:-1]

            # Update the value in the DataFrame
            df.at[i, 'Document_Value'] = value
    #ustawienie porządanej kolejności kolumn
    df = df[['Document_Name', 'Document_Date', 'Document_Value']]

    df = df.dropna()
    #doprowadzenie kolumny z kwotami do porządanego formatu
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    print(df)
    return df


def extract_data_lidl_it(pdf_file):
    # użycie tabuli
    df = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})

    # łączenie wszystkich DataFrame ze wszystkich stron
    df = pd.concat(df)
    df[['Document_Name', 'Document_Date']] = df[0].str.split(' ', n=2, expand=True)

    df = df.rename(columns={2: 'Document_Value'})

    # #ustawienie porządanej kolejności kolumn
    df = df[['Document_Name', 'Document_Date', 'Document_Value']]
    df = df.dropna()
    df = df.drop(0)
    #doprowadzenie kolumny z kwotami do porządanego formatu
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    print(df)
    return df


def extract_data_lidl_rs(pdf_file):
    # użycie tabuli
    df = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})

    # łączenie wszystkich DataFrame ze wszystkich stron
    df = pd.concat(df)
    df = df[df[0].str.match(r'^\d{8}')]
    df[['temp','Document_Name']] = df[0].str.split(' ', n=2, expand=True)

    df = df.rename(columns={4: 'Document_Value', 1: 'Document_Date'})
    df = df.reset_index(drop=True)
    #przeniesienie minusa na początek kwoty
    for i, value in enumerate(df['Document_Value']):

        value = str(value).strip()

        # Check if the string ends with '-' and starts with a number
        if value.endswith('-') and value[0].isdigit():
            # Swap the positions of the '-' sign and the number using string slicing and concatenation
            value = '-' + value[:-1]

            # Update the value in the DataFrame
            df.at[i, 'Document_Value'] = value
    #ustawienie porządanej kolejności kolumn
    df = df[['Document_Name', 'Document_Date', 'Document_Value']]
    # #doprowadzenie kolumny z kwotami do porządanego formatu
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    print(df)
    return df


def extract_data_lidl_hr(pdf_file):
    # użycie tabuli
    # df = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})
    # # # print(df_col)
    # # #jeżeli wartość
    # if df == []:
            # with pdf_file as pdf:
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    # pdf = io.open(pdf_file, 'rb', buffering=0)
    start_marker = 'Beleg'
    end_marker = '_\nGesamt-Summe'

    intervals = [(0, 68)]

    # Create a PDF reader object
    # pdf_reader = PyPDF2.PdfFileReader(pdf)
    data = []
    # print('dupa')
    for page_num in range(pdf_reader.getNumPages()):
        # Get the page object
        page = pdf_reader.getPage(page_num)

        # Extract the text from the page
        text = page.extract_text()

        # Find the start and end positions of the relevant text
        start_pos = text.find(start_marker)
        end_pos = text.find(end_marker)

        # Extract the relevant text
        relevant_text = text[start_pos:end_pos]

        # Split the text into rows
        rows = relevant_text.split('\n')
        for row in rows:
            if row.startswith(start_marker) or row.startswith(end_marker):
                continue
            row_data = []
            for interval in intervals:
                row_data.append(row[interval[0]:interval[1]].strip())
            data.append(row_data)

# Create a Pandas DataFrame from the extracted data
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(data)
    df[0] = df[0].str.replace(' +', ' ').str.replace('_', '')
    df = df[df[0].str.match(r'^\d{8}')]
    df = df.dropna()
    # print(df)
    # df = df[df[1].str.match(r'^\d{1,3}(?:\.\d{3})*(?:,\d{2})$')]

    # df = df.to_excel('test_lidl.xlsx', index=False)


    df[['temp', 'Document_Name', 'Document_Date', 'temp1', 'temp2', 'Document_Value']] = df[0].str.split(' ', n=5, expand=True)

    df = df.drop(columns=['temp', 'temp1'])
    df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3',
                                                      regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR[^/](\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3',
                                                      regex=True)
    # df = df.drop(df.index[-4:])
    df = df.drop_duplicates()
    df = df.replace(' ', pd.NA).replace('', pd.NA)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    for i, value in enumerate(df['Document_Value']):

        value = str(value).strip()

        # Check if the string ends with '-' and starts with a number
        if value.endswith('-') and value[0].isdigit():
            # Swap the positions of the '-' sign and the number using string slicing and concatenation
            value = '-' + value[:-1]

            # Update the value in the DataFrame
            df.at[i, 'Document_Value'] = value

    df = df[['Document_Name', 'Document_Date', 'Document_Value']]
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    print(df)
    # print(len(df['Document_Value']))
    return df


def extract_data_lidl_nl(pdf_file):
    # użycie tabuli
    # df = tabula.read_pdf(pdf_file, pages='all', encoding="ISO-8859-1", pandas_options={'header': None})
    # # # print(df_col)
    # # #jeżeli wartość
    # if df == []:
            # with pdf_file as pdf:
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    # pdf = io.open(pdf_file, 'rb', buffering=0)
    start_marker = 'Beleg'
    end_marker = '_\nGesamt-Summe'

    intervals = [(0, 68)]

    # Create a PDF reader object
    # pdf_reader = PyPDF2.PdfFileReader(pdf)
    data = []
    # print('dupa')
    for page_num in range(pdf_reader.getNumPages()):
        # Get the page object
        page = pdf_reader.getPage(page_num)

        # Extract the text from the page
        text = page.extract_text()

        # Find the start and end positions of the relevant text
        start_pos = text.find(start_marker)
        end_pos = text.find(end_marker)

        # Extract the relevant text
        relevant_text = text[start_pos:end_pos]

        # Split the text into rows
        rows = relevant_text.split('\n')
        for row in rows:
            if row.startswith(start_marker) or row.startswith(end_marker):
                continue
            row_data = []
            for interval in intervals:
                row_data.append(row[interval[0]:interval[1]].strip())
            data.append(row_data)

# Create a Pandas DataFrame from the extracted data
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(data)
    df[0] = df[0].str.replace(' +', ' ').str.replace('_', '')
    df = df[df[0].str.match(r'^\d{8}')]
    # df = df.dropna()
    df[0] = df[0].str.strip()
    # print(df)
    # print(df)
    # df = df[df[1].str.match(r'^\d{1,3}(?:\.\d{3})*(?:,\d{2})$')]

    # df = df.to_excel('test_lidl.xlsx', index=False)


    df[['temp', 'Document_Name', 'Document_Date', 'Document_Value']] = df[0].str.split(' ', n=4, expand=True)

    # df = df.drop(columns=['temp', 'temp1'])
    df['Document_Name'] = df['Document_Name'].replace('^VR(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^(\d{4})(\d{2})(\d{5})$', r'VR/\1/\2/\3', regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR/(\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3',
                                                      regex=True)
    df['Document_Name'] = df['Document_Name'].replace('^VR[^/](\d{4})/(\d{2})/(\d{5})$', r'VR/\1/\2/\3',
                                                      regex=True)
    # df = df.drop(df.index[-4:])
    df = df.drop_duplicates()
    df = df.replace(' ', pd.NA).replace('', pd.NA)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    for i, value in enumerate(df['Document_Value']):

        value = str(value).strip()

        # Check if the string ends with '-' and starts with a number
        if value.endswith('-') and value[0].isdigit():
            # Swap the positions of the '-' sign and the number using string slicing and concatenation
            value = '-' + value[:-1]

            # Update the value in the DataFrame
            df.at[i, 'Document_Value'] = value

    df = df[['Document_Name', 'Document_Date', 'Document_Value']]
    df.iloc[:, 2] = df.iloc[:, 2].str.replace('.', '')
    df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2].str.replace(',', '.'))
    print(df)
    # print(len(df['Document_Value']))
    return df