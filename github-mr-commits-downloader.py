#!/usr/bin/env python3

import os
from heapq import merge

import requests
from urllib.parse import urlparse, quote
from termcolor import colored
import argparse,re
import pdb

MR_OUTPUT_FOLDER = "MR-Download-Results"
COMMIT_OUTPUT_FOLDER = "Commit-Download-Results"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pru','--pr-url',dest='pullrequest_url', help="Pull Request URL")
    parser.add_argument('-cu','--commit-url',dest='commit_url', help="Commit Request URL")
    parser.add_argument('-cf','--commit-file',dest='commit_file', help="Commit Request File")
    parser.add_argument('-mu','--merge-url',dest='mr_url', help="Merge Request URL")
    parser.add_argument('-mf','--merge-file',dest='mr_file', help="Merge Request File")
    parser.add_argument('-t','--token',dest='github_token',help="Gitlab Token (Optional: Fetched from Env: GITHUB_API_TOKEN)")
    parser.add_argument('-ff','--full-file',action="store_true",dest='full_file',help="Download Complete File (Default: Downloads only diff)",default=False)
    args = parser.parse_args()

    if not args.github_token and not os.getenv("GITHUB_API_TOKEN"):
        exit(colored("[-] Error: Could not fetch Env Variable GITLAB_API_TOKEN. Please set it or provide argument -t <token>","red"))

    if not args.commit_url and not args.commit_file and not args.mr_url and not args.mr_file and not args.pullrequest_url:
        exit(colored("[-] Error: Either commit_url or commit_file or mr_url or mr_file should be provided","red"))
    

    return args

def get_github_api_baseurl(github_url):
    parsed_url = urlparse(github_url)
    github_api_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/api/v3"  #https://github.host.com/api/v3
    return github_api_base_url


def Download_Code_From_PR_Url(pr_url):
    global GITHUB_API_TOKEN

    #Get Base URL
    base_url = get_github_api_baseurl(pr_url)
    pr_uri_list = pr_url.split("/")[3:]
    org,repo,pulls,pull_number = pr_uri_list[0],pr_uri_list[1],"pulls",pr_uri_list[3]  #URL has pull, but api requires pulls
    final_api_url = f"{base_url}/repos/{org}/{repo}/{pulls}/{pull_number}"
    headers = {"Authorization": f"token {GITHUB_API_TOKEN}", "Accept": "application/vnd.github.v3.diff"}
    response = requests.get(final_api_url, headers=headers)
    print(response.text)
 
    #Example PR URL: https://github.host.com/api/v3/repos/ORGNAME/REPONAME/pulls/211


def Download_Code_From_MR(mr_url):
    pass



def Download_Code_From_Commit_Url(commit_url):
    pass



def save_diff_to_file(filepath, codediff):
    filename = filepath.split("/")[-1]
    folder = "/".join(filepath.split("/")[:-1])
    if folder != "":
        os.makedirs(folder, exist_ok=True)
    with open (filepath, "w") as fileptr:
        fileptr.write(codediff)

    beautify_file(filepath)


def beautify_file(filepath):
    with open(filepath,"r") as diff_file:
        processed_file_content = ""
        for line in diff_file:
            if line.startswith("+") or line.startswith("-"):
                processed_file_content += line[1:]
            else:
                line = re.sub(r'@@ -\d+,\d+ \+\d+,\d+ @@ ', '', line)
                processed_file_content += line

    with open(filepath,"w") as diff_file:
        diff_file.write(processed_file_content)

    print(colored(f"|--> File: ","yellow"),colored(f"{filepath}","white"))


def verify_github_token(github_url):
    global GITHUB_API_TOKEN

    github_base_url = get_github_api_baseurl(github_url)
    git_verify_url = f"{github_base_url}/user"
    headers = {"Authorization" : f"token {GITHUB_API_TOKEN}"}
    res = requests.get(git_verify_url,headers=headers)
    if res.status_code != 200:
        exit(colored(f"[X] Gitlab Token is Invalid: {res.status_code}","red"))
    print(colored("[-] Gitlab Token successfully validated","light_magenta"))



def main():
    global GITHUB_API_TOKEN
    global DOWNLOAD_COMPLETE_FILE

    args = get_args()
    GITHUB_API_TOKEN = args.github_token or os.getenv("GITHUB_API_TOKEN")

    curr_dir = os.getcwd()
    os.makedirs("results", exist_ok=True)
    os.chdir("results")

    DOWNLOAD_COMPLETE_FILE = args.full_file

    if args.pullrequest_url:
        verify_github_token(args.pullrequest_url)
        Download_Code_From_PR_Url(args.pullrequest_url)
        #Example_Commit_URL = "https://github.host.com/projectname/subproject/-/commit/commithash"

    if args.commit_url:
        verify_github_token(args.commit_url)
        Download_Code_From_Commit_Url(args.commit_url)
        #Example_Commit_URL = "https://github.host.com/projectname/subproject/-/commit/commithash"

    elif args.mr_url:
        verify_github_token(args.mr_url)
        Download_Code_From_MR(args.mr_url)
        #Example_MR_URL = "https://github.host.com/projectname/subproject/-/merge_requests/177"

    elif args.commit_file:
        with open(os.path.join(curr_dir, args.commit_file), "r") as fileptr:
            urls = fileptr.readlines()
            verify_github_token(urls[0].strip())
            for commit_url in urls:
                commit_url = commit_url.strip()
                print(colored(f"\n[-] {commit_url}","cyan"))
                Download_Code_From_Commit_Url(commit_url)

    elif args.mr_file:
        with open(os.path.join(curr_dir, args.mr_file), "r") as fileptr:
            urls = fileptr.readlines()
            verify_github_token(urls[0].strip())
            for merge_url in urls:
                merge_url = merge_url.strip()
                print(colored(f"\n[-] {merge_url}","cyan"))
                Download_Code_From_MR(merge_url)

main()


'''
#TODO
1)Add support for full file download even in MergeRequests
2)Test with multiple Commit requests, as last time it was given empty response for few files
'''