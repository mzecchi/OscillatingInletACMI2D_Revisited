import struct
import os
from pathlib import Path
import argparse

# --------------------------------------------------------------------------- #

# Set up argument parser
parser = argparse.ArgumentParser(description="Process STL files in a specified case directory.")
parser.add_argument("CASE", help="Name of the case directory (e.g., 'moving2')")
args = parser.parse_args()

# Use the CASE argument to construct paths dynamically
case_dir = args.CASE
source_dir_str = f"{case_dir}/constant/triSurface/STLs/"
out_file_str = f"{case_dir}/constant/triSurface/{case_dir}.stl"

# Example: Print the paths (you can replace this with your actual functionality)
print(f"Source directory: {source_dir_str}")
print(f"Output file: {out_file_str}")

# --------------------------------------------------------------------------- #

def binary_to_ascii_stl(binary_file, ascii_file):
    with open(binary_file, "rb") as bf, open(ascii_file, "w") as af:
        # Read the 80-byte header
        header = bf.read(80)
        solid_name = binary_file.split("/")[-1]
        solid_name = solid_name.replace(".stl", "")
        af.write(f"solid {solid_name}\n")

        # Read the triangle count (4 bytes)
        triangle_count = struct.unpack("<I", bf.read(4))[0]

        # Process each triangle
        for _ in range(triangle_count):
            # Read normal vector (3 floats)
            normal = struct.unpack("<fff", bf.read(12))
            af.write(f"  facet normal {normal[0]} {normal[1]} {normal[2]}\n")
            af.write("    outer loop\n")
            # Read the 3 vertices (3 floats each)
            for _ in range(3):
                vertex = struct.unpack("<fff", bf.read(12))
                af.write(f"      vertex {vertex[0]} {vertex[1]} {vertex[2]}\n")
            af.write("    endloop\n")
            af.write("  endfacet\n")
            # Skip the 2-byte attribute
            bf.read(2)

        af.write(f"endsolid {solid_name}\n")

# --------------------------------------------------------------------------- #

# get the directory where STLs file to be combined are found
source_dir = Path.cwd() / source_dir_str
# define output file path
out = Path.cwd() / out_file_str

# List all files with .stl extension
stl_files = [file.name for file in source_dir.glob("*.stl")]
print("Files to be combined: ", stl_files)

ascii_stl_files = []

# Loop through each binary STL file, converting it to ASCII STL
for binary_file in stl_files:
    
    # Define the output ASCII STL file name (e.g., "Patch1_ascii.stl" for "Patch1.stl")
    ascii_file = binary_file.replace(".stl", "_ascii.stl")
    ascii_file = "./" + source_dir_str + ascii_file
    ascii_stl_files.append(ascii_file)
    
    # Convert binary STL to ASCII STL
    binary_file = "./" +  source_dir_str + binary_file
    binary_to_ascii_stl(binary_file, ascii_file)
    #print(f"Converted {binary_file} to {ascii_file}")


# Concatenate the ASCII files
with open(out, "w") as outfile:
    for filename in ascii_stl_files:
        with open(filename, "r") as infile:
            outfile.write(infile.read())  # Write each file as-is

print(f"Combined STL file saved as '{out}'")

#cleanup
# Iterate through files in the directory
for file in source_dir.iterdir():
    if file.is_file() and file.name.endswith("_ascii.stl"):
        file.unlink()  # Remove the file


print("End")