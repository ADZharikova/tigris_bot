import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


class Gog:

    CREDENTIALS_FILE = 'creds.json'
    spreadsheet_id = '1BjXw7Kq-Jo0JVDjV4T4__CiLHzZIYj1lXShpZ6zEvc4'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

    def add_payment(self, fio_adult: str, fio_kid: str, date: str, abonement_type: str, type_of_sport: str, abonement_count_workout: str, price: str):
        _numb = str(self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range = 'J2:J2',
            majorDimension = "ROWS"
            ).execute())

        _numb=_numb[63:-4]

        _range = "A" + _numb + ":G" + _numb
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": _range,
                    "majorDimension": "ROWS",
                    "values": [[fio_adult, fio_kid, date, abonement_type, type_of_sport, abonement_count_workout, price]]}
	            ]
            }
        ).execute()