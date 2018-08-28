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
All installed aspell language will be automatically used by this plugin. Some languages aree installed in your system by default. If you need more just install them with:
```
audo apt install aspell-XX
```
where XX is language iso code.

## Usage examples
```
spell en great
spell pl góra
spell de viel
```