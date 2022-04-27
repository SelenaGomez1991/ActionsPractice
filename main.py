import time
import requests
from requests.structures import CaseInsensitiveDict
import os
import copy
import math

def thread_func(url, headers, out_dest, base_name, file_nums, file_size, webdavCl, maxSizeAtServer, max_files_at_time = 9999):
    print("Thread started")
    files_uploaded = 0
    for i in range(len(file_nums)):
        # Now calculate start and end based on file_size
        
        start = file_nums[i] * file_size * GB_TO_BYTES
        end = start + file_size * GB_TO_BYTES - 1
        range_str = "bytes=" + str(start) + "-" + str(end)
        headers["Range"] = range_str

        while i - files_uploaded > max_files_at_time: time.sleep(10)

        # Now download the file using streaming
        session = requests.Session()
        resp =session.get(url, headers = headers, stream = True)
        # Streaming Loop and write to file locally
        file_name = f'{base_name}_{i}'
        print(f'Downloading {file_name}')
        with open(file_name, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                else:
                  print('Shit')
            f.flush()

        print(f'Uploading {file_name}')
        # Now upload the file using webdav server only if file size + available storage < max_file_size
        avail_size = maxSizeAtServer - recurse_file_size(out_dest)/GB_TO_BYTES
        while avail_size < file_size: time.sleep(10)        
        files_uploaded += 1
        while True:
            try:
                webdavCl.upload_file(file_name, os.path.join(out_dest, file_name), overwrite = True)
                os.remove(file_name)
                break
            except InsufficientStorage:
                time.sleep(10)
                continue
            except Exception as e:
                print('While Uploading following error occured', e)
                break

# !pip install webdav4
# !sudo apt-get install aria2



def recurse_file_size(dir):
    total_size = 0
    for item in client.ls(dir):
        if item['type'] == 'directory':
            total_size += recurse_file_size(item['name'])
        else:
            total_size += client.content_length( item['name'])
    return total_size

MB_TO_BYTES = 1024 * 1024
GB_TO_BYTES = 1024 * 1024 * 1024
KB_TO_BYTES = 1024

headers = CaseInsensitiveDict()
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
headers["Accept-Language"] = "en-GB,en;q=0.9"
headers["Cache-Control"] = "max-age=0"
headers["Connection"] = "keep-alive"
headers["Referer"] = "https://www.xilinx.com/"
headers["Sec-Fetch-Dest"] = "document"
headers["Sec-Fetch-Mode"] = "navigate"
headers["Sec-Fetch-Site"] = "cross-site"
headers["Sec-Fetch-User"] = "?1"
headers["Sec-GPC"] = "1"
headers["Upgrade-Insecure-Requests"] = "1"
headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"


import sys

# Order: url, FILE_SIZE, PART_SIZE = 1, NUM_THREADS = 1, OUT_FILE_NAME, OUT_DIR, MAX_SIZE_AT_SERVER = 8, PASSWORD

url = sys.argv[1]
FILE_SIZE = float(sys.argv[2]) 
PART_SIZE = int(sys.argv[3]) 
NUM_PARTS = int(math.ceil(FILE_SIZE / PART_SIZE))
NUM_THREADS = int(sys.argv[4])  # Will be decided based on storage size of local server
file_nums = [[i for i in range(NUM_PARTS)][thread::NUM_THREADS] for thread in range(NUM_THREADS)]

from webdav4.client import Client, InsufficientStorage
p = sys.argv[8]
user_name = 'cs5190443'
client = Client(f'https://owncloud.iitd.ac.in/nextcloud/remote.php/dav/files/{user_name}/',
                auth=(user_name, p))

out_dest = sys.argv[6]
try: client.mkdir(out_dest, )
except: ...

thread_func(url, copy.deepcopy(headers), out_dest, sys.argv[5], file_nums[0], PART_SIZE, client,maxSizeAtServer =  int(sys.argv[7]),)


