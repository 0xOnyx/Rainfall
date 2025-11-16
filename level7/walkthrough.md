# Level 7 Walkthrough

## Understanding the Binary

The binary reads the password for `level8` from a file and stores it in a global variable `c`. There is also a function
`m` that prints the contents of `c`, but this function is never called directly. However, the binary is vulnerable to a
buffer overflow because it uses the unsafe `strcpy` function to fill two buffers. At the end of the `main` function,
there is a call to `puts`, so we can overwrite the address of `puts` in the Global Offset Table (GOT) with the address
of `m`. This way, when the program calls `puts`, it will actually call `m`, printing the contents of `c`.

## Understanding the Vulnerability

The `strcpy` function is used to copy user input as follows:
- `argv[1]` is copied to `buffer_heap_1[1]`, which has a length of eight bytes.
- `argv[2]` is copied to `buffer_heap_2[1]`, which also has a length of eight bytes.

If the user provides more than eight bytes of input in either argument, the program will overflow the buffer and
overwrite other memory locations.

## Heap Structures
`main` allocates four 8-byte chunks:
```
struct node {
  int tag;     // 1 or 2
  char *ptr;   // points to another malloc(8)
};
```
Sequence:
1. Allocate node A (`tag=1`) and node B (`tag=2`).
2. Allocate buffers (8 bytes each) referenced by A->ptr and B->ptr.
3. `strcpy(A->ptr, argv[1])`.
4. `strcpy(B->ptr, argv[2])`.
5. Read `/home/user/level8/.pass` into global `c`.
6. `puts("~~")`.

Function `m()` (unused) prints the time + contents of `c`. We want `puts` to call `m()` instead.

## Exploit Idea
- `strcpy` on `argv[1]` can overflow the buffer behind A->ptr and reach into the next heap structure (node B).
- Node B stores the pointer that `strcpy` uses for `argv[2]`. By overwriting B->ptr with a GOT address, the second
`strcpy` writes arbitrary data to that GOT entry.
- Choose `puts@GOT` (`0x8049928`) as the target and overwrite it with the address of `m()` (`0x080484f4`).

## Calculating Offsets
GDB shows the difference between the two buffers is 0x10 bytes, so after 20 bytes (16 + 4) we reach the pointer field of
the next node.

```
argv1 = "A"*20 + p32(0x8049928)
argv2 = p32(0x080484f4)
```

When `strcpy(B->ptr, argv[2])` executes, it writes our fake function pointer into `puts@GOT`. Later, `puts("~~")` jumps
into `m()`, which prints the flag plus timestamp.

## Execution
```bash
$ ./level7 $(python3 -c 'import sys,struct; sys.stdout.buffer.write(b"A"*20 + struct.pack("<I", 0x8049928))') \
            $(python3 -c 'import sys,struct; sys.stdout.buffer.write(struct.pack("<I", 0x080484f4))')
5684af5cb4c8679958be4abe6373147ab52d95768e047820bf382e44fa8d8fb9
```

## Notes
- NX is disabled, but this GOT overwrite technique is more reliable.
- Ensure arguments do not contain null bytes before the pointer overwrite (use little-endian packing of addresses
without zeros in the high byte).

