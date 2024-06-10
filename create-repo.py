"""
Creates New Branch and Updates terraform.tfvars 
"""
import os
import requests
from github import Github

api_token=os.environ["create_repo_token"]
headers = {"Authorization": "Bearer " + api_token}
orgName="edeuae"
actor = os.environ["ACTOR"]


def assignMember(orgName,memberName,repoName):
    print(F'Assigning member {memberName} permission admin on repo {repoName}.')
    url =  F'https://api.github.com/repos/{orgName}/{repoName}/collaborators/{memberName}'
    variables = '{"permission":"admin"}'
    res = requests.put(url,data=variables ,headers=headers, timeout=10)
    status_code=res.status_code
    print(F'status_code = {status_code}')
    match status_code:
        case 204:
            # permissions assigned
            msg = F'Member {memberName} has been granted permission admin on repo {repoName} in organization {orgName}.'
            print(msg)
            updateGithubIssue(msg,"open")
        case _  :
            # permissions not assigned
            msg = F'Failure assigning team {memberName} permission admin on repo {repoName}.  Permissions not granted.'
            print(msg)
            # github_message +=  msg + "\n"
            # updateGithubIssue(github_message, "open")
            updateGithubIssue(msg, "open")
            exit()


def updateGithubIssue(message, issuestate):
    RepoName = os.getenv('REPO_NAME', "")
    IssueNumber = os.getenv('CREATE_REPO_NUMBER', "")
    token = os.getenv('GITHUB_TOKEN', "")

    if len(token)==0:
        print("skipping github issue update, token was empty...")
    else:
        print("updating github issue with status - message: {} - {}".format(issuestate, message)) 
        # both were successful
        g = Github(token)
        print("Github Issue Update : connected")
        repo = g.get_repo(RepoName)
        print("Github Issue Update repo : {} ".format(repo))
        issue = repo.get_issue(number=int(IssueNumber))
        print("Github Issue Update issue : {} ".format(issue))
        comment = issue.create_comment(message)
        print("Github Issue Update comment : {} ".format(comment))
        status = issue.edit(state=issuestate)
        print("Github Issue Update status : {} ".format(status))

def checkRepoDoesNotExist(orgName, repoName): 
    print(F'Checking if repo {repoName} already exists in {orgName}.')
    url = F'https://api.github.com/repos/{orgName}/{repoName}'
    res = requests.get(url, headers=headers, timeout=10)
    status_code=res.status_code
    print(F'status_code = {status_code}')
    match status_code:
        case 200:
            # repo found
            tmpRepo=res.json()
            tmpRepo_name=tmpRepo['name']
            tmpRepo_full_name=tmpRepo['full_name']
            if tmpRepo_name == repoName:
                print(F'The repo exists with the same name {tmpRepo_name} at {tmpRepo_full_name}.')
                msg = F'Repo {repoName} already exists in organization {orgName}. {tmpRepo_full_name}'
                print(msg)
                updateGithubIssue(msg, "open")
                exit()
            else:
                print(F'The repo exists with a different name {tmpRepo_name} at {tmpRepo_full_name}.  This is a renamed repo.')
        case 404:
            # repo not found
            msg = "Repo {} does not already exist in the organization. ".format(repoName)
            print(msg)
        case _:
            # error
            msg = "Error checking if repo already exists.  The repo was not created."
            print(msg)
            # github_message +=  msg + "\n"
            # updateGithubIssue(github_message, "open")
            updateGithubIssue(msg, "open")
            exit()
            
def createRepo(repoName, repoDesc, orgName): 
    print(F'Creating repo {repoName} ')
    url=F'https://api.github.com/orgs/{orgName}/repos' 
    variables='{"name":"' + repoName + '","description":"' + repoDesc + '","private":true}'
    res = requests.post(url, data=variables, headers=headers, timeout=10)
    status_code=res.status_code
    print(F'status_code = {status_code}')
    match status_code:
        case 201:
            # repo created
            msg = "Repo {} created.".format(repoName)
            print(msg)
            updateGithubIssue(msg, "open")
        case _:
            # error
            msg = "Error creating repo.  The repo was not created."
            print(msg)
            # github_message +=  msg + "\n"
            # updateGithubIssue(github_message, "open")
            updateGithubIssue(msg, "open")
            exit()

                
def main():
    """
    Main function
    """
    repo_event=os.environ["CREATE_REPO_EVENT"]
    print(F'repo_event= {repo_event}')
    
    repo_title=os.environ["CREATE_REPO_TITLE"]
    print(F'repo_title= {repo_title}')
    
    repo_number=os.environ["CREATE_REPO_NUMBER"]
    print(F'repo_number= {repo_number}')
    
    repo_message=os.environ["CREATE_REPO_MESSAGE"]
    print(F'repo_message= {repo_message}')
    
    issue_repo_url=os.environ["ISSUE_REPO_URL"]
    print(F'issue_repo_url {issue_repo_url}')
    
    repo_name=os.environ["REPO_NAME"]
    print(F'repo_name {repo_name}')
    
    repo_url=os.environ["REPO_URL"]
    print(F'repo_url {repo_url}')
           
    # parse message
    lines=repo_message.splitlines()
    linenum=0
    for line in lines:
        print("{}: {}".format(linenum, line))
        linenum += 1

    repoName = lines[2].strip()
    repoDesc = lines[6].strip()
    print(F'repoName {repoName}')
    print(F'repoDesc {repoDesc}')
    if repoDesc == '_No response_':
        repoDesc=''
        print(F'repoDesc changed to {repoDesc}.')


    # check for spaces in repo name
    if repoName.count(' ') > 0:
        print("The repository name contains spaces.")
        # Github will automatically convert spaces to -
        msg = F'The repository name {repoName} contains spaces.  Please submit a new request with a repository name that does not contain spaces. '
        print(msg)
        updateGithubIssue(msg, "open")
        exit()
    else:
        print("The repository name does not contain any spaces.")
        
    # check repo name < 100 chars 
    if len(repoName) > 100:
        print("The length of the repoName is greater than 100.")
        # Github has a max 100 character repo name limit
        msg = F'The repository name {repoName} is too long.  Github has a max 100 character repo name limit. '
        print(msg)
        updateGithubIssue(msg, "open")
        exit()
    else:
        print("The length of the repo name is not greater than 100.")

   
    # validate repo does not already exist
    checkRepoDoesNotExist(orgName, repoName)

    # create repo
    createRepo(repoName, repoDesc, orgName) 

    assignMember(orgName,actor,repoName)

    
    updateGithubIssue("Request completed.", 'closed')

if __name__ == '__main__':
  main()