from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

# Variables de configuración
organization_url = 'https://dev.azure.com/codikasrl'
project_name = 'AFP Popular'
repository_id = '2bc4869b-ed57-4ac8-aab8-6fba86b63f41'
personal_access_token = 'wqshn2jieklvr7sbfrcy2kjr25itfr67ou24dbn5446uasoz5i4q'
branch_name='master'

# Crea la conexión con Azure DevOps
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Obtiene el cliente de Git de Azure DevOps
git_client = connection.clients.get_git_client()

git_client

# Obtiene las estadísticas de la rama especificada
branch_stats = git_client.get_branch_stats(
    project=project_name, 
    repository_id=repository_id, 
    name=branch_name
)

# Obtiene el objeto de datos de cloc para la rama
cloc_data = branch_stats.code_metrics

# Imprime la cantidad de líneas de código
print(f"La rama {branch_name} tiene {cloc_data.lines_of_code} líneas de código.")