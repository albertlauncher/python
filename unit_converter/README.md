# unit-converter

Extension for converting units of length, mass, speed, temperature, time, current, luminosity, printing measurements, molecular substance, currency, and more.

![demo 0.18](https://user-images.githubusercontent.com/20955511/211650412-b42412f3-c4d5-4d2a-8b77-05ff39fcb48e.gif)

## Install Requirements

Ensure that `Pint` and `inflect` are installed in `~/.local/share/albert/python/site-packages`.

```bash
pip install -U inflect==6.0.2 Pint==0.20.1 -t ~/.local/share/albert/python/site-packages
```

## Usage

Type the trigger, followed by the amount and unit, the word "to" or "in", and then the unit you want to convert to.

`<trigger> <amount> <from_unit> {to|in} <to_unit>`

Examples:

`convert 180 minutes to hrs`

`convert 100 km to miles`

`convert 88 mph to kph`

`convert 32 degrees F to C`

`convert 3.14159 rad to degrees`

`convert 100 EUR to USD`

## Configuration

In `config.jsonc` there are options to customize the behavior of the extension:

### Rounding Precision

The `rounding_precision` option controls how many decimal places the result will be rounded to. By default, this is 3.

The `rounding_precision_zero` option controls how many decimal places the result will be rounded to when the result is close to zero. By default, this is 12.

### Aliases

To add an alias for a unit, add a key-value pair to the `aliases` object.

Example: `"sec": "second"` allows you to type `sec` instead of `second`.

Many aliases are already supported.

### Display Names

If the display name of a unit seems strange, you can override it by adding a key-value pair to the `display_names` object.

Example: `"degree_Celsiuses": "°C"` will make the displayed result appear as `32 °C` instead of `32 degree_Celsiuses`.
