import subprocess
import os
import glob

# Paths
BARTENDER_EXE = r"C:\Program Files\Seagull\BarTender Suite\bartend.exe"
PRINT_JOBS_DIR = r"D:\Workspace\NY_tagging_sys\print_jobs"

def get_latest_job_file():
    # Look for both .xml and .txt
    list_of_files = glob.glob(os.path.join(PRINT_JOBS_DIR, '*.xml')) + \
                    glob.glob(os.path.join(PRINT_JOBS_DIR, '*.txt'))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def test_print():
    if not os.path.exists(BARTENDER_EXE):
        print(f"ERROR: bartend.exe not found at {BARTENDER_EXE}")
        return

    job_file = get_latest_job_file()
    if not job_file:
        print(f"ERROR: No XML or TXT files found in {PRINT_JOBS_DIR}")
        return

    print(f"--- DEBUG PRINT SESSION ---")
    print(f"Latest job file detected: {job_file}")
    
    # Read and print the content so we can see it in terminal
    try:
        with open(job_file, 'r', encoding='utf-8') as f:
            print("File Content:")
            print(f.read())
            print("-" * 30)
    except Exception as e:
        print(f"ERROR reading file: {e}")

    print(f"Executing: \"{BARTENDER_EXE}\" /XMLScript=\"{job_file}\"")
    
    try:
        # We run it with subprocess.Popen to not block
        process = subprocess.Popen([BARTENDER_EXE, f'/XMLScript={job_file}'])
        print("\nCommand sent to Bartender.")
        print("Look at your screen! If there is an error (e.g. Printer not found),")
        print("Bartender might pop up a window or show an error icon in the tray.")
        print("-" * 30)
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    test_print()
