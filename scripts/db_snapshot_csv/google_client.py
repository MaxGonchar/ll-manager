import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


class GoogleClient:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, folder_id: str) -> None:
        self.folder_id = folder_id
        self.creds = self._get_creds()
        self.service = self._get_service()

    def _get_service(self):
        try:
            service = build("drive", "v3", credentials=self.creds)
            return service
        except HttpError as error:
            print(f"Failed to get Google Drive service: {error}")
            raise

    def _get_creds(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json", self.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def get_saved_snapshots(self):
        try:
            files = []
            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = (
                    self.service.files()
                    .list(
                        q=f"'{self.folder_id}' in parents",
                        spaces="drive",
                        fields="nextPageToken, files(id, name)",
                        pageToken=page_token,
                    )
                    .execute()
                )
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break

        except HttpError as error:
            print(f"An error occurred: {error}")
            files = None

        return files

    def upload_with_conversion(self, file_name):
        try:
            file_metadata = {
                "name": file_name,
                "mimeType": "application/zip",
                "parents": [self.folder_id],
            }
            media = MediaFileUpload(
                file_name, mimetype="application/zip", resumable=True
            )
            # pylint: disable=maybe-no-member
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            print(f'File with ID: "{file.get("id")}" has been uploaded.')

        except HttpError as error:
            print(f"An error occurred: {error}")
            file = None

        return file.get("id")  # type: ignore

    def delete_extra_snapshots(self, file_ids):
        def delete_callback(request_id, response, exception):
            if exception is not None:
                print("!!!", exception)

        try:
            batch = self.service.new_batch_http_request(
                callback=delete_callback
            )
            for file_id in file_ids:
                batch.add(self.service.files().delete(fileId=file_id))
            batch.execute()
        except HttpError as error:
            print(f"An error occurred: {error}")
