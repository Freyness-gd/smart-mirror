import pickle, os.path, json, time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import re
import sys

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailClient():

    __service = None
    __messageList = [0, 0, 0, 0, 0]
    __maxNumb = 5
    __loadedStruct = None

    def __init__(self):
        creds = None
        if os.path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('credentials/token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        # __service object created
        self.__service = build('gmail', 'v1', credentials=creds)


    def get_message(self):
        if not(self.check_update()):
            print ("none")
            return None

        messageStruct = {"email1":{"subject":"", "snippet":"", "date":""},
                         "email2":{"subject":"", "snippet":"", "date":""},
                         "email3":{"subject":"", "snippet":"", "date":""},
                         "email4":{"subject":"", "snippet":"", "date":""},
                         "email5":{"subject":"", "snippet":"", "date":""}}
        pageindex = 1
        #itterate through the email data and save subject and snippet
        for message in self.__messageList:

            #determines how many chracter are shown
            subject_limit = 30
            snippet_limit = 50
            data = self.__service.users().messages().get(userId='me', id=message).execute()
            snippet=''
            subject=''
            date='xxxx'

            for character in data['snippet']:
                snippet += character
                if snippet_limit == 0:
                    snippet += "..."
                    break
                snippet_limit -= 1

            

            for i in range(len(data['payload']['headers'])):
                if data['payload']['headers'][i]['name'] == 'Subject':
                    data_subject = data['payload']['headers'][i]['value']
                elif data['payload']['headers'][i]['name'] == 'Date':
                    date = data['payload']['headers'][i]['value']


            for character in data_subject:
                subject += character
                if subject_limit == 0:
                    subject += "..."
                    break
                subject_limit -= 1


            try:
                index_comma = re.search(',', date, re.I).end()
                index_comma += 1
                date = date[index_comma:(index_comma+11)]
            except Exception as e:
                print("Error occured")


            pageString = "email" + str(pageindex)
            #save the data
            messageStruct[pageString]['snippet'] = snippet
            messageStruct[pageString]['subject'] = subject
            messageStruct[pageString]['date'] = date
            pageindex += 1

        self.__loadedStruct = json.dumps(messageStruct)

    def check_update(self):
        rawid = self.__service.users().messages().list(userId='me', maxResults=self.__maxNumb, labelIds="CATEGORY_UPDATES").execute()
        new___messageList = []

        for x in rawid['messages']:
            new___messageList.append(x['id'])

        if self.__messageList[0] != new___messageList[0]:
            self.__messageList = new___messageList
            return True
        else:
            return False

    def request_payload(self):
        self.get_message()
        return self.__loadedStruct


if __name__ == '__main__':
    client = GmailClient()
    client.get_message()
