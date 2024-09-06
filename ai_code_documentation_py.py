# -*- coding: utf-8 -*-
"""AI_Code_Documentation.py

This script is designed to automatically annotate code files or folders with proper software engineering documentation using the Cohere AI model.

It provides an interactive command-line interface that allows the user to choose between annotating a single file or a folder of files.

For single file annotation, the user is prompted to enter the file name, and the code is then annotated and saved with appropriate documentation.

For folder annotation, the script processes all supported code files within the specified folder and saves the annotated versions accordingly.

The script utilizes the Cohere Client to interact with the AI model and perform the code annotation.
"
"""

!pip install cohere

import os
import cohere
from google.colab import drive
import re

import os

if os.path.ismount('/content/drive'):
    pass
else:
    drive.mount('/content/drive')

co = cohere.Client("USER API KEY NEEDED")
path = "USE LOCAL PATH TO ACCESS FILES"
# example of path: '/content/drive/My Drive/code_demos'
dest = "USE CHOSEN DESTINATION FOR DOCUMENTED FILES"
#example of dest: '/content/drive/My Drive/code_demos/demo_results'

def main():
  """
    Main function to initiate the code annotation process.

    Prompts the user for input and directs the flow of the script based on their choices.
    """
  print("Welcome to the Code Annotation Tool!")

  choice = input("Do you want to annotate a single file or a folder of files? (Enter 'file' or 'folder'): ").strip().lower()


  if choice == 'file':
      print("Files Availible:")
      list_files_in_directory(path)
      file_name = input("Enter the file name you wish to annotate: ")
      file_path = f'/content/drive/My Drive/code_demos/{file_name}'
      documented_file = annotate_code(file_path)
      save_documentation(documented_file, file_name, dest)
  elif choice == 'folder':
      exclude_folder = 'demo_results'
      print("Folders Availible:\n", list_folders(path, exclude_folder))
      folder_name = input("Enter the folder name you wish to annotate: ")
      folder_path = f'/content/drive/My Drive/code_demos/{folder_name}'
      process_folder(folder_path)
  else:
      print("Invalid choice. Please enter 'file' or 'folder'.")



if __name__ == "__main__":
    main()

def annotate_code(file_path):
  """
    Annotate the code in the specified file path.

    Parameters:
    file_path (str): Path to the code file.

    Returns:
    str: Annotated code with proper software engineering documentation.
    """
  with open(file_path, 'r') as file:
      code = file.read()

  methods_and_classes = detect_methods_and_classes(code)

  if methods_and_classes == 'single':
      annotation = co.chat(
          model="command-r-plus",
          message=f"Annotate this code using proper software engineering documentation without additional explanation after (must compile after the code is returned):\n\n{code}",
          k=1
      )
      annotated_code = annotation.text
  else:
      specific_choice = input("Do you want to annotate a specific method/class or the entire file? (Enter 'specific' or 'entire'): ").strip().lower()

      if specific_choice == 'specific':
          method_name = input("Enter the name of the method/class you want to annotate: ").strip()
          annotated_code = annotate_specific_method(file_path, method_name)
      else:
          annotation = co.chat(
              model="command-r-plus",
              message=f"Annotate this code using proper software engineering documentation without additional explanation after (must compile after the code is returned):\n\n{code}",
              k=1
          )
          annotated_code = annotation.text

  cleaned_code = clean_annotated_code(annotated_code)
  print('FILE BEING WRITTEN:\n', cleaned_code)
  return cleaned_code

def save_documentation(documented_code, original_file_name, dest):
  """
    Save the annotated code to a new file with appropriate naming conventions.

    Parameters:
    documented_code (str): Annotated code to be saved.
    original_file_name (str): Name of the original file.
    dest (str): Destination folder path to save the annotated file.
    """

  suffix_map = {
      '.py': '_annotated.py',
      '.c': '_annotated.c',
      '.cpp': '_annotated.cpp',
      '.java': '_annotated.java',
      '.js': '_annotated.js',
      '.m': '_annotated.m'
  }

  for ext, suffix in suffix_map.items():
      if original_file_name.endswith(ext):
          new_file_name = original_file_name.replace(ext, suffix)
          break
  else:
      new_file_name = original_file_name

  file_path = os.path.join(dest, new_file_name)

  with open(file_path, 'w') as file:
      file.write(documented_code)
  print(f"Documentation saved to {file_path}")

def process_folder(folder_path):
  """
    Process a folder of code files and annotate each supported file.

    Parameters:
    folder_path (str): Path to the folder containing code files.
    """

  folder_name = os.path.basename(folder_path)
  result_folder = os.path.join(dest, f"{folder_name}_annotated")

  if not os.path.exists(result_folder):
      os.makedirs(result_folder)

  extensions = ('.py', '.c', '.cpp', '.java', '.js', '.m')  # Add any other languages as needed
  for root, _, files in os.walk(folder_path):
      for file_name in files:
          if file_name.endswith(extensions):
              file_path = os.path.join(root, file_name)
              documented_file = annotate_code(file_path)
              save_documentation(documented_file, file_name, result_folder)

def detect_methods_and_classes(code):
  """
    Detect if the code contains multiple methods or classes and return their names.

    Parameters:
    code (str): Code content to analyze.

    Returns:
    list or str: List of method/class names if multiple are found, or 'single' if only a single method/class is detected.
    """

  response = co.chat(
      model="command-r-plus",
      message=f"If multiple classes or methods are contained in the file list the class name and the methods in it, else only return the word 'single':\n\n{code}",
      k=1
  )

  extraction_result = response.text.strip().lower()
  print(extraction_result)
  if extraction_result != 'single':
      return extraction_result.split('\n')
  else:
      return 'single'

def save_methods_summary(extraction_result):
  """
    Save the extracted method/class names to a file.

    Parameters:
    extraction_result (list): List of method/class names.
    """
  if extraction_result != ["single"]:
      methods_summary = extraction_result
  else:
      methods_summary = []

  return methods_summary
  print("SAVE METHODS SUMMARY")

def annotate_specific_method(file_path, method_name):
  """
    Annotate a specific method or class within a code file.

    Parameters:
    file_path (str): Path to the code file.
    method_name (str): Name of the method or class to annotate.

    Returns:
    str: Annotated code with the specified method/class annotated.
    """

  with open(file_path, 'r') as file:
      code = file.read()

  method_code = extract_method_or_class(code, method_name)
  if not method_code:
      print(f"Method/Class named {method_name} not found.")
      return ''

  print('METHOD/CLASS TO BE ANNOTATED:\n', method_code)
  response = co.chat(
      model="command-r-plus",
      message=f"Annotate the following method/class with proper software engineering documentation, do not add additional explaination outside of the proper documentation. Ensure the code remains functional and can compile:\n\n{method_code}",
      k=1
  )
  annotated_code = response.text.strip()

  cleaned_annotated_code = clean_annotated_code(annotated_code)

  # Replace the original method with the annotated one in the full code
  annotated_full_code = code.replace(method_code, cleaned_annotated_code)

  return annotated_full_code

def extract_method_or_class(code, method_name):

  """
    Extract the code for a specific method or class from the given code content.

    Parameters:
    code (str): Code content to search within.
    method_name (str): Name of the method or class to extract.

    Returns:
    str: Code for the specified method or class, or None if not found.
    """

  # Pattern to match a method or class by name
  pattern = re.compile(
      rf"(def\s+{re.escape(method_name)}\s*\(.*?\)\s*:\s*|class\s+{re.escape(method_name)}\s*.*?:)((?:\n(?:\s+.*)+)?)",
      re.DOTALL
  )
  match = pattern.search(code)
  if match:
      return match.group(0)
  else:
      return None

def clean_annotated_code(annotated_code):
  """
    Clean the annotated code by removing unwanted comment delimiters and specific phrases.

    Parameters:
    annotated_code (str): Annotated code to be cleaned.

    Returns:
    str: Cleaned annotated code.
    """

  # Define patterns to remove based on common language delimiters
  patterns_to_remove = [
      r"'''", r"```python", r"```",  # Python and Markdown
      r"/\*\*", r"/\*", r"\*/",     # C, C++, Java, JavaScript (block comments)
      r"//",                        # C, C++, Java, JavaScript (single line comments)
      r"#",                         # Python, Shell scripts, etc.
      r"<!--", r"-->",              # HTML, XML
  ]

  # Compile regex patterns
  regex_patterns = [re.compile(pattern) for pattern in patterns_to_remove]

  lines = annotated_code.split('\n')
  cleaned_lines = []

  for line in lines:
      # Check for unwanted comment delimiters and the specific phrase
      if not any(pattern.match(line.strip()) for pattern in regex_patterns) and \
          "Here is the annotated code with proper software engineering documentation:" not in line:
          cleaned_lines.append(line)

  return '\n'.join(cleaned_lines)

def list_files_in_directory(directory):
    try:
        # List all files and directories in the given directory
        files_and_dirs = os.listdir(directory)

        # Filter out directories, only keep files
        files = [f for f in files_and_dirs if os.path.isfile(os.path.join(directory, f))]

        # Display the files
        if files:
            for file in files:
                print(file)
        else:
            print("No files found in the directory.")

    except Exception as e:
        print(f"An error occurred: {e}")

def list_folders(directory, exclude_folder):
    # List all entries in the given directory
    all_entries = os.listdir(directory)

    # Filter out files and the folder to exclude
    folders = [entry for entry in all_entries
               if os.path.isdir(os.path.join(directory, entry)) and entry != exclude_folder]

    return folders
