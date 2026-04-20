import win32com.client
import pythoncom

def main():
    try:
        bt_app = win32com.client.dynamic.Dispatch("BarTender.Application")
        missing = pythoncom.Missing
        empty = pythoncom.Empty
        
        tests = [
            ("2 params with missing", [missing]),
            ("3 params with missing", [missing, missing]),
            ("3 params with 0 and missing", [0, missing]),
            ("2 params with empty", [empty]),
            ("3 params with empty", [empty, empty]),
        ]
        
        xml = "<XMLScript Version=\"2.0\"><Command Name=\"Ping\"></Command></XMLScript>"
        
        for name, extra_args in tests:
            print(f"\n--- {name} ---")
            try:
                res = bt_app.XMLScript(xml, *extra_args)
                print(f"Succeeded! Res: {res}")
            except Exception as e:
                print(f"Failed: {e}")
                
        bt_app.Quit(1)
            
    except Exception as e:
        print(f"Initialization failed: {e}")

if __name__ == "__main__":
    main()
