from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib;  # code to parse for data
import sys
import re
import MolDisplay
import molsql
import cgi
import os
import sqlite3
from io import TextIOWrapper, BytesIO

public_files = ["/index.html","/style.css","/script.js"]

class webServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Basic webform passed to server if path is /, get user to upload a file
        if self.path in public_files:
            self.send_response(200)
            
            fileType = self.path.split(".")[-1]
            if (fileType == "css"):
                self.send_header("Content-type", "text/css")
            elif(fileType == "js"):
                self.send_header("Content-type", "text/javascript")
            else:    
                self.send_header("Content-type", "text/html")
            
            fp = open(self.path[1:])
            page = fp.read()
            fp.close()
            
            self.send_header("Content-length", len(page))            
            self.end_headers()
            
            self.wfile.write(bytes(page, "utf-8"))
        else:
            # send not found error if path other then / is requested
            self.send_response(404)
            self.end_headers();
            self.wfile.write(bytes( "404: not found", "utf-8" ))
    
    # Post request if path is server
    def do_POST(self):
        MolDisplay.radius = db.radius();
        MolDisplay.element_name = db.element_name();
        MolDisplay.header += db.radial_gradients();

        if self.path == "/upload-sdf":
            form = cgi.FieldStorage(fp = self.rfile, headers=self.headers, environ={"REQUEST_METHOD": 'POST'})
            SDFfile = form['sdf-file']
            # header = self.rfile.read(int(self.headers.get("Content-Length")))
            # fp = TextIOWrapper(BytesIO(header))
            fp = TextIOWrapper(BytesIO(SDFfile.file.read()))
            molName = form.getvalue('moleculeName')
            db.add_molecule(molName, fp)

            mol = db.load_mol(molName);
            mol.sort()
            svgString = mol.svg()
            
            with open(f"{molName}.svg", "w") as file:
                public_files.append(f"{molName}.svg")
                file.write(svgString);
            file.close()

            file_path = f"{molName}.svg"
            os.chmod(file_path, 0o777)


        # Post Method For Adding an element to the sqlite database
        elif self.path == "/add-element":
            form = cgi.FieldStorage(fp = self.rfile, headers=self.headers, environ={"REQUEST_METHOD": 'POST'})
            print(form)
            elementNumber = form.getvalue('elementNumber')
            elementName = form.getvalue('elementName')
            elementCode = form.getvalue('elementCode')
            color1 = form.getvalue('color1')[1:]
            color2 = form.getvalue('color2')[1:]
            color3 = form.getvalue('color3')[1:]
            elementRadius = form.getvalue('elementRadius')
            listToPass = [elementNumber, elementCode, elementName,  color1, color2, color3, elementRadius]
            db.add_element(listToPass)

            self.send_response(200)
            self.end_headers()
        # Post Method For Removing an element from the database
        elif self.path == "/remove-element":
            form = cgi.FieldStorage(fp = self.rfile, headers=self.headers, environ={"REQUEST_METHOD": 'POST'})
            value = form.getvalue('value')
            listToPass = [value]
            db.remove_element(listToPass)
            self.send_header("Content-type", "image/svg+xml")
            self.end_headers()

        elif self.path == "/select-molecule":
            form = cgi.FieldStorage(fp = self.rfile, headers=self.headers, environ={"REQUEST_METHOD": 'POST'})
            moleculeName = form.getvalue('moleculeName')
            mol = db.load_mol(moleculeName);
            mol.sort()
            svgString = mol.svg()
            self.send_response(200)
            self.send_header("Content-length", len(svgString))
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(svgString, "utf-8"))


        else: 
            # Send not found error if any other path is requested
            self.send_response(404)
            self.end_headers();
            self.wfile.write(bytes( "404: not found", "utf-8" ))
#Create DB
db = molsql.Database(reset=True)
db.create_tables()

# Create the server
server = HTTPServer(('localhost', int(sys.argv[1])), webServer)



print("Server Running")
server.serve_forever()
