import boto3
from flask import current_app
from werkzeug.datastructures import FileStorage
from io import BytesIO
import tempfile
import os
from werkzeug.utils import secure_filename
import uuid
class AwsService():
	def __init__(self) -> None:
		self.s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'), region_name=current_app.config['AWS_REGION'])

	def upload_file(self, file):
		try:
			# Create a temporary file
			with tempfile.NamedTemporaryFile(delete=False) as temp_file:
				file.save(temp_file.name)
				temp_file_path = temp_file.name

			# Use the original filename for the S3 object name
			object_name = secure_filename(file.filename)
   
			key = f"resumes/{object_name}-{uuid.uuid4()}"
			print(f"Uploading file to S3: {key}")

			# Upload the temporary file
			response = self.s3.upload_file(temp_file_path, current_app.config['AWS_BUCKET_NAME'], key)
			print(f"File uploaded successfully to S3")

			# Remove the temporary file
			os.unlink(temp_file_path)
			return key
   
		except Exception as e:
			print(f"Error uploading file to S3: {str(e)}")
			return False
		return response

	def get_file(self, key):
		return self.s3.generate_presigned_url('get_object', 
												Params={'Bucket': current_app.config['AWS_BUCKET_NAME'], 'Key': key}, 
												ExpiresIn=60,
												HttpMethod='GET')

	def delete_file(self, bucket_name, key):
		self.s3.delete_object(Bucket=bucket_name, Key=key)