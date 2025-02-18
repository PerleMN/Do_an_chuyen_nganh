import os
import pandas as pd
    
def count_number_detected_file(file_path):
    data = pd.read_csv(file_path)
   
    total_rows = len(data)
    data['Detected Packer'] = data['Detected Packer'].fillna('nan').astype(str).str.strip().str.lower()
    
    undetected_count = data['Detected Packer'].isin(["None", "Timeout", "Unexpected result", "Error", "nan"]).sum()
    detected_count = total_rows - undetected_count
    return detected_count
    
def calculate_detection_percentage(file_path):
    data = pd.read_csv(file_path)
   
    detected_count = count_number_detected_file(file_path)
    divisor = 200 if "clamav_results.csv" in file_path else 2000
    
    detection_percentage = (detected_count / divisor) * 100
    return detection_percentage

def calculate_correct_detection_percentage(file_path):
    data = pd.read_csv(file_path)
    
    correct_count = data['Correct/Incorrect'].sum()
    detected_count = count_number_detected_file(file_path)
    
    if detected_count > 0:
        correct_detection_percentage = (correct_count / detected_count) * 100
    else:
        correct_detection_percentage = 0.0
    
    return correct_detection_percentage
    
def calculate_average_detection_time(file_path):
    data = pd.read_csv(file_path)
    data['Detection Time'] = pd.to_numeric(data['Detection Time'], errors='coerce')
    average_time = data['Detection Time'].mean()
    return average_time

def scan_files_in_subdirectories():
    root_directory = os.getcwd()

    data = {
        'unipacker': {'detection_time':[], 'detection_percentage': [], 'correct_detection_percentage':[]},
        'clamav': {'detection_time':[], 'detection_percentage': [], 'correct_detection_percentage':[]},
        'peid': {'detection_time':[], 'detection_percentage': [], 'correct_detection_percentage':[]},
        'die': {'detection_time':[], 'detection_percentage': [], 'correct_detection_percentage':[]}
    }

    for subdir, _, files in os.walk(root_directory):
        for file in files:
            file_path = os.path.join(subdir, file)
            _, extension = os.path.splitext(file_path)
            if extension == ".csv":
                print(file_path + ": ")
                dec_per = calculate_detection_percentage(file_path)
                print("\tdetection percentage: " + str(dec_per))
                cor_per = calculate_correct_detection_percentage(file_path)
                print("\tcorrect detection percentage: " + str(cor_per))
                avg_detection_time = calculate_average_detection_time(file_path)
                print("\taverage detection time: " + str(avg_detection_time))
                
                for detect_type in data:
                    if detect_type in file:
                        data[detect_type]['detection_time'].append(avg_detection_time)
                        data[detect_type]['detection_percentage'].append(dec_per)
                        data[detect_type]['correct_detection_percentage'].append(cor_per)
                        
    for detect_type, d in data.items ():
        avg_detection_time = sum(d['detection_time' ]) / len(d['detection_time' ]) if d['detection_time' ] else 0
        avg_detection_percentage = sum(d['detection_percentage' ]) / len(d['detection_percentage' ]) if d['detection_percentage' ] else 0
        avg_correct_percentage = sum(d['correct_detection_percentage' ]) / len(d['correct_detection_percentage' ]) if d['correct_detection_percentage' ] else 0
        print(f"{detect_type.capitalize()}:")
        print("\taverage detection percentage: " + str(avg_detection_percentage))
        print("\taveragecorrect detection percentage: " + str(avg_correct_percentage))
        print("\taverage detection time: " + str(avg_detection_time))
        
                

scan_files_in_subdirectories()


