# v.api
## Requisitos
> - Visual Studio Code <br>
> - Python 3.7.x <br>
> - Google Cloud <br>

## Criando um virtual enviroment em Python
> Criamos o virtual enviroment(venv) e o ativamos em um terminal com os comandos:
```bash
python -m venv venv 
source /venv/bin/activate
```
> Caso queira sair do virtual enviroment use o comando ```deactivate```<br>

## Instalando as dependencias
> Instalamos as dependencias do software com o seguinte comando:
```bash
pip install --upgrade google-cloud-translate google-cloud-texttospeech google-cloud-speech requests flask
```
> Lembre-se de se autenticar no Google Cloud exportando a sua chave de serviço para a variável de ambiente ```GOOGLE_APPLICATION_CREDENTIALS```
<br>

## Iniciando o backend 
> Dentro do virtual enviroment, ussamos o seguinte comando para iniciar o backend:
```bash
flask run
```

> Se for preciso encerrar a aplicação, usa-se: Ctrl + C<br>
