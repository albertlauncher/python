# Unit Converter

Extension for converting units of length, mass, speed, temperature, time,
current, luminosity, printing measurements, molecular substance, and currency.

All units from the Pint Python library are supported.

Currency conversion rates are provided by <https://www.exchangerate-api.com>.

Examples:

`convert 180 minutes to hrs`

`convert 100 km to miles`

`convert 88 mph to kph`

`convert 32 degrees F to C`

`convert 3.14159 rad to degrees`

`convert 100 USD to EUR`

![demo 0.18](https://user-images.githubusercontent.com/20955511/211650412-b42412f3-c4d5-4d2a-8b77-05ff39fcb48e.gif)

## Install Requirements

Ensure that `Pint` and `inflect` are installed in `~/.local/share/albert/python/site-packages`.

```bash
pip install -U inflect==6.0.2 Pint==0.20.1 -t ~/.local/share/albert/python/site-packages
```
