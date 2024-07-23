from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import requests
import json
from datetime import datetime, timedelta

# Variables de configuración
organization_url = 'https://dev.azure.com/codikasrl'
project_name = 'AFP Popular'
repository_id = '2bc4869b-ed57-4ac8-aab8-6fba86b63f41'
personal_access_token = 'wqshn2jieklvr7sbfrcy2kjr25itfr67ou24dbn5446uasoz5i4q'

# Crea la conexión con Azure DevOps
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Obtiene el cliente de Git de Azure DevOps
git_client = connection.clients.get_git_client()

# Obtiene información sobre el repositorio
repository = git_client.get_repository(repository_id)

# Especifica el rango de fecha para obtener estadísticas de líneas de código
start_date = datetime.utcnow() - timedelta(days=7)
end_date = datetime.utcnow()

# Construye la URL de la API para obtener estadísticas del repositorio
stats_url = f"{organization_url}/{project_name}/_apis/git/repositories/{repository.id}/stats/lines?startLine=1&endLine=-1&startDate={start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}&endDate={end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"

# Hace una solicitud GET a la URL de la API para obtener estadísticas del repositorio
response = requests.get(stats_url, auth=("", personal_access_token))

# Analiza la respuesta JSON para obtener la cantidad de líneas de código
stats = response.json()
total_lines = stats['value']

# Imprime la cantidad de líneas de código
print(f"El repositorio {repository.name} tiene {total_lines} líneas de código en la última semana.")