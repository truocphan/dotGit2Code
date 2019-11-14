import sys, os, subprocess
import wget
import requests
import re


dotgit = [
	"/.git/COMMIT_EDITMSG",
	"/.git/FETCH_HEAD",
	"/.git/HEAD",
	"/.git/ORIG_HEAD",
	"/.git/config",
	"/.git/description",
	"/.git/hooks/applypatch-msg.sample",
	"/.git/hooks/applypatch-msg.sample",
	"/.git/hooks/applypatch-msg.sample",
	"/.git/hooks/commit-msg.sample",
	"/.git/hooks/post-commit.sample",
	"/.git/hooks/post-receive.sample",
	"/.git/hooks/post-update.sample",
	"/.git/hooks/pre-applypatch.sample",
	"/.git/hooks/pre-commit.sample",
	"/.git/hooks/pre-push.sample",
	"/.git/hooks/pre-rebase.sample",
	"/.git/hooks/pre-receive.sample",
	"/.git/hooks/prepare-commit-msg.sample",
	"/.git/hooks/update.sample",
	"/.git/index",
	"/.git/info/exclude",
	"/.git/info/refs",
	"/.git/logs/HEAD",
	"/.git/logs/refs/heads/master",
	"/.git/logs/refs/remotes/origin/HEAD",
	"/.git/logs/refs/remotes/origin/master",
	"/.git/logs/refs/stash",
	"/.git/objects/info/packs",
	"/.git/packed-refs",
	"/.git/refs/heads/master",
	"/.git/refs/remotes/origin/HEAD",
	"/.git/refs/remotes/origin/master",
	"/.git/refs/stash"
]

headers = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
}

def Download_File(url):
	if requests.get(url, headers=headers).status_code == 200:
		if not os.path.exists("/".join(url.split("//")[-1].split("/")[:-1])):
			os.makedirs("/".join(url.split("//")[-1].split("/")[:-1]))
		print("Downloading: {}".format(url))
		if os.path.exists(url.split("//")[-1]):
			os.remove(url.split("//")[-1])
		wget.download(url, url.split("//")[-1])
		print("\n")
		return True
	return False

def Download_objects(SHA1_hash_lists, url, SHA1_hash):
	if SHA1_hash not in SHA1_hash_lists:
		if Download_File(url+"/.git/objects/{}/{}".format(SHA1_hash[:2], SHA1_hash[2:])):
			SHA1_hash_lists.append(SHA1_hash)
			proc = subprocess.Popen("cd {}; git cat-file -p {}".format(url.split("//")[-1], SHA1_hash), stdout=subprocess.PIPE, shell=True)
			(out, err) = proc.communicate()
			for SHA1_hash in re.findall("[0-9a-fA-F]{40}", out):
				Download_objects(SHA1_hash_lists, url, SHA1_hash)

try:
	url = sys.argv[1]
	for i in dotgit:
		Download_File(url+i)
	if os.path.exists(url.split("//")[-1]+"/.git/refs/heads/master"):
		SHA1_hash_lists = list()
		SHA1_hash = open(url.split("//")[-1]+"/.git/refs/heads/master").read()[:-1]
		Download_objects(SHA1_hash_lists, url, SHA1_hash)

except Exception as e:
	exit("python {} URL".format(sys.argv[0]))