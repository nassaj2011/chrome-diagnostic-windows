from __future__ import annotations

import json
import os
import platform
import re
from datetime import datetime
from typing import Any

import psutil

from .chrome import find_chrome_executable
from .utils import run_powershell


def _ps_json(script: str, timeout: int = 30) -> Any:
    if os.name != "nt":
        return None
    wrapped = f"$ProgressPreference='SilentlyContinue'; $ErrorActionPreference='SilentlyContinue'; {script} | ConvertTo-Json -Depth 5 -Compress"
    result = run_powershell(wrapped, timeout=timeout)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return None


def collect_system_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "windows": platform.platform(),
        "python_runtime": platform.python_version(),
        "cpu": platform.processor(),
        "logical_processors": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).astimezone().isoformat(timespec="seconds"),
        "volumes": [],
        "chrome_path": "",
        "chrome_version": "",
    }
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            info["volumes"].append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "total_gb": round(usage.total / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "free_percent": round((usage.free / usage.total) * 100, 1) if usage.total else 0,
            })
        except (PermissionError, OSError):
            pass
    chrome = find_chrome_executable()
    if chrome:
        info["chrome_path"] = str(chrome)
        version = _ps_json(f"(Get-Item -LiteralPath '{str(chrome).replace("'", "''")}').VersionInfo.FileVersion", timeout=10)
        if isinstance(version, str):
            info["chrome_version"] = version

    if os.name == "nt":
        extra = _ps_json("""
        [pscustomobject]@{
          OsCaption=(Get-CimInstance Win32_OperatingSystem).Caption
          OsVersion=(Get-CimInstance Win32_OperatingSystem).Version
          OsBuild=(Get-CimInstance Win32_OperatingSystem).BuildNumber
          CpuNames=@(Get-CimInstance Win32_Processor | ForEach-Object {$_.Name})
          Gpus=@(Get-CimInstance Win32_VideoController | ForEach-Object {[pscustomobject]@{Name=$_.Name;DriverVersion=$_.DriverVersion;DriverDate=$_.DriverDate}})
          Disks=@(Get-CimInstance Win32_DiskDrive | ForEach-Object {[pscustomobject]@{Model=$_.Model;Interface=$_.InterfaceType;Size=$_.Size;Status=$_.Status}})
          PowerPlan=(powercfg /GETACTIVESCHEME | Out-String).Trim()
        }
        """, timeout=30)
        if isinstance(extra, dict):
            info.update(extra)
    return info


def collect_defender_status() -> dict[str, Any]:
    data = _ps_json("""
      if(Get-Command Get-MpComputerStatus -ErrorAction SilentlyContinue){
        $m=Get-MpComputerStatus
        [pscustomobject]@{
          AntivirusEnabled=$m.AntivirusEnabled
          RealTimeProtectionEnabled=$m.RealTimeProtectionEnabled
          BehaviorMonitorEnabled=$m.BehaviorMonitorEnabled
          SignatureLastUpdated=$m.AntivirusSignatureLastUpdated
          QuickScanAge=$m.QuickScanAge
          FullScanAge=$m.FullScanAge
        }
      }
    """, timeout=20)
    return data if isinstance(data, dict) else {"status": "unavailable"}


def collect_whea_events(hours: int = 24) -> list[dict[str, Any]]:
    data = _ps_json(f"""
      $since=(Get-Date).AddHours(-{int(hours)})
      Get-WinEvent -FilterHashtable @{{LogName='System';ProviderName='Microsoft-Windows-WHEA-Logger';Id=17;StartTime=$since}} -ErrorAction SilentlyContinue |
        Select-Object -First 200 TimeCreated,Id,LevelDisplayName,Message
    """, timeout=30)
    if data is None:
        return []
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        message = str(item.get("Message") or "")
        primary = re.search(r"Primary Device Name:\s*([^\r\n]+)", message)
        bdf = re.search(r"Primary Bus:Device:Function:\s*([^\r\n]+)", message)
        rows.append({
            "TimeCreated": item.get("TimeCreated"),
            "Id": item.get("Id"),
            "LevelDisplayName": item.get("LevelDisplayName"),
            "PrimaryDeviceName": primary.group(1).strip() if primary else "",
            "PrimaryBusDeviceFunction": bdf.group(1).strip() if bdf else "",
            "Message": re.sub(r"\s+", " ", message).strip(),
        })
    return rows


def collect_pcie_devices() -> list[dict[str, Any]]:
    data = _ps_json("""
      $signed=@{}
      Get-CimInstance Win32_PnPSignedDriver | Where-Object {$_.DeviceID -like 'PCI\\*'} | ForEach-Object {$signed[$_.DeviceID]=$_}
      Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object {$_.InstanceId -like 'PCI\\*'} | ForEach-Object {
        $loc=''
        try{$loc=((Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationPaths' -ErrorAction Stop).Data -join '; ')}catch{}
        $drv=$signed[$_.InstanceId]
        [pscustomobject]@{
          Name=$_.FriendlyName
          Class=$_.Class
          Status=$_.Status
          InstanceId=$_.InstanceId
          LocationPath=$loc
          DriverVersion=$drv.DriverVersion
          DriverProvider=$drv.DriverProviderName
          InfName=$drv.InfName
        }
      }
    """, timeout=45)
    if data is None:
        return []
    return data if isinstance(data, list) else [data] if isinstance(data, dict) else []
