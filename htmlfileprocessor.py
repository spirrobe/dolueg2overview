#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def htmlfileprocessor(templatefile,
                      outputfile,
                      # defines how the codes are indicates in the html file
                      pattern=['[',']']
                      ):

    # FIX THESE IMPORT RELATIVE TO YOUR SETUP
    import socket
    from sql.util import getdata4html

    def codeextractor(line,pattern):
        code = line[line.index(pattern[0])+1:line.index(pattern[1])]

        # too short cant be a database code or other
        # valid code for getdata4html
        if 'unit' in code.lower() or len(code) <= 3:

            return pattern[0]+code[4*int('unit' in code.lower()):]+pattern[1]
        else:
            return getdata4html(code)

    with open(templatefile) as fo:
        lines = fo.readlines()

    skipping = False
    for lineno, line in enumerate(lines):
        # skip commented lines
        if line.startswith('#'):
           continue
        # sanity check for javascript in template file
        if '<script>' in line:
            skipping = True
        if '</script>' in line:
            skipping = False
        if skipping:
            continue

        if pattern[0] in line and pattern[1] in line:
            oline = ''
            for n in range(min([line.count(pattern[0]),
                                line.count(pattern[0])])):

                value = codeextractor(line, pattern)
                oline += line[:line.index(pattern[0])] + value
                line = line[line.index(pattern[1])+1:]

            lines[lineno] = oline + line

    with open(outputfile,'w') as fo:
        fo.writelines(lines)


if __name__ == '__main__':
    print('*'*10, 'HELP for htmlfileprocessor', '*'*10)
    print('Reads in a html file and replaces codes, i.e. things in square',
          'brackets according to getdata4html, i.e. getting times and data',
          'and adjusting them')
    print('Maybe help out a bit with keyword to make it clearer for people',)
#    main()
    a = htmlfileprocessor('/media/met-server0/AML/prog/idl/htm/template.txt',
                           '/home/spirro00/Desktop/current.html')
