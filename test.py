import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from threading import Timer


from shared_vars import drive

TEST_PHOTOS_ALBUM='AF1QipMRowgw87imsEaj-LMCn0iWWn5QlIXifYJqndzDykpO1E0wyTjvxsBCpKk3JTccLA'

nammappings=[]

def nArgs(*args):
        file_list = drive.ListFile({'q': "'1xyZ3daNuKgrM0lBvCRA9wZ8yKF_WSwuo' in parents and trashed=false"}).GetList()
        print(file_list[0]['title'])
        for file in file_list:
                nammappings.append(file['title']+','+file['id']+'\n')
        print(nammappings)


        file1 = open('myfile.txt', 'w')

        

        # Writing multiple strings
        # at a time
        file1.writelines(nammappings)
        
        # Closing file
        file1.close()
 


#arguments: 
#how long to wait (in seconds), 
#what function to call, 
#what gets passed in
r = Timer(1.0, nArgs, ("arg1","arg2"))

r.start()





#id and title