from __future__ import print_function
import httplib2
import os
import io
from kivy.logger import Logger

import apiclient
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload 
import oauth2client
from oauth2client import client
from oauth2client import tools


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Kiltispiikki'
            
class DriveClient():

    
    def __init__(self):
        self.credentials = self.get_credentials()
        self.service = None
    
    def get_credentials(self):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive-kiltispiikki.json')
    
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
	    try:
		c_secret_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),CLIENT_SECRET_FILE)
		flow = client.flow_from_clientsecrets( c_secret_path, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
		    credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
		    credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	    except oauth2client.clientsecrets.InvalidClientSecretsError:
		Logger.info("Drive: creation of client secrets faield, prob missing client_secret.json")		    
            
        return credentials    
        
    def connect(self):
        """Shows basic usage of the Google Drive API.
    
        Creates a Google Drive API service object and outputs the names and IDs
        for up to 10 files.
        """
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)
        return service
    
         
    def upload_file(self, filename = None, file_path = None):
        if self.service == None:
            self.service = self.connect()
            if self.service == None:
                Logger.info('DriveClient: Connecting to drive failed')
                return
        #no filename given -> abort        
        if not filename: return False
        

        FILENAME = filename
        if file_path:
            FILENAME = os.path.join(file_path, filename)
            
        
        #filetype on drive, docs filetype required for export
        MIMETYPE = 'application/vnd.google-apps.document'
        #filename on this system and the name of the uploaded file on drive
        TITLE = filename
        #general description
        DESCRIPTION = 'Csv list of account_name,customer_name,tab_value'
        #The Kiltispiikkivarmuuskopiot folder on hupi.mestarit drive
        PARENTFOLDER = '0BxdutqQIi9bzYWJsU0ExM2hUbXM'
        
        media_body = apiclient.http.MediaFileUpload(
                            FILENAME,
                            resumable=True
                        )
        # The body contains the metadata for the file. Name on drive
        body = {
          'description': DESCRIPTION,
          'name':TITLE,
          'parents':[PARENTFOLDER],
          'mimeType':MIMETYPE,
        }
        
        # Perform the request and print the result.
        self.service.files().create(body=body, media_body=media_body).execute()
        #return true if upload successful
        return True
        
    def download_latest_csv(self, full_path=None):
        if self.service == None:
            self.service = self.connect()
            if self.service == None:
                Logger.info('DriveClient: Connecting to drive failed')
                return None
                
        parent_folder_id = '0BxdutqQIi9bzYWJsU0ExM2hUbXM'
        results = self.service.files().list(
                    pageSize=10,fields="nextPageToken, files(id, name)",
                    q="'{}' in parents".format(parent_folder_id),
                    orderBy="createdTime desc").execute()
        
        #import pprint
        #pprint.pprint(results)
        
        items = results.get('files', [])
        if not items:
            Logger.info('DriveClient: No files in the Kiltispiikki folder.')
            return None
        else:
            download_id = items[0]['id']
            name = items[0]['name']
            file1 = self.service.files().export(
                    fileId=download_id, mimeType='text/plain').execute()
            if file1:
                fn = name
                if full_path:
                    fn = os.path.join( full_path, 'logs', fn)
                with open(fn, 'wb') as fh:
                    fh.write(file1)
                Logger.info('DriveClient: downloaded {}'.format(fn))                
            return name



    def download_settings(self, full_path=None):
                
        settings_file_id = '1TT33uz1xMpmJ5vHewv4IwihpKTNokTTC'

        return self.download_file(settings_file_id, "settings_main", full_path= full_path)





    #only for binary files such as json (not google docs)
    def download_file(self, file_id, file_name, full_path = None):
        if self.service == None:
            self.service = self.connect()
            if self.service == None:
                Logger.info('DriveClient: Connecting to drive failed')
                return None


        request = self.service.files().get_media(fileId=file_id)

        fn = file_name
        if ( full_path is not None):
            fn = os.path.join(full_path, file_name)
        fh = io.FileIO(fn, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            Logger.info("DriveClient:  Download {}".format( int(status.progress() * 100) ) ) 
        return fn

