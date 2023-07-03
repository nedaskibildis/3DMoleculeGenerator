import MolDisplay;
import os;
import sqlite3;

class Database:
    # Init that removes database if reset is set to true
    def __init__(self, reset=False):
        if reset:
            os.remove("molecules.db")

        self.conn = sqlite3.connect("molecules.db")
    
    # Method That Creates All Tables Needed For The Database
    def create_tables( self ):
        # Create Elements Table
        self.conn.execute(""" CREATE TABLE IF NOT EXISTS Elements (
            ELEMENT_NO INTEGER NOT NULL,
            ELEMENT_CODE VARCHAR(3) PRIMARY KEY NOT NULL,
            ELEMENT_NAME VARCHAR(32) NOT NULL,
            COLOUR1 CHAR(6) NOT NULL,
            COLOUR2 CHAR(6) NOT NULL,
            COLOUR3 CHAR(6) NOT NULL,
            RADIUS DECIMAL(3)
        );""")
        # Create Atoms Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms (
            ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ELEMENT_CODE VARCHAR(3) NOT NULL,
            X DECIMAL(7,4) NOT NULL,
            Y DECIMAL(7,4) NOT NULL,
            Z DECIMAL(7,4) NOT NULL,
            FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements
        );""")
        # Create Bonds Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds (
            BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            A1 INTEGER NOT NULL,
            A2 INTEGER NOT NULL,
            EPAIRS INTEGER NOT NULL
        );""")
        # Create Molecules Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules(
            MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            NAME TEXT UNIQUE NOT NULL
        );""")
        # Create MoleculeAtom Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom(
            MOLECULE_ID INTEGER NOT NULL,
            ATOM_ID INTEGER NOT NULL,
            PRIMARY KEY(MOLECULE_ID, ATOM_ID)
            FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
            FOREIGN KEY (ATOM_ID) REFERENCES Atoms
        );""")
        # Create MoleculeBond Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond(
            MOLECULE_ID INTEGER NOT NULL,
            BOND_ID INTEGER NOT NULL,
            PRIMARY KEY(MOLECULE_ID, BOND_ID)
            FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
            FOREIGN KEY (BOND_ID) REFERENCES Bonds
        );""")
        self.conn.commit()
    
    def __setitem__( self, table, values):
        # Create a list where all the values are the same, but as strings instead of other data types
        valuesAsStrings = [];
        for value in values:
            valuesAsStrings.append(str(value))
        # Creates a string filled with ? based off how many values must be inserted into the table
        newValues = ",".join(['?' for value in valuesAsStrings])
        # Create a string and execute the insert
        parameterString = f"INSERT INTO {table} VALUES({newValues})"
        self.conn.execute(parameterString, valuesAsStrings)
        self.conn.commit()

    def add_atom( self, molname, atom):
        # Create a list of elements data and insert it into Atoms Table
        data1 = (atom.element, atom.x, atom.y, atom.z)
        self.conn.execute(""" INSERT
        INTO Atoms(ELEMENT_CODE, X, Y, Z)
        VALUES (?,?,?,?);""", data1)

        # Create cursor so that I can access values selected using fetch
        cursor = self.conn.cursor()

        cursor.execute(f"""SELECT MOLECULE_ID FROM Molecules WHERE NAME = "{molname}";""");
        molID = cursor.fetchone()
        cursor.execute("SELECT ATOM_ID FROM Atoms ORDER BY rowid DESC LIMIT 1")
        atomID = cursor.fetchone()[0]
        
        data2 = (molID[0], atomID)

        # Pass Molecule ID and Atom Id into MoleculeAtom Table
        self.conn.execute(""" INSERT 
        INTO MoleculeAtom(MOLECULE_ID, ATOM_ID)
        VALUES(?,?);""", data2)
        self.conn.commit()

    def add_bond( self, molname, bond):
        # This function uses the exact same concept as the above function, but for the bond tables instead of the atoms tables
        data1 = (bond.a1, bond.a2, bond.epairs)
        self.conn.execute(""" INSERT
        INTO Bonds(A1, A2, EPAIRS)
        VALUES(?,?,?);""", data1);

        cursor = self.conn.cursor()

        cursor.execute(f"""SELECT MOLECULE_ID FROM Molecules WHERE NAME = "{molname}";""")
        molID = cursor.fetchone()
        cursor.execute("SELECT BOND_ID FROM Bonds ORDER BY rowid DESC LIMIT 1")
        bondID = cursor.fetchone()[0]

        data2 = (molID[0], bondID)

        self.conn.execute(""" INSERT 
        INTO MoleculeBond(MOLECULE_ID, BOND_ID)
        VALUES(?,?);""", data2)
        self.conn.commit
    
    def add_molecule(self, name, fp):
        # Create new molecule and parse the file pointer
        newMolecule = MolDisplay.Molecule()
        newMolecule.parse(fp)
        # Pass the new Molecule Into Molecules Table
        self.conn.execute(f"""INSERT
        INTO Molecules(NAME)
        VALUES("{name}");""")

        # For loops that add the respectful atoms and bonds to the molecule
        for i in range(newMolecule.atom_no):    
            self.add_atom(name, newMolecule.get_atom(i))
        for i in range(newMolecule.bond_no):
            self.add_bond(name, newMolecule.get_bond(i))

        self.conn.commit()
    
    def load_mol(self, name):
        # Create Cursor for fetch commands and a new molecule to return
        cursor = self.conn.cursor()
        # cursor = self.conn.cursor()
        newMol = MolDisplay.Molecule()
        newMol.atom_no = 0;
        # Select Statement That gets atom info from atoms where atom_id matches molecule_id and molecule_id name is the one passed in and then turns it into a list
        cursor.execute(f"""SELECT Atoms.ELEMENT_CODE,Atoms.X,Atoms.Y,Atoms.Z
        FROM Atoms
        INNER JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
        INNER JOIN Molecules ON MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
        WHERE Molecules.NAME = "{name}"
        ORDER BY Atoms.ATOM_ID 
        ;""")
        listOfAtoms = cursor.fetchall();

        # Same as above but for bonds instead of atoms
        cursor.execute(f"""SELECT Bonds.A1, Bonds.A2, Bonds.EPAIRS
        FROM Bonds
        INNER JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
        INNER JOIN Molecules ON MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
        WHERE Molecules.NAME = "{name}"
        ORDER BY Bonds.BOND_ID 
        ;""")
        listOfBonds = cursor.fetchall();
        # For loops that append atoms and bonds to the new molecule 
        for atom in listOfAtoms:
            newMol.append_atom(atom[0], atom[1], atom[2], atom[3])
        for bond in listOfBonds:
            newMol.append_bond(bond[0], bond[1], bond[2])
        
        return newMol
        
    def radius(self):

        cursor = self.conn.cursor()
        radiusDictionary = {}
        # Get every element code and radius from elements
        cursor.execute("""SELECT
        ELEMENT_CODE, RADIUS
        FROM Elements""")
        listOfElements = cursor.fetchall();

        # For loops that maps each element code to its radius
        for element in listOfElements:
            radiusDictionary[element[0]] = element[1]

        return radiusDictionary
    
    def element_name(self):

        cursor = self.conn.cursor()
        nameDictionary = {}
        # Get every element code and name from elements
        cursor.execute("""SELECT
        ELEMENT_CODE, ELEMENT_NAME
        FROM Elements""")
        listOfElements = cursor.fetchall();
        # For loop that maps each element to its element name
        for element in listOfElements:
            nameDictionary[element[0]] = element[1]
        
        return nameDictionary
    
    def radial_gradients(self):
        cursor = self.conn.cursor()

        radialString = """
            <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
            <stop offset="0%%" stop-color="#%s"/>
            <stop offset="50%%" stop-color="#%s"/>
            <stop offset="100%%" stop-color="#%s"/>
            </radialGradient>"""
        stringToReturn = ""

        # Select Every Row From the elements table, and then concatonate the element Name and 3 colours for each element in the table
        cursor.execute("""SELECT * FROM Elements;""")
        elementList = cursor.fetchall();
        for element in elementList:
            gradient = radialString % (element[2], element[3], element[4], element[5])
            stringToReturn += gradient

        return stringToReturn
    
    def add_element(self, listToPass):
        cursor = self.conn.cursor()
        cursor.execute("""INSERT
        INTO Elements(ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS)
        VALUES (?,?,?,?,?,?,?);""", listToPass)
    
    def remove_element(self, listToPass):
        cursor = self.conn.cursor()
        cursor.execute("""DELETE FROM Elements WHERE ELEMENT_NAME = ?;""", listToPass)
