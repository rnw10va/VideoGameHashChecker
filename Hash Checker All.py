import os
import zipfile
import subprocess
import hashlib
import zlib
import win32com.client
from datetime import datetime
 
def main():
    script_path = os.path.realpath(__file__)
    script_dir = os.path.dirname(script_path)
    datFileDir = script_dir+"\\DATS\\"
    romFileDir = script_dir+"\\ROMS\\"
    counterBad=0
    counterGood=0
    badFileList=[]
    goodFileList=[]
    #Loops through all shortcuts in the ROMS directory
    for romLnkFile in os.listdir(romFileDir):
        lnkPath = getLnkTarget(romFileDir+romLnkFile)
        if os.path.exists(lnkPath):
            allFilesRecursively = findAllFiles(lnkPath)

            #Loops through all of the files in the location the shortcut points to
            for file in allFilesRecursively:
                zipFile = os.path.splitext(file)[1].lower() == ".zip"
                chdFile = os.path.splitext(file)[1].lower() == ".chd"
                
                #If the file is a zip file extract it before hashing, check the 
                # extracted file, delete it, then note the process in the results.
                if zipFile:
                    with zipfile.ZipFile(file, "r") as zip_ref:
                        os.mkdir(lnkPath+"\\tempRomFolder")
                        zip_ref.extractall(lnkPath+"\\tempRomFolder")
                    tempFile=os.listdir(lnkPath+"\\tempRomFolder")
                    newTempRom=lnkPath + "\\tempRomFolder\\" + tempFile[0]
                    strGood, strBad = lookThroughDatFiles(newTempRom, datFileDir)
                    os.remove(newTempRom)
                    os.rmdir(lnkPath+"\\tempRomFolder")
                
                #If the file is a CHD file extract it before hashing, check the 
                # extracted file, delete it, then note the process in the results.
                elif chdFile:

                    #Check the CHD file by exctracting it to an ISO
                    os.mkdir(lnkPath+"\\tempRomFolder")
                    fileNameNoExt = os.path.basename(file).split('.')[0]
                    newTempRomIso = lnkPath + "\\tempRomFolder\\" + fileNameNoExt + ".iso"
                    subprocess.run("\""+script_dir+"\\chdman\" extractdvd -i \""+file+"\" -o \""+newTempRomIso+"\"")
                    strGood, strBad = lookThroughDatFiles(newTempRomIso, datFileDir)
                    os.remove(newTempRomIso)

                    #If the CHD extracted to ISO did not match a hash then extract the CHD to cue and bin files and check the bn instead instead.
                    if strGood == "":
                        newTempRomCue = lnkPath + "\\tempRomFolder\\" + fileNameNoExt + ".cue"
                        strGoodCue, strBadCue = "", ""
                        subprocess.run("\""+script_dir+"\\chdman\" extractcd -i \""+file+"\" -o \""+newTempRomCue+"\" -sb")
                        os.remove(newTempRomCue)
                        allTempFilesRecursively = findAllFiles(lnkPath+"\\tempRomFolder")

                        #Loop through the bin/cue files and hash check all of the bin files
                        for file in allTempFilesRecursively:
                            if os.path.splitext(file)[1].lower() == ".bin":
                                strGoodTemp, strBadTemp = lookThroughDatFiles(file, datFileDir)
                                if strBadTemp == "":
                                    strGoodCue = strGoodCue + ", " + strGoodTemp
                                else:
                                    strBadCue = strBadCue + ", " + strBadTemp
                            os.remove(file)

                        #If all the bin hashes did match
                        if strBadCue == "":
                            strGood, strBad = "Original File: "+fileNameNoExt+".chd -> Temp file: "+fileNameNoExt+".cue"+strGoodCue, ""
                    
                        #If any bin hashes did match
                        else:
                            strGood, strBad = "", "Original File: "+fileNameNoExt+".chd -> Temp file: "+fileNameNoExt+".cue"+strBad+"&"+\
                            "Original File: "+fileNameNoExt+".chd -> Temp file: "+fileNameNoExt+".cue: "+strBadCue
                    
                    #If the CHD extracted to ISO did match a hash
                    else:
                        strGood = "Original File: "+fileNameNoExt+".chd -> Temp file: "+fileNameNoExt+".iso: "+strGood

                    os.rmdir(lnkPath+"\\tempRomFolder")
                
                #If the file is NOT a zip file or a CHD file extract it before hashing, check the 
                # extracted file, delete it, then note the process in the results.
                else:
                    strGood, strBad = lookThroughDatFiles(file, datFileDir)

                #If the hash did match
                if strBad == "":
                    goodFileList.append(strGood)
                    counterGood+=1
                
                #If the hash did NOT match
                else:
                    badFileList.append(strBad)
                    counterBad+=1
        else:
            print(lnkPath + " does not point to an existing rom directory.")

    #Loops over the checked files and creates a txt file that lists which are good and which are bad hashes.
    with open(script_dir+'\\results-'+datetime.now().strftime("%m-%d-%Y %H-%M-%S")+'.txt', 'w') as f:
        f.write(""+str(counterBad)+" files with incorrect hashes.")
        for badFile in badFileList:
            f.write("\n"+badFile)
        f.write("\n\n\n"+str(counterGood)+" files with correct hashes.")
        for goodFile in goodFileList:
            f.write("\n"+goodFile)

def hashFile(file_path, chunk_size=4096):
    """Splits file into chunks then calls hashingTheChunks to hash them into sha1 and crc32 hashes
    """
    try:
        with open(file_path, 'rb') as file:
            return hashingTheChunks(iter(lambda: file.read(chunk_size), b''))
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None

def hashingTheChunks(data_iterable):
    """Hashes the chunks into one returnable String value for both sha1 and crc32
    """
    hasher = hashlib.new('sha1')
    crc_value = 0
    for chunk in data_iterable:
        hasher.update(chunk)
        crc_value = zlib.crc32(chunk, crc_value)
    return str(hasher.hexdigest()), str(format(crc_value, '#08x'))[2:]

def getLnkTarget(lnkPath):
    """Returns where a shortcut points to
    """
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(lnkPath)
    return shortcut.TargetPath

def findAllFiles(directory):
    """Returns a list of all files in the directory and all subdirectories
    """
    files = []
    for path, subDirectories, filenames in os.walk(directory):
        for filename in filenames:
            file = os.path.join(path, filename)
            files.append(file)
    return files

def lookThroughDatFiles(file, datFileDir):
    """Hashes files and then checks the dat files for the hashes
    """
    string1, stringCrc = hashFile(file)
    print(string1)
    print(stringCrc)

    #Loops through all of the dat files in the DATS directory
    for datFile in os.listdir(datFileDir):
        dat=open(datFileDir+datFile,"r")
        datString=dat.read()   

        #If the hashes match hashes in the current dat file
        if string1 in datString and stringCrc in datString:
            print(file + " is not corrupt!")
            return file + ": from dat file: " + datFile + " - CRC: " + stringCrc + " - sha1: " + string1, ""
        
    #If the hash was not found in any dat file
    print(file + " is corrupt!")
    return "", file + " - CRC: " + stringCrc + " - sha1: " + string1


if __name__ == "__main__":
    main()
