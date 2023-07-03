#include "mol.h"


void atomset( atom *atom, char element[3], double *x, double *y, double *z ) {
    // Set Name Of Atom Equal To Name Passed In
    strcpy(atom->element, element);
    // Copy Pointers Passed In Into Coordinates Of Atom
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
    // Set Element Equal to Element Name Of Atom
    strcpy(element, atom->element);
    // Set Coordinates equal to atom coordinates
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom
**atoms, unsigned char *epairs ) {

    bond->a1 =  *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;
    compute_coords(bond);
}

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom
**atoms, unsigned char *epairs ) {
    // copy atoms and epairs to pointers to atoms and bonds
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
    *atoms = bond->atoms;
}

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    // Return NULL IF negative values for atom max or bond max are passed in
    if (atom_max < 0 || bond_max < 0) {
        printf("ERROR, ATOM_MAX AND BOND_MAX MUST BE INITIALIZED TO AT LEAST 1\n");
        return NULL;
    }
    molecule* newMolecule = malloc(sizeof(molecule));
    // return null if malloc fails
    if (newMolecule == NULL) {
        printf("ERROR, MALLOC FAILED\n");
        return NULL;
    }
    
    // Initial copy of values from params and initilization of arrays
    newMolecule->atom_max = atom_max;
    newMolecule->atom_no = 0;
    if (atom_max == 0 ) {
        newMolecule->atoms = malloc(sizeof(atom));
        newMolecule->atom_ptrs = malloc(sizeof(atom*));
    } else {
        newMolecule->atoms = malloc(sizeof(atom) * atom_max);
        newMolecule->atom_ptrs = malloc(sizeof(atom*) * atom_max);
    }
    newMolecule->atom_ptrs[0] = &newMolecule->atoms[0];

    newMolecule->bond_max = bond_max;
    newMolecule->bond_no = 0;
    if (bond_max == 0) {
        newMolecule->bonds = malloc(sizeof(bond));
        newMolecule->bond_ptrs = malloc(sizeof(bond*));
    } else {
        newMolecule->bonds = malloc(sizeof(bond) * bond_max);
        newMolecule->bond_ptrs = malloc(sizeof(bond*) * bond_max);
    }
    newMolecule->bond_ptrs[0] = &newMolecule->bonds[0];


    return newMolecule;
}

molecule *molcopy(molecule *src) {  
    // Allocate memory for new molecule 
    molecule *newMol = molmalloc(src->atom_max, src->bond_max);

    // return NULL if malloc fails
    if (newMol == NULL) {
        return NULL;
    }
    
    // For loops to append atoms and bonds to copy of molecule
    for (int i = 0;  i < src->atom_no; i++) {
        molappend_atom(newMol, &src->atoms[i]);  
    }
    for (int i = 0;  i < src->bond_no; i++) {
        molappend_bond(newMol, &src->bonds[i]);  
    }

    // Return New Molecule
    return newMol;
}

void molfree(molecule *ptr) {
    // Frees The 1D Arrays
    free(ptr->atoms);
    free(ptr->bonds);

    // Frees The Double Pointer
    free(ptr->bond_ptrs);
    free(ptr->atom_ptrs);

    // Frees the pointer itself
    free(ptr);
}

void molappend_atom(molecule *molecule, atom *atom) {
    // Exits if null molecule or null atoms is passed in
    if (atom == NULL || molecule == NULL) {
        exit(1);
    }
    
    // Sets atom max to 1 and allocates memory if atom max was initially 0
    if (molecule->atom_max == 0) {
        molecule->atom_max = 1;
        molecule->atoms = realloc(molecule->atoms, sizeof(*atom)*  molecule->atom_max);
    }
    // Doubles the size of atom max and reallocates memory if molecule was full
    if (molecule->atom_no == molecule->atom_max) {
        molecule->atom_max *= 2;
        molecule->atoms = realloc(molecule->atoms, sizeof(*atom)*  molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(*atom) * molecule->atom_max);
        for (int i = 0; i < molecule->atom_no;i++) {
            molecule->atom_ptrs[i] = &molecule->atoms[i];
        }
    }
    // exits if realloc fails
    if(molecule->atoms == NULL) {
            printf("REALLOC FAILED, EXITING\n");
            exit(1);
        }
    molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(*atom) * molecule->atom_max);
    // exits if realloc fails
    if (molecule->atom_ptrs == NULL) {
        printf("REALLOC FAILED, EXITING\n");
        exit(1);
    }

    molecule->atom_no++;
    molecule->atoms[molecule->atom_no - 1] = *atom;
    molecule->atom_ptrs[molecule->atom_no - 1] = &molecule->atoms[molecule->atom_no - 1];
}

void molappend_bond(molecule *molecule, bond *bond) {
    // Exits if molecule or bond passed in is null
    if (molecule == NULL || bond == NULL) {
        exit(1);
    }

    if (molecule->bond_max == 0) {
        molecule->bond_max = 1;
        molecule->bonds = realloc(molecule->bonds, sizeof(*bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(*bond) * molecule->bond_max);
    } else if (molecule->bond_no == molecule->bond_max) {
        molecule->bond_max*= 2;
        molecule->bonds = realloc(molecule->bonds, sizeof(*bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(*bond) * molecule->bond_max);
        for (int i = 0; i < molecule->bond_no;i++) {
            molecule->bond_ptrs[i] = &molecule->bonds[i];
        }
    }
    if(molecule->bonds == NULL || molecule->bond_ptrs == NULL) {
        printf("REALLOC FAILED, EXITING\n");
        exit(1);
    }
    molecule->bond_no++;
    molecule->bonds[molecule->bond_no - 1] = *bond;
    molecule->bond_ptrs[molecule->bond_no - 1] = &molecule->bonds[molecule->bond_no - 1];

}

void molsort(molecule *molecule) {
    
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom*), compareAtomFunction);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond*), bond_comp);
}

int compareAtomFunction(const void* a, const void* b) {
    atom* atom1; atom* atom2;
    atom1 = *(atom **) a;
    atom2 = *(atom **)b;
    if (atom1->z >= atom2->z) {
        return 1;
    } else {
        return -1;
    }

}

int bond_comp(const void* a, const void* b) {
    bond* bond1;
    bond* bond2;
    bond1 = *(bond **) a;
    bond2 = *(bond **) b;
    if (bond1->z >= bond2->z) {
        return 1;
    } else {
        return -1;
    }
}

void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double theta = deg * (M_PI / 180.0);
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[1][1] = cos(theta);
    xform_matrix[1][2] = sin(theta) * -1;
    xform_matrix[2][1] = sin(theta);
    xform_matrix[2][2] = cos(theta);
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double theta = deg * (M_PI / 180.0);
    xform_matrix[0][0] = cos(theta);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(theta);
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = sin(theta) * -1;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(theta);
    
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double theta = deg * (M_PI / 180.0);
    xform_matrix[0][0] = cos(theta);
    xform_matrix[0][1] = sin(theta) * -1;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin(theta);
    xform_matrix[1][1] = cos(theta);
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform( molecule *molecule, xform_matrix matrix ) {
    if (molecule == NULL) {
        return;
    }
    for (int i = 0; i < molecule->atom_no; i++) {
        double originalX = molecule->atoms[i].x;
        double originalY = molecule->atoms[i].y;
        double originalZ = molecule->atoms[i].z;
        molecule->atoms[i].x = (matrix[0][0] * originalX) + (matrix[0][1] * originalY) + (matrix[0][2] * originalZ);
        molecule->atoms[i].y = (matrix[1][0] * originalX) + (matrix[1][1] * originalY) + (matrix[1][2] * originalZ);
        molecule->atoms[i].z =  (matrix[2][0] * originalX) + (matrix[2][1] * originalY) + (matrix[2][2] * originalZ);
    }
    for (int i = 0; i < molecule->bond_no; i++) {
        compute_coords(&molecule->bonds[i]);
    }
}

// Nightmare Mode Functions

rotations *spin(molecule *mol) {
    rotations* newRotation = malloc(sizeof(rotations));
    xform_matrix xRotation;
    xform_matrix yRotation;
    xform_matrix zRotation;

    for (int i = 0; i < 72; i++) {
        newRotation->x[i] = molcopy(mol);
        newRotation->y[i] = molcopy(mol);
        newRotation->z[i] = molcopy(mol);
        xrotation(xRotation, 5 * i);
        yrotation(yRotation, 5 * i);
        zrotation(zRotation, 5 * i);
        mol_xform(newRotation->x[i], xRotation);
        mol_xform(newRotation->y[i], yRotation);
        mol_xform(newRotation->z[i], zRotation);
        molsort(newRotation->x[i]);
        molsort(newRotation->y[i]);
        molsort(newRotation->z[i]);
    }

    return newRotation;
}
void rotationsfree(rotations* rotations) {
    for (int i = 0; i < 72; i++) {
        molfree(rotations->x[i]);
        molfree(rotations->y[i]);
        molfree(rotations->z[i]);
    }

    free(rotations);
}

// A2 Functions

void compute_coords(bond* bond) {
    int a1index = bond->a1;
    int a2index = bond->a2;
    bond->x1 = bond->atoms[a1index].x;
    bond->x2 = bond->atoms[a2index].x;
    bond->y1 = bond->atoms[a1index].y;
    bond->y2 = bond->atoms[a2index].y;
    bond->z = (bond->atoms[a1index].z + bond->atoms[a2index].z) / 2;
    bond->len = sqrt(pow(bond->x2 - bond->x1, 2) + pow(bond->y2 - bond->y1, 2));
    bond->dx = (bond->x2 - bond->x1) / bond->len;
    bond->dy = (bond->y2 - bond->y1) / bond->len;
}

int main() {

    return 1;
}
