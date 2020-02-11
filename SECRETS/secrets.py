import os

def set_secret(secret_name, secret):
    with open(os.path.join(os.getcwd(),'SECRETS',f'{secret_name}.sec'),'wb') as f:
        f.write(secret)
def get_secret(secret_name):
    with open(os.path.join(os.getcwd(),'SECRETS',f'{secret_name}.sec'),'rb') as f:
        return f.readline()