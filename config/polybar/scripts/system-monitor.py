#!/usr/bin/env python3
import sys
import subprocess
import time

# System Color Monitor
# Usage: ./system-monitor.py [cpu|ram|gpu]

COLOR_NORMAL = "" # Inherit default (Turquoise)
COLOR_WARN = "%{F#FFC07F}" # Pastel Orange
COLOR_CRIT = "%{F#FF7A7A}" # Pastel Red
COLOR_END = "%{F-}"

def get_color(val, warn, crit):
    if val >= crit:
        return COLOR_CRIT
    elif val >= warn:
        return COLOR_WARN
    else:
        return COLOR_NORMAL

def get_cpu():
    # Read /proc/stat
    def read_stat():
        with open('/proc/stat', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('cpu '):
                    parts = line.split()
                    # user, nice, system, idle, iowait, irq, softirq, steal
                    parts = [int(p) for p in parts[1:]]
                    idle = parts[3] + parts[4] # idle + iowait
                    total = sum(parts)
                    return idle, total
        return 0, 0

    idle1, total1 = read_stat()
    time.sleep(0.5)
    idle2, total2 = read_stat()
    
    total_delta = total2 - total1
    idle_delta = idle2 - idle1
    
    if total_delta == 0: return "0%"
    
    cpu_usage = 100.0 * (1.0 - idle_delta / total_delta)
    
    # Logic: 0-59 Normal, 60-74 Warn, 75+ Crit
    col = get_color(cpu_usage, 60, 75)
    
    return f"{col}{int(cpu_usage)}%{COLOR_END}"

def get_ram():
    # Read /proc/meminfo
    mem_total = 0
    mem_avail = 0
    
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            elif line.startswith('MemAvailable:'):
                mem_avail = int(line.split()[1])
    
    if mem_total == 0: return "0%"
    
    used = mem_total - mem_avail
    percent = (used / mem_total) * 100.0
    
    # Logic: 0-54 Normal, 55-74 Warn, 75+ Crit
    col = get_color(percent, 55, 75)
    
    return f"{col}{int(percent)}%{COLOR_END}"

def get_gpu():
    try:
        # nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            text=True
        ).strip()
        usage = int(output)
        
        # Logic: 0-59 Normal, 60-74 Warn, 75+ Crit
        col = get_color(usage, 60, 75)
        
        return f"{col}{usage}%{COLOR_END}"
    except:
        return ""

def main():
    if len(sys.argv) < 2:
        return
        
    mode = sys.argv[1]
    
    if mode == "cpu":
        print(get_cpu())
    elif mode == "ram":
        print(get_ram())
    elif mode == "gpu":
        print(get_gpu())

if __name__ == "__main__":
    main()
