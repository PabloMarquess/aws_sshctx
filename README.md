# EC2 Connect via EICE (sshctx tool)

sshctx tool é um script criado para realizar acessos via EC2 Instance Connect Endpoint `eice` com fuzzy finder `fzf`.

![info-video](docs/cli-sshctx.gif)


## Pré-requisitos

🐍 [Python 3.x](https://www.python.org/downloads/)
📦 [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
📦 [boto3](https://aws.amazon.com/pt/sdk-for-python/)
📦 [fzf](https://github.com/junegunn/fzf)


## Configurações

Mova o [sshctx.py](https://github.com/PabloMarquess/sshctx/blob/main/sshctx.py) para algum diretorio.

```console
$ ./path/to/sshctx.py
```
Crie um alias.

```console
cat <<EOF >> ~/.zshrc
alias sshctx='/path/to/sshctx.py'
EOF
```

### CLI

```console
USO:
    $ sshctx [INSTANCE_IDENTIFIER] [USER]

INSTANCE_IDENTIFIER:
    - <instance-ip>
        Acesso via IP Privado
    - <instance-id>
        Acesso via ID da Instância
    - <instance-name>
        Acesso via Nome da Instância
USERS:
    - <root>
    - <ec2-user>
    - <ubuntu>
