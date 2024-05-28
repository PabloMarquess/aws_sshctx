import boto3
import subprocess
import sys

# Inicializa o cliente EC2
ec2 = boto3.client('ec2')

# Função para obter todas as instâncias com paginação
def get_all_instances():
    paginator = ec2.get_paginator('describe_instances')
    instances = []
    for page in paginator.paginate():
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
                    instance_info = {
                        'Name': name,
                        'InstanceId': instance['InstanceId'],
                        'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A').ljust(15)
                    }
                    instances.append(instance_info)
    return instances

# Função para selecionar uma instância usando fzf
def select_instance(instances):
    sorted_instances = sorted(instances, key=lambda x: x['Name'])
    instance_list = [
        f"[ {instance['InstanceId']} | {instance['PrivateIpAddress']}] - {instance['Name']}"
        for instance in sorted_instances
    ]
    fzf = subprocess.Popen(['fzf', '--prompt', 'Selecione a instância: '], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    fzf_input = "\n".join(instance_list).encode('utf-8')
    fzf_output, _ = fzf.communicate(input=fzf_input)
    selected_instance = fzf_output.decode('utf-8').strip()

    if selected_instance:
        instance_id = selected_instance.split('|')[0].strip('[] ').strip()
        return instance_id
    else:
        return None

# Função para selecionar um usuário usando fzf
def select_user():
    users = ['ubuntu', 'ec2-user', 'root']
    fzf = subprocess.Popen(['fzf', '--prompt', 'Selecione o usuário: '], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    fzf_input = "\n".join(users).encode('utf-8')
    fzf_output, _ = fzf.communicate(input=fzf_input)
    selected_user = fzf_output.decode('utf-8').strip()
    return selected_user

# Função para obter o IP privado da instância
def get_instance_private_ip(instance_id):
    response = ec2.describe_instances(InstanceIds=[instance_id])
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            return instance.get('PrivateIpAddress', 'N/A')
    return 'N/A'

# Função para tentar a conexão com um usuário específico
def try_connect(instance_id, os_user):
    if instance_id:
        instance_ip = get_instance_private_ip(instance_id)
        if instance_ip == 'N/A':
            print(f"Não foi possível obter o IP privado para a instância {instance_id}")
            return False
        command = f"aws ec2-instance-connect ssh --instance-id {instance_id} --instance-ip {instance_ip} --os-user {os_user} --connection-type eice"
        result = subprocess.run(command, shell=True)
        return result.returncode == 0
    else:
        return False

# Obtém todas as instâncias
instances = get_all_instances()

# Verifica se um nome de instância, ID ou IP foi passado como argumento
if len(sys.argv) > 1:
    instance_identifier = sys.argv[1]
    matching_instance = next(
        (instance for instance in instances if instance_identifier in (instance['Name'], instance['InstanceId'], instance['PrivateIpAddress'].strip())),
        None
    )
    if matching_instance:
        selected_instance_id = matching_instance['InstanceId']
    else:
        print(f"Instância com identificador '{instance_identifier}' não encontrada.")
        sys.exit(1)
else:
    # Permite a seleção da instância
    selected_instance_id = select_instance(instances)
    if not selected_instance_id:
        print("Nenhuma instância selecionada.")
        sys.exit(1)

# Verifica se um usuário foi passado como argumento
if len(sys.argv) > 2:
    selected_user = sys.argv[2]
else:
    # Permite a seleção do usuário
    selected_user = select_user()

print(f"conectando...")

# Tenta a conexão com o usuário selecionado
if not try_connect(selected_instance_id, selected_user):
    print(f"Falha ao conectar à instância {selected_instance_id} com o usuário '{selected_user}'. Usuário inválido.")