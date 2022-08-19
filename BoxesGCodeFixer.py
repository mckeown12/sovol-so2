import argparse
import re

parser = argparse.ArgumentParser(description='Fixes the GCode of a boxes.py box to work with sovol-SO2 (removes variables)')
parser.add_argument('input', help='Input gcode file')
args = parser.parse_args()


def getParams(lines):
    matches = sum([re.findall("(#[0-9]+) = ([0-9\.]+)", line) for line in lines], [])
    return {match[0]: float(match[1]) for match in matches}


with open(args.input, 'r') as f:
    text = f.read()
    sections = text.split("\n\n")
    params = getParams(sections[0].split("\n"))

    # for section in sections[1:]:
    #     lines = section.split("\n")
    #     for j in range(len(lines)):
    #         line = lines[j]
    #         for key in params:
    #             line = line.replace(key, str(params[key]))
    #         lines[j] = line
    #     sections[i] = "\n".join(lines)





print(getParams(lines))