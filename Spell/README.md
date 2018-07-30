-# Albert launcher spell extension


## Installation
Put extension into right location
```
~/.local/share/albert/org.albert.extension.python/modules/
```

## Preparing additional dictionaries

Be sure that you have installed needed packages.
```bash
sudo apt install xclip aspell aspell-en aspell-pl aspell-de
```
Dump dictionary of any language you need.
```bash
aspell -l en dump master | aspell -l en expand | gzip -c > ~/.local/share/albert/org.albert.extension.python/modules/Spell/dictionaries/en.gz
aspell -l pl dump master | aspell -l pl expand | gzip -c > ~/.local/share/albert/org.albert.extension.python/modules/Spell/dictionaries/pl.gz
aspell -l de dump master | aspell -l de expand | gzip -c > ~/.local/share/albert/org.albert.extension.python/modules/Spell/dictionaries/de.gz

```
## Usage examples
```
spell en great
spell pl góra
spell de viel
```
