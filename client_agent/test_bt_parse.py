import win32com.client
import pythoncom
import xml.etree.ElementTree as ET
import os

def parse_and_print(xml_content, bt_app):
    try:
        root = ET.fromstring(xml_content)
        print_element = root.find('.//Print')
        if print_element is None:
            return "No <Print> element found in XML"
            
        # Get Format Path
        format_element = print_element.find('Format')
        if format_element is None or not format_element.text:
            return "No <Format> path found in XML"
        format_path = format_element.text
        
        # Get Printer
        printer_name = None
        printer_element = print_element.find('.//PrintSetup/Printer')
        if printer_element is not None:
            printer_name = printer_element.text
            
        # Get Named Substrings
        substrings = {}
        for ns in print_element.findall('NamedSubString'):
            name = ns.get('Name')
            value_element = ns.find('Value')
            if name and value_element is not None:
                substrings[name] = value_element.text

        print(f"Format: {format_path}")
        print(f"Printer: {printer_name}")
        print(f"Substrings: {substrings}")
        
        # Now Execute via COM
        if not os.path.exists(format_path):
            return f"Format file not found at: {format_path}"
            
        print("Opening format...")
        # btDoNotSaveChanges = 0
        bt_fmt = bt_app.Formats.Open(format_path, False, "")
        
        if printer_name:
            bt_fmt.Printer = printer_name
            
        print("Setting substrings...")
        for k, v in substrings.items():
            bt_fmt.SetNamedSubStringValue(k, v)
            
        print("Printing...")
        # PrintOut(ShowPrintDialog, WaitForCompletion)
        bt_fmt.PrintOut(False, False)
        
        print("Closing format...")
        bt_fmt.Close(0) # 0 = doNotSaveChanges
        
        return "Success"
        
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    xml = """<?xml version="1.0" encoding="utf-8"?>
<XMLScript Version="2.0">
    <Command Name="Job1">
        <Print>
            <Format>D:\\test_label.btw</Format>
            <PrintSetup>
                <Printer>Microsoft Print to PDF</Printer>
            </PrintSetup>
            <NamedSubString Name="ItemName"><Value>MOCK ITEM</Value></NamedSubString>
            <NamedSubString Name="QTY"><Value>10PCS</Value></NamedSubString>
        </Print>
    </Command>
</XMLScript>"""
    
    # Create mock template
    with open("D:\\test_label.btw", "w") as f:
        f.write("mock")

    try:
        bt_app = win32com.client.dynamic.Dispatch("BarTender.Application")
        res = parse_and_print(xml, bt_app)
        print(f"Result: {res}")
        bt_app.Quit(1)
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()
