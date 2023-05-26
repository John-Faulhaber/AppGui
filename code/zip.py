'''
Module to handle .zip file creation for compiling.
'''
# Create a zip file titled "appgui", from the contents within the "temp_zip" directory
import shutil


shutil.make_archive('appgui', 'zip', 'temp_zip')
