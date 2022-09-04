import argparse
import re
#for sovol-so2, F is speed, S is laser intensity with 1000 being max



def getParams(lines):
    matches = sum([re.findall("(#[0-9]+) ?= ?(\-?[0-9\.]+)", line) for line in lines], [])
    return {match[0]: float(match[1]) for match in matches}

def multBrackets(match):
    inches_to_mm = 25.4
    return str(float(match.group(1))*float(match.group(2))*inches_to_mm)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Fixes the GCode of a boxes.py box to work with sovol-SO2 (removes variables)')
    parser.add_argument('input', help='Input gcode file')
    parser.add_argument('--output', help='Output gcode file')
    parser.add_argument('--speed', help='How many mm/min to go', default=300, type=float)

    args = parser.parse_args()

    preamble = f"M4 F{args.speed}"
    postamble = "M5"

    if args.output is None:
        args.output = args.input+'FIXED'


    with open(args.input, 'r') as f:
        text = f.read()
        sections = text.split("\n\n")
        params = getParams(sections[0].split("\n"))
        print(params)

        for i, section in enumerate(sections):
            if i==0:
                continue
            lines = section.split("\n")
            for j in range(len(lines)):
                line = lines[j]
                for key in params:
                    line = line.replace(key, str(params[key]))
                    line = re.sub(r"\[(\-?[0-9\.]+) ?\* ?(\-?[0-9\.]+)\]", multBrackets, line)
                lines[j] = line
            sections[i] = "\n".join(lines)+'\n'
        print(sections[1])
        lines = [preamble]+sum([x.split('\n') for x in sections[1:]], [])+[postamble]
        
        for i, line in enumerate(lines):
            if 'G00' in line:
                lines[i] = f'S0\n{line}\nS1000'
            
        with open(args.output, 'w') as f:
            f.write("\n".join(lines))



