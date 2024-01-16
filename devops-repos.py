from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.git.models import GitRepositoryStats
import requests
import pprint

# Conexión al servicio de Azure DevOps
personal_access_token = 'wqshn2jieklvr7sbfrcy2kjr25itfr67ou24dbn5446uasoz5i4q'
organization_url = 'https://dev.azure.com/codikasrl'

credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)


# Get a client (the "core" client provides access to projects, teams, etc)
core_client = connection.clients.get_core_client()
# statistics_client = connection.clients.get_statistics_client()

# Get the first page of projects
get_projects_response = core_client.get_projects()
index = 0

while get_projects_response is not None:
    for project in get_projects_response.value:
        pprint.pprint(f"Proyecto: {project.name}")
        pprint.pprint(f"Proyecto ID: {project.id}")
        index += 1
        git_client = connection.clients.get_git_client()
        repos = git_client.get_repositories(project.id)

        for repo in repos:
            print(f"\tRepositorio: {repo.name}")
            print(f"\tRepositorio ID: {repo.id}")
            print(repo)
            repo_stats = git_client.get_repository_statistics(project.id, repo.id)
            print(repo_stats)

    if get_projects_response.continuation_token is not None and get_projects_response.continuation_token != "":
        # Get the next page of projects
        get_projects_response = core_client.get_projects(continuation_token=get_projects_response.continuation_token)
    else:
        # All projects have been retrieved
        get_projects_response = None


# # # Obtener todos los proyectos
# core_client = connection.clients.get_core_client()
# projects = core_client.get_projects()
# get_projects_response = core_client.get_projects()

# for project in projects:
#     git_client = connection.clients.get_git_client()
#     repos = git_client.get_repositories(project.id)
    
#     for repo in repos:
#         print(f"\tRepositorio: {repo.name}")
#         repo_stats = git_client.get_repository_statistics(project.id, repo.id)

#         for stat in repo_stats:
#             if isinstance(stat, GitRepositoryStats):
#                 print(f"\t\tCommits: {stat.active_pull_requests_count}")
#                 print(f"\t\tLines of Code: {stat.lines_of_code}")
