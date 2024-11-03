def check_and_correct_indentation(filename):
    corrected_lines = []
    indentation_corrected = False

    with open(filename, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            stripped_line = line.rstrip()
            if stripped_line:  # Ignore empty lines
                leading_spaces = len(line) - len(line.lstrip())

                # Check if the leading spaces are a multiple of 4
                if leading_spaces % 4 != 0:
                    corrected_indentation = (leading_spaces // 4 + 1) * 4
                    corrected_line = ' ' * corrected_indentation + line.lstrip()
                    corrected_lines.append(corrected_line)
                    print(
                        f"Corrected indentation on line {line_number}: changed from {leading_spaces} to {corrected_indentation} spaces")
                    indentation_corrected = True
                else:
                    corrected_lines.append(line)
            else:
                corrected_lines.append(line)

    # If corrections were made, save the corrected file
    if indentation_corrected:
        with open(filename, 'w') as file:
            file.writelines(corrected_lines)
        print(f"Indentation errors corrected and saved in '{filename}'.")
    else:
        print(f"No indentation errors found in '{filename}'.")


if __name__ == "__main__":
    filename = input("Enter the path of the Python file to check and correct: ")
    check_and_correct_indentation(filename)
