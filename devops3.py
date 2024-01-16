from vsts.vss_connection import VssConnection
from vsts.git.v4_1.git_client import GitClient
from msrest.authentication import BasicAuthentication

# Variables de configuración
organization_url = 'https://dev.azure.com/codikasrl'
project_name = 'AFP Popular'
repository_id = '2bc4869b-ed57-4ac8-aab8-6fba86b63f41'
personal_access_token = 'wqshn2jieklvr7sbfrcy2kjr25itfr67ou24dbn5446uasoz5i4q'
branch_name='master'

# Crea la conexión con Azure DevOps
credentials = BasicAuthentication('', personal_access_token)
connection = VssConnection(base_url=organization_url, creds=credentials)

# Obtiene el cliente de Git de Azure DevOps
print(GitClient)

# Obtiene el cliente de Git de Azure DevOps
git_client = connection.get_client(GitClient)

# Obtiene las estadísticas de cloc para el repositorio o la rama especificados
if branch_name:
    # Si se especificó un nombre de rama, obtén la cantidad de líneas de código para la rama
    cloc_data = git_client.get_branch_stats(
        repository_id=repository_id,
        project=project_name,
        name=branch_name
    ).code_metrics
else:
    # Si no se especificó un nombre de rama, obtén la cantidad de líneas de código para todo el repositorio
    cloc_data = git_client.get_repository_code_metrics(
        repository_id=repository_id,
        project=project_name
    ).code_metrics

# Imprime la cantidad de líneas de código
print(f"El {(f'repositorio {repository_id}' if not branch_name else f'rama {branch_name}')} tiene {cloc_data.lines_of_code} líneas de código.")