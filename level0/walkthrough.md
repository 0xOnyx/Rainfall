# Level 0 Walkthrough

## 1. Program Analysis
The binary takes a single command-line argument, converts it with `atoi`, and compares the result against `0x1a7` (`423` decimal). Matching the comparison keeps the execution inside the “win” path, which eventually reaches `system("/bin/sh")`.

### Decompilation with GDB
```bash
$ gdb ./level0
(gdb) b *main
(gdb) run
(gdb) x/20i $eip
```

### Important Assembly Instructions
```asm
0x8048ed4 <main+20>:    call   0x8049710 <atoi>        ; convert argv[1]
0x8048ed9 <main+25>:    cmp    eax, 0x1a7              ; 0x1a7 == 423
0x8048ede <main+30>:    jne    0x8048f58 <main+152>    ; jump away on mismatch
```
If the comparison succeeds, execution flows through several calls (format string, banner, `system("/bin/sh")`). Otherwise the jump discards us.

## 2. Vulnerability Analysis
1. No validation is performed on the integer except the equality check.
2. `atoi` accepts decimal strings only; any other base will fail the comparison.
3. Providing `423` makes `cmp` succeed, so the `jne` is not taken and we stay on the privileged branch.

## 3. Exploitation

### Convert the Target Value
```bash
$ python3 -c "print(int('0x1a7', 16))"
423
```

### Trigger the Success Path
```bash
$ ./level0 423
Good... wait what?
$ id
```
Once the program spawns a shell (running as `level1`), we can read the next password.

## 4. Flag Retrieval
```bash
$ cat /home/user/level1/.pass
```

## 5. Key Points
- Recognize direct comparisons in disassembly and convert hex literals to decimal quickly.
- `jne` is the only gatekeeper; ensuring the zero flag remains set is enough to win.
- GDB is useful to confirm control flow and to set breakpoints around `cmp/jne`.
