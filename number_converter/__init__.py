# -*- coding: utf-8 -*-

"""Convert a number from one base to another.

You can insert a number and his base and get the same value in other bases.
Supported bases are: 2, 10 and 16.

Synopsis: <trigger> <base> <number>"""

from albert import *
import os

__title__ = 'Number converter'
__version__ = '0.4.0'
__triggers__ = 'conv '
__authors__ = 'mparati31'

iconPath = os.path.dirname(__file__) + '/icon.svg'
iconBinaryPath = os.path.dirname(__file__) + '/binary.svg'
iconDecimalPath = os.path.dirname(__file__) + '/decimal.svg'
iconHexPath = os.path.dirname(__file__) + '/hex.svg'

values = {
    '2': ['0', '1'],
    '10': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    '16': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
}

def check(base, num):
    for n in num:
        if n not in values[base]:
            return False
    return True

def handleQuery(query):
    if query.isTriggered:
        args = query.string.split()

        if len(args) != 2:
            return Item(id=__title__,
                    icon=iconPath,
                    text='Wrong number of arguments',
                    subtext=f'Correct syntax is: {__triggers__} base number')

        base, number = args

        if base not in values:
            return Item(id=__title__,
                    icon=iconPath,
                    text='Base value not valid',
                    subtext=f'Valid values are: {", ".join(list(values))}')

        if not check(base, number.upper()):
            return Item(id=__title__,
                    icon=iconPath,
                    text=f'Value not valid for base {base}',
                    subtext=f'Valid values are: {", ".join(list(values[base]))}')

        decimal = int(number, base=int(base))
        binary = format(decimal, 'b')
        hexa = format(decimal, 'x').upper()

        results = []

        if base != '2':
            results.append(
                Item(
                    id=__title__,
                    icon=iconBinaryPath,
                    text=f'Binary: {binary}',
                    subtext='Enter to copy',
                    actions=[ClipAction('Copy Exception to clipboard', str(binary))]
                )
            )

        if base != '10':
            results.append(
                Item(
                    id=__title__,
                    icon=iconDecimalPath,
                    text=f'Decimal: {decimal}',
                    subtext='Enter to copy',
                    actions=[ClipAction('Copy Exception to clipboard', str(decimal))]
                )
            )

        if base != '16':
            results.append(
                Item(
                    id=__title__,
                    icon=iconHexPath,
                    text=f'Hexadecimal: {hexa}',
                    subtext='Enter to copy',
                    actions=[ClipAction('Copy Exception to clipboard', str(hexa))]
                )
            )


        return results
