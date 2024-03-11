
from googleapiclient.discovery import build
from google.oauth2 import service_account
from threading import Timer
import asyncpraw
import asyncio
from secrets.reddit_secrets import ID,SECRET,PASSWORD,USER_AGENT,NAME

from shared_vars import drive,googleClient


nammappings=[]


print([].__len__())



# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.create_task(e())
# loop.run_forever()
# https://docs.google.com/spreadsheets/d/1RY8yiuL2cZkQyMMjpGWZleoBs21_zrRbvWxxyMNplOA/edit?pli=1#gid=1464273541

# def nArgs(*args):
      #  cardSheetSearch = googleClient.open("Hellscube Database").worksheet("MORE TESTING")
      #  cardSheetSearch.append_row(["1","3","4"])
       
        # file_list = drive.ListFile({'q': "'1xyZ3daNuKgrM0lBvCRA9wZ8yKF_WSwuo' in parents and trashed=false"}).GetList()
        # print(file_list[0]['title'])
        # for file in file_list:
        #         nammappings.append(file['title']+','+file['id']+'\n')
        # print(nammappings)


        # file1 = open('myfile.txt', 'w')

        

        # # Writing multiple strings
        # # at a time
        # file1.writelines(nammappings)
        
        # # Closing file
        # file1.close()
 


#arguments: 
#how long to wait (in seconds), 
#what function to call, 
#what gets passed in
# r = Timer(1.0, nArgs, ("arg1","arg2"))

# r.start()





#id and title