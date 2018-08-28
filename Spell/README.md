-# Albert launcher spell extension


## Installation
Put extension into right location
```
~/.local/share/albert/org.albert.extension.python/modules/
```

## Preparing dependencies

Be sure that you have installed needed packages.
```bash
sudo apt install xclip aspell aspell-en aspell-pl aspell-de
```

## Additional dictionaries

All installed aspell language will be automatically used by this plugin. By default your system should have some languages already installed, like your current default system language. You can list all installed languages with command:
```bash
aspell dump dicts
```
If you need more languages just install them with:
```bash
audo apt install aspell-XX
```
where XX is your language iso code.

## Usage examples
```
spell en great
spell pl góra
spell de viel
```
