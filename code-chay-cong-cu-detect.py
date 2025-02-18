import subprocess
import os
import pexpect
import re
import time
import csv

def run_die(file_path):
    start_time = time.time()
    try:
        result = subprocess.run(
            ['diec', file_path],
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return "None", 0
        detection_time = time.time() - start_time
        output = result.stdout
        match = re.search(r'Packer:\s*(.*)', output)
        if match:
            packer = match.group(1)
            return packer, detection_time
        else:
            return "None", 0
    except FileNotFoundError:
        print(f"Error: '{die_path}' không được tìm thấy. Kiểm tra đường dẫn hoặc cài đặt DIE.")
        return "None", 0

def run_peid(file_path):
    start_time = time.time()
    try:
        result = subprocess.run(
            ['peid', file_path],
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return "None", 0
        detection_time = time.time() - start_time
        output = result.stdout
        r = "None"
        if output:
            r = output.splitlines()[0] 
        if r!="None":
            return r, detection_time
        else:
            return r, 0
    except FileNotFoundError:
        print(f"Error: '{die_path}' không được tìm thấy. Kiểm tra đường dẫn hoặc cài đặt DIE.")
        return "None", 0
        
def run_unipacker(file_path):
    uni_path = "/home/kali/Downloads/unipacker/unipacker/shell.py"
    
    try:
        child = pexpect.spawn(f"python {uni_path}", timeout=120)
        
        child.expect("Enter the option ID: ")
        output = child.before.decode("utf-8")
        start = None
        for i, line in enumerate(output.splitlines()):
            if "Your options for today:" in line:
                start = i + 1
        id = None
        if start is not None:
            for idx, line in enumerate(output.splitlines()[start:], start = 0):
                if "New sample" in line:
                    id = idx - 1
                    break
        start_time = time.time()
        child.sendline(str(id))

        #child.expect("Please enter the sample path (single file or directory): ")
        child.sendline(file_path)

        child.expect(r"\[.*\]> ")
        child.sendline("aaa")

        child.expect(r"PE stats:.*")        
        output = child.before.decode("utf-8")
        detection_time = time.time() - start_time
        for line in output.splitlines():
            if "Chosen unpacker" in line:
                match = re.search(r"Chosen unpacker:\s*(.*)", line.strip())
                result = match.group(1)
                return result.strip(), detection_time
                break
        else:
            print("Không tìm thấy dòng 'Chosen unpacker' trong đầu ra.")
            return "None", 0
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"Lỗi khi chạy lệnh")
        return "None", 0
    finally:
        if child.isalive():
            child.terminate()
def run_clamav(file_path):
    start_time = time.time()
    for attempt in range(5):
        try:
            result = subprocess.run(
                ["clamscan", "--debug", "--detect-pua=yes", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output = result.stdout + result.stderr
            if "zsh: killed" in output:
                print("Command killed, đang thử lại...")
                continue
            detection_time = time.time() - start_time
            pua_match = re.search(rf"{re.escape(file_path)}: PUA\.Win\.Packer\..+", output)
            if pua_match:
                return pua_match.group().split(": ")[1], detection_time

            if f"SCAN SUMMARY" in output:
                if "LibClamAV debug: UPX" in output:
                    return "UPX", detection_time
                elif "LibClamAV debug: Petite" in output:
                    return "Petite", detection_time
                elif "LibClamAV debug: MEW" in output:
                    return "MEW", detection_time
                else:
                    return "None", detection_time
            else:
                print("Command killed, đang thử lại...")
                continue

            print("Unexpected result:", output)
            return "Unexpected result", 0
        except FileNotFoundError:
            return "Error", 0
    return "Timeout", 0
      
def save_to_csv(file_path, results):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File Name", "Detected Packer", "Detection Time", "Correct/Incorrect"])
        writer.writerows(results)
        
def process_folder(folder_path):
    die_results = []
    peid_results = []
    unipacker_results = []
    clamav_results = []
    
    result = os.path.basename(os.path.dirname(folder_path))
    if os.path.isdir("/home/kali/result/" + result) == 0:
        os.mkdir("/home/kali/result/" + result)
    idx = 1
    for root, _, files in os.walk(folder_path):
        for file in files:
            if idx > 200:
                break
            file_path = os.path.join(root, file)
            print(str(idx) + ". " + file_path)
            idx = idx +1
            
            die_output, die_time = run_die(file_path)
            if die_output:
                match = re.search(result, die_output, re.IGNORECASE)
                r=0
                if match:
                    r=1
                die_results.append([file, die_output, die_time,r])
                print("Kết quả từ DIE:", die_output, ", ", die_time, ", ", r)
            else:
                die_results.append([file, "None", die_time,r])
            
            peid_output, peid_time = run_peid(file_path)
            if peid_output:
                match = re.search(result, peid_output, re.IGNORECASE)
                r=0
                if match:
                    r=1
                peid_results.append([file, peid_output, peid_time,r])
                print("Kết quả từ peid:", peid_output, ", ", peid_time, ", ", r)
            else:
                peid_results.append([file, "None", peid_time,r])

            unipacker_output, unipacker_time = run_unipacker(file_path)
            if unipacker_output:
                match = re.search(result, unipacker_output, re.IGNORECASE)
                r=0
                if match:
                    r=1
                unipacker_results.append([file, unipacker_output, unipacker_time,r])
                print("Kết quả từ unipacker:", unipacker_output, ", ", unipacker_time, ", ", r)
            else:
                unipacker_results.append([file, "None", unipacker_time,r])

            clamav_output, clamav_time = run_clamav(file_path)

            if clamav_output:
                match = re.search(result, clamav_output, re.IGNORECASE)
                r=0
                if match:
                    r=1
                clamav_results.append([file, clamav_output, clamav_time,r])
                print("Kết quả từ clamav:", clamav_output, ", ", clamav_time, ", ", r)
            else:
                clamav_results.append([file, "None", clamav_time,r])
            
    save_to_csv("/home/kali/result/" + result + "/die_results.csv", die_results)
    print("die done")
    save_to_csv("/home/kali/result/" + result + "/peid_results.csv", peid_results)
    print("peid done")
    save_to_csv("/home/kali/result/" + result + "/unipacker_results.csv", unipacker_results)
    print("uni done")
    save_to_csv("/home/kali/result/" + result + "/clamav_results.csv", clamav_results)
    print("clamav done")

if __name__ == "__main__":
    folder_path = input("Enter the folder path: ").strip()
    if os.path.isdir(folder_path): 
        process_folder(folder_path)
    else:
        print("Invalid folder path")
