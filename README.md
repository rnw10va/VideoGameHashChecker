# VideoGameHashChecker
Simple hash checker for video games to ensure your libraries have no corruptions.

A hash checker, specifically designed to check a videogame library without editing, renaming, or moving games. Works on any file types, with special
logic for CHD and zip files, to extract them to temp files before checking the hash, which is noted in the final output.

Usage - 
1. Replace the placeholder text file inside of the DATS folder with file(s) that contain sha1 and crc32 hashes to compare your games against.
2. Replace the placeholder text file inside of the ROMS folder with shortcut(s) to your game directories. The script will hash all files 
   recursively, and hash any file types other than zip and CHD, which will be converted first.
3. Run the script. If the script does not run, you may be missing some dependencies, such as the following:
    a. chdman.exe - should be downloaded and placed next to the Python script (Hash Checker All.py) if you have CHD files.
	More dependencies to be listed soon...
4. Open the output text file, which should be in the same folder as the script (Hash Checker All.py) to see which games matched and which did not.
   The text file will all be divided into games that did not match and games that did match. For the games that did not match, the game location 
   and both hashes will be shown. For the gammes that did match, the file with the matching hash, the game location, and both hashes will be shown.
   