# Macroeconomics Model

**Author:** Talhah Karani (2545335) - Macroeconomics Group 12  
**Date Created:** 24/08/2024  
**Date Modified:** 29/08/2024  

## Usage

1. Ensure that the header file and the `Model.py` file are in the same directory.
2. Navigate to the directory containing these files.
3. Ensure that Python is installed on your device, along with the `matplotlib` library.
4. Run the model using the following command:

   ```bash
   python Model.py
   ```
   
## Prerequisites
Python: Ensure Python 3.x is installed. You can download it from python.org.

Matplotlib: Required for plotting the GDP graph. Install it using the command:

   ```bash
   pip install matplotlib
   ```

## Installation
To set up your environment, follow these steps:

Clone or download the project files.
Install Python and Matplotlib as mentioned above.

## Simulation Parameters
Simulation Duration: The model prompts you to enter the simulation duration in years. If no input is provided, it defaults to ten years. This can also be modified directly in the Model.py file.

## Output Explanation
A graph showing the GDP over the specified simulation period will be displayed.
Any economic shocks and their occurrence times will be printed to the console.

## Troubleshooting
Error: ModuleNotFoundError: No module named 'matplotlib': Ensure that Matplotlib is correctly installed using pip install matplotlib.

Graph Not Displaying: Check if the Matplotlib backend is set up correctly for your environment. Running the code in a different environment (like Jupyter Notebook or a command-line interface) may help.
