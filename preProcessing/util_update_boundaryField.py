# Define the input and output file paths
input_fields = ["p", "U", "epsilon", "k", "nut"]

ref_block_name = "stationary_wall"
target_boundaries = "blockage"

for field in input_fields:
    
    in_file = "./0/" + field

    # Read the input file
    with open(in_file, "r") as file:
        lines = file.readlines()

    # Variables for processing

    i = 0
    blocks = []

    while i < len(lines):
        
        line = lines[i]
        
        # look for keyword type, which is always present in a boundary definition block
        if "type" in line and "cyclicACMI" not in line:
            
            s_block = 0
            e_block = 0
            block = []
            
            j = i - 1
            
            # look for for"{" above
            while j > 0:
                line = lines[j]
                if "{" in line:
                    # look for either "}" (end of another block) "{" (beginning of boundaryField)
                    # in case this is the first boundary in the list
                    h = j - 1
                    while h > 0:
                        line = lines[h]
                        if ("{" in line) or ("}" in line):
                            s_block = h + 1
                            break
                        h = h - 1;
                    break
                    
                j += 1
            
            while j < len(lines):
                line = lines[j]
                if "}" in line:
                    e_block = j
                    break;
                    
                j += 1
            
            for id in range(s_block, e_block + 1):  # Add 1 to include the end
                line = lines[id].strip()
                if line != "":
                    line = lines[id].rstrip()
                    block.append(line)
                
            blocks.append(block)
            block = []

        i += 1

    # find the reference boundary, that will be copied into all the target boundaries

    ref_block = []

    for block in blocks:
        for s in block:
            if ref_block_name in s:
               ref_block = block
               break;
        if len(ref_block) > 0:
            break;
        

    if len(ref_block) == 0:
        print("Boundary ", ref_block_name, " not found");
 

    # copy the reference boundary into the target ones

    for id in range(len(blocks)):
        for s in blocks[id]:
            if target_boundaries in s:
                name = s
                blocks[id] = ref_block.copy()
                blocks[id][0] = name
                break;
          
    out_file = in_file
    
    with open(out_file, "w") as file:
        
        # Write header, until boundaryField
        
        for line in lines:  
            if "boundaryField" in line:
                break
            file.write(line)

        # Write teh boundary field
        
        file.write("boundaryField\n")
        file.write("{\n")
        
        file.write('\t#includeEtc "caseDicts/setConstraintTypes"\n\n')
        
        for block in blocks:
            for s in block:
                file.write(s)
                file.write("\n")
        
        file.write("}\n")

    print(f"Update boundaryField for file: {out_file}")
