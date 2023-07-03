#!/usr/bin/python3
import molecule;
import re;

# Variable Declarations Provided

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">""";
footer = """</svg>""";

offsetx = 500;
offsety = 500;

# Atom Class
class Atom:
    
    # Initialize function, idk how to do it yet
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z

    #String Method That Prints The Atoms element name, x, y, and z coordinates.
    def __str__(self):
        return f"{self.atom.element}, {self.atom.x}, {self.atom.y}, {self.atom.z}"
    
    # SVG Calculation
    def svg(self):
            return ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (self.atom.x * 100 + offsetx, self.atom.y * 100 + offsety, radius[self.atom.element], element_name[self.atom.element])

# Bond Class
class Bond:

    # Initialize everything to the bond that is passed in
    def __init__(self, c_bond):
        self.bond = c_bond
        self.z = c_bond.z

    # Print The Info Of The 2 Atoms That it is connected to as well as the number of epairs to debug
    def __str__(self):
        return f'dX: {self.bond.dx} dY: {self.bond.dy}\nAtom 1 Info:\nX1: {self.bond.x1} Y1: {self.bond.y1}\nAtom 2 Info:\nX2: {self.bond.x2} Y2: {self.bond.y2}\n \nNumber Of Epairs: {self.bond.epairs}'
    
    # Calculate The center of the bond and then move 10 pixels perpindicular in each direction and return the svg
    def svg(self):
        x1center = self.bond.x1 * 100 + offsetx
        x2center = self.bond.x2 * 100 + offsetx
        y1center = self.bond.y1 * 100 + offsety
        y2center = self.bond.y2 * 100 + offsety
        a1p1x = x1center - self.bond.dy*10
        a1p1y = y1center + self.bond.dx*10
        a1p2x = x1center + self.bond.dy*10
        a1p2y = y1center - self.bond.dx*10
        a2p1x = x2center + self.bond.dy*10
        a2p1y = y2center - self.bond.dx*10
        a2p2x = x2center - self.bond.dy*10
        a2p2y = y2center + self.bond.dx*10
    

        return ' <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (a1p1x, a1p1y, a1p2x, a1p2y, a2p1x, a2p1y, a2p2x, a2p2y)


class Molecule(molecule.molecule):

    # Print Every Atom and bond for debugging
    def __str__(self):
        stringToReturn = ''
        for i in range(self.atom_no):
            atomToPrint = Atom(self.get_atom(i))
            stringToReturn += f'Atom {i + 1}:\n Name: {atomToPrint.element}, X Coordinate: {atomToPrint.x}, Y Coordinate: {atomToPrint.y}, Z Coordinate {atomToPrint.z}\n'
        for i in range(self.bond_no):
            bondToPrint = Bond(self.get_bond(i))
            atom1 = Atom(self.get_atom(bondToPrint.a1))
            atom2 = Atom(self.get_atom(bondToPrint.a2))
            stringToReturn += f'Bond {i+1}\n Bond {i + 1} is pointing to a {atom1.element} atom and atom {atom2.element}\n This Bond Contains {bondToPrint.epairs} epairs\n The First Atom is located at {bondToPrint.x1},{bondToPrint.y1}\n The Second Atom is located at {bondToPrint.x2},{bondToPrint.y2}\n The dX and Dy of these atoms are {bondToPrint.dx},{bondToPrint.dy}\n This bond has a length of {bondToPrint.len}\n'
        
        return stringToReturn
    
    # SVG Function To Combine the atom and bond SVGs for the molecule
    def svg(self):
        stringToReturn = header
        i = 0;
        j = 0;
        # Compare Both Values and only increase the index of the one that has the lesser Z value
        while(i < self.atom_no and j < self.bond_no):
            atomToComp = Atom(self.get_atom(i))
            bondToComp = Bond(self.get_bond(j))
            if (atomToComp.z < bondToComp.z):
                stringToReturn += atomToComp.svg()
                i+= 1
            else:
                stringToReturn += bondToComp.svg()
                j+= 1
        # Loop to copy the rest of the atoms svgs if there were any left over
        while (i < self.atom_no):
            atomToComp = Atom(self.get_atom(i))
            stringToReturn += atomToComp.svg()
            i+= 1
        # Same as above but for bonds
        while (j < self.bond_no):
            bondToComp = Bond(self.get_bond(j))
            stringToReturn += bondToComp.svg()
            j+= 1 
        stringToReturn += footer
        return stringToReturn

    def parse(self, fp):
        # Read first 4 Headers
        atomCount = 0;
        bondCount = 0;
        numHeaders = 0
        i = 0
        
        header = fp.read()
        
            # Skip over first four headers
        header = header.split('\n', 4)[-1]
            # Copy rest of string after 4 headers, create a molecule and then parse and create the svg

        # Regex Pattern to Find every atom in the SDF File and create a list of it
        atomPattern = re.compile(r"\s+-*\d.\d+\s+-*\d.\d+\s+-*\d.\d+\s+[a-z A-Z]*[a-z A-Z]")
        listOfAtoms = atomPattern.findall(header)
        # Same as above but for bonds
        bondPattern = re.compile(r"(?<!\d)([1-9]|[1-9][0-9])\s+([1-9]|[1-9][0-9])\s+(0?[1-9]|[1-9][0-9])")
        listOfBonds = bondPattern.findall(header)
        # for loop that extracts every atom into a list and then appends the atoms info to molecule
        for atom in listOfAtoms:
            extractionPattern = re.compile(r"\s+-*\d+\.\d+")
            elementPattern = re.compile(r"[a-zA-z]")
            elementName = elementPattern.findall(atom)
            atomsCoords = extractionPattern.findall(atom)
            xCoord = float(atomsCoords[0])
            yCoord = float(atomsCoords[1])
            zCoord = float(atomsCoords[2])
            self.append_atom(elementName[0], xCoord, yCoord, zCoord)
        # Same as above but for bond
        for bond in listOfBonds:
            extractionPattern = re.compile(r"\d+")
            bondInfo = extractionPattern.findall(str(bond))
            self.append_bond(int(bondInfo[0]) - 1,int(bondInfo[1]) - 1, int(bondInfo[2]))
