import sys
import platform
import psutil
import subprocess
import socket
import time
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QFrame, QScrollArea, QProgressBar, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QRect, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QPen, QBrush, QMovie

# Additional imports for enhanced functionality
try:
    import cpuinfo
    HAS_CPUINFO = True
except ImportError:
    HAS_CPUINFO = False

try:
    import GPUtil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

class SystemInfoWorker(QThread):
    """Worker thread for gathering comprehensive system information"""
    info_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(str, int)  # status message, progress percentage
    
    def run(self):
        info = self.gather_system_info()
        self.info_ready.emit(info)
    
    def gather_system_info(self):
        """Gather comprehensive and accurate system information with progress updates"""
        info = {}
        
        # Operating System Details
        self.progress_update.emit("Detecting operating system...", 5)
        time.sleep(0.3)  # Small delay to show progress
        try:
            info['os_name'] = platform.system()
            info['os_version'] = platform.release()
            info['os_build'] = platform.version()
            
            if platform.system() == "Windows":
                info['os_full'] = f"Windows {platform.release()}"
                try:
                    info['os_edition'] = platform.win32_edition()
                    if info['os_edition']:
                        info['os_full'] += f" {info['os_edition']}"
                except:
                    pass
            else:
                info['os_full'] = f"{platform.system()} {platform.release()}"
            
            info['os_architecture'] = platform.architecture()[0]
            info['hostname'] = socket.gethostname()
            info['machine_type'] = platform.machine()
            
            try:
                info['username'] = os.getlogin()
            except:
                info['username'] = os.environ.get('USERNAME', os.environ.get('USER', 'Unknown'))
        except:
            info['os_full'] = "Unknown OS"
            info['os_architecture'] = "Unknown"
            info['hostname'] = "Unknown"
            info['username'] = "Unknown"
        
        # System Uptime and Boot Time
        self.progress_update.emit("Calculating system uptime...", 10)
        time.sleep(0.2)
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_delta = timedelta(seconds=uptime_seconds)
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            info['uptime'] = f"{days} days, {hours:02d}:{minutes:02d}"
            info['boot_time'] = datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
        except:
            info['uptime'] = "Unknown"
            info['boot_time'] = "Unknown"
        
        # Motherboard Information
        self.progress_update.emit("Scanning motherboard information...", 20)
        time.sleep(0.4)
        info['motherboard'] = self.get_motherboard_info()
        
        # Detailed Processor Information
        self.progress_update.emit("Analyzing processor specifications...", 30)
        time.sleep(0.5)
        try:
            if HAS_CPUINFO:
                cpu_info = cpuinfo.get_cpu_info()
                info['processor'] = cpu_info.get('brand_raw', platform.processor())
                info['cpu_vendor'] = cpu_info.get('vendor_id_raw', 'Unknown')
                info['cpu_family'] = cpu_info.get('family', 'Unknown')
                info['cpu_model'] = cpu_info.get('model', 'Unknown')
                info['cpu_stepping'] = cpu_info.get('stepping', 'Unknown')
                info['cpu_flags'] = cpu_info.get('flags', [])
                info['cpu_cache_l1'] = cpu_info.get('l1_data_cache_size', 'Unknown')
                info['cpu_cache_l2'] = cpu_info.get('l2_cache_size', 'Unknown')
                info['cpu_cache_l3'] = cpu_info.get('l3_cache_size', 'Unknown')
            else:
                info['processor'] = platform.processor()
                info['cpu_vendor'] = 'Unknown'
                info['cpu_flags'] = []
            
            # Clean up processor name
            if info['processor']:
                info['processor'] = ' '.join(info['processor'].split())
                info['processor'] = info['processor'].replace('(R)', '').replace('(TM)', '').replace('(tm)', '').strip()
            
            info['cpu_cores_physical'] = psutil.cpu_count(logical=False) or 0
            info['cpu_cores_logical'] = psutil.cpu_count(logical=True) or 0
            
            # CPU Frequency Information
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    info['cpu_freq_current'] = cpu_freq.current / 1000  # Convert to GHz
                    info['cpu_freq_max'] = cpu_freq.max / 1000 if cpu_freq.max else 0
                    info['cpu_freq_min'] = cpu_freq.min / 1000 if cpu_freq.min else 0
                else:
                    info['cpu_freq_current'] = 0
                    info['cpu_freq_max'] = 0
                    info['cpu_freq_min'] = 0
            except:
                info['cpu_freq_current'] = 0
                info['cpu_freq_max'] = 0
                info['cpu_freq_min'] = 0
            
            # CPU Usage (overall and per core)
            info['cpu_usage'] = psutil.cpu_percent(interval=0.1)
            info['cpu_usage_per_core'] = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # CPU Times
            cpu_times = psutil.cpu_times()
            info['cpu_times'] = {
                'user': cpu_times.user,
                'system': cpu_times.system,
                'idle': cpu_times.idle
            }
            
        except:
            info['processor'] = "Unknown Processor"
            info['cpu_cores_physical'] = 0
            info['cpu_cores_logical'] = 0
            info['cpu_usage'] = 0
            info['cpu_usage_per_core'] = []
        
        # Memory Information with Capabilities
        self.progress_update.emit("Examining memory configuration...", 45)
        time.sleep(0.3)
        try:
            memory = psutil.virtual_memory()
            info['ram_total_gb'] = memory.total / (1024**3)
            info['ram_used_gb'] = memory.used / (1024**3)
            info['ram_available_gb'] = memory.available / (1024**3)
            info['ram_free_gb'] = memory.free / (1024**3)
            info['ram_percent'] = memory.percent
            info['ram_cached_gb'] = getattr(memory, 'cached', 0) / (1024**3)
            info['ram_buffers_gb'] = getattr(memory, 'buffers', 0) / (1024**3)
            
            # Estimate memory capabilities
            info['memory_capabilities'] = self.get_memory_capabilities(info['ram_total_gb'], info.get('cpu_vendor', ''))
            
            # Swap information
            swap = psutil.swap_memory()
            info['swap_total_gb'] = swap.total / (1024**3)
            info['swap_used_gb'] = swap.used / (1024**3)
            info['swap_free_gb'] = swap.free / (1024**3)
            info['swap_percent'] = swap.percent
        except:
            info['ram_total_gb'] = 0
            info['ram_used_gb'] = 0
            info['ram_available_gb'] = 0
            info['ram_percent'] = 0
            info['swap_total_gb'] = 0
            info['swap_used_gb'] = 0
            info['swap_percent'] = 0
            info['memory_capabilities'] = {}
        
        # Comprehensive Storage Information with Capabilities
        self.progress_update.emit("Scanning storage devices...", 60)
        time.sleep(0.4)
        info['storage_devices'] = []
        info['storage_capabilities'] = {}
        try:
            partitions = psutil.disk_partitions()
            total_storage = 0
            
            for partition in partitions:
                try:
                    if platform.system() == "Windows":
                        # Skip system partitions and removable drives
                        if partition.device.startswith(('A:', 'B:')) or 'cdrom' in partition.opts:
                            continue
                    
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_storage += usage.total
                    
                    # Get disk I/O stats
                    disk_io = psutil.disk_io_counters(perdisk=True)
                    device_name = partition.device.replace(':', '').replace('\\', '') if platform.system() == "Windows" else partition.device.split('/')[-1]
                    
                    io_stats = None
                    for disk_name, stats in disk_io.items():
                        if device_name.lower() in disk_name.lower():
                            io_stats = {
                                'read_bytes': stats.read_bytes / (1024**3),  # GB
                                'write_bytes': stats.write_bytes / (1024**3),  # GB
                                'read_count': stats.read_count,
                                'write_count': stats.write_count
                            }
                            break
                    
                    device_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3),
                        'percent': (usage.used / usage.total) * 100,
                        'io_stats': io_stats
                    }
                    info['storage_devices'].append(device_info)
                except (PermissionError, OSError):
                    continue
            
            # Storage capabilities
            info['storage_capabilities'] = self.get_storage_capabilities(total_storage / (1024**3))
            
        except:
            pass
        
        # Enhanced Graphics Information
        self.progress_update.emit("Detecting graphics hardware...", 70)
        time.sleep(0.3)
        info['gpu_devices'] = []
        try:
            if HAS_GPUTIL:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    info['gpu_devices'].append({
                        'name': gpu.name,
                        'memory_total': gpu.memoryTotal,
                        'memory_used': gpu.memoryUsed,
                        'memory_free': gpu.memoryFree,
                        'load': gpu.load * 100,
                        'temperature': gpu.temperature,
                        'uuid': gpu.uuid,
                        'driver_version': getattr(gpu, 'driver', 'Unknown')
                    })
            
            # Fallback GPU detection
            if not info['gpu_devices']:
                gpu_name = self.get_gpu_info()
                if gpu_name and gpu_name != "Unknown Graphics Card":
                    info['gpu_devices'].append({'name': gpu_name})
        except:
            pass
        
        # Comprehensive Network Information
        self.progress_update.emit("Analyzing network interfaces...", 80)
        time.sleep(0.3)
        info['network_interfaces'] = []
        info['network_stats'] = {}
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for name, addresses in interfaces.items():
                # Skip loopback and virtual interfaces
                if name.lower() in ['lo', 'loopback'] or 'virtual' in name.lower():
                    continue
                
                if name in stats:
                    interface_info = {
                        'name': name,
                        'is_up': stats[name].isup,
                        'speed': stats[name].speed if stats[name].speed > 0 else 0,
                        'mtu': stats[name].mtu,
                        'addresses': []
                    }
                    
                    # Get all addresses (IPv4, IPv6, MAC)
                    for addr in addresses:
                        if hasattr(addr, 'family'):
                            family_str = str(addr.family)
                            if 'AF_INET' in family_str and not addr.address.startswith('127.'):
                                interface_info['addresses'].append({
                                    'type': 'IPv4',
                                    'address': addr.address,
                                    'netmask': addr.netmask,
                                    'broadcast': getattr(addr, 'broadcast', None)
                                })
                            elif 'AF_LINK' in family_str or 'AF_PACKET' in family_str:
                                interface_info['mac_address'] = addr.address
                    
                    # Add I/O statistics
                    if name in io_counters:
                        io = io_counters[name]
                        interface_info['io_stats'] = {
                            'bytes_sent': io.bytes_sent / (1024**2),  # MB
                            'bytes_recv': io.bytes_recv / (1024**2),  # MB
                            'packets_sent': io.packets_sent,
                            'packets_recv': io.packets_recv,
                            'errors_in': io.errin,
                            'errors_out': io.errout,
                            'drops_in': io.dropin,
                            'drops_out': io.dropout
                        }
                    
                    if interface_info['addresses']:
                        info['network_interfaces'].append(interface_info)
            
            # Overall network statistics
            net_io = psutil.net_io_counters()
            if net_io:
                info['network_stats'] = {
                    'total_bytes_sent': net_io.bytes_sent / (1024**3),  # GB
                    'total_bytes_recv': net_io.bytes_recv / (1024**3),  # GB
                    'total_packets_sent': net_io.packets_sent,
                    'total_packets_recv': net_io.packets_recv
                }
        except:
            pass
        
        # Battery and Power Information
        self.progress_update.emit("Checking power management...", 85)
        time.sleep(0.2)
        try:
            battery = psutil.sensors_battery()
            if battery:
                time_left = None
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    time_left = f"{hours}h {minutes}m"
                
                info['battery'] = {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': time_left,
                    'time_left_seconds': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except:
            info['battery'] = None
        
        # Temperature and Sensor Information
        self.progress_update.emit("Reading sensor data...", 90)
        time.sleep(0.2)
        try:
            temps = psutil.sensors_temperatures()
            info['temperatures'] = {}
            for sensor_name, sensor_list in temps.items():
                if sensor_list:
                    info['temperatures'][sensor_name] = []
                    for sensor in sensor_list:
                        info['temperatures'][sensor_name].append({
                            'label': sensor.label or sensor_name,
                            'current': sensor.current,
                            'high': sensor.high,
                            'critical': sensor.critical
                        })
        except:
            info['temperatures'] = {}
        
        # Fan Information
        try:
            fans = psutil.sensors_fans()
            info['fans'] = {}
            for fan_name, fan_list in fans.items():
                if fan_list:
                    info['fans'][fan_name] = []
                    for fan in fan_list:
                        info['fans'][fan_name].append({
                            'label': fan.label or fan_name,
                            'current': fan.current
                        })
        except:
            info['fans'] = {}
        
        # Process Information
        self.progress_update.emit("Counting system processes...", 95)
        time.sleep(0.2)
        try:
            info['process_count'] = len(psutil.pids())
            info['process_running'] = len([p for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_RUNNING])
            info['process_sleeping'] = len([p for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_SLEEPING])
        except:
            info['process_count'] = 0
            info['process_running'] = 0
            info['process_sleeping'] = 0
        
        # Load Average (Unix-like systems)
        try:
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()
                info['load_average'] = {
                    '1min': round(load_avg[0], 2),
                    '5min': round(load_avg[1], 2),
                    '15min': round(load_avg[2], 2)
                }
        except:
            info['load_average'] = None
        
        self.progress_update.emit("Finalizing system analysis...", 100)
        time.sleep(0.3)
        
        return info
    
    def get_motherboard_info(self):
        """Get motherboard information"""
        motherboard_info = {
            'manufacturer': 'Unknown',
            'product': 'Unknown',
            'version': 'Unknown',
            'serial': 'Unknown'
        }
        
        try:
            if platform.system() == "Windows":
                # Try WMI for motherboard info
                try:
                    result = subprocess.run([
                        'wmic', 'baseboard', 'get', 'manufacturer,product,version,serialnumber', '/format:csv'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # Skip header
                            if line.strip() and ',' in line:
                                parts = line.split(',')
                                if len(parts) >= 5:
                                    motherboard_info['manufacturer'] = parts[1].strip() or 'Unknown'
                                    motherboard_info['product'] = parts[2].strip() or 'Unknown'
                                    motherboard_info['serial'] = parts[3].strip() or 'Unknown'
                                    motherboard_info['version'] = parts[4].strip() or 'Unknown'
                                    break
                except:
                    pass
            
            elif platform.system() == "Linux":
                # Try DMI decode for motherboard info
                try:
                    result = subprocess.run(['dmidecode', '-t', 'baseboard'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            line = line.strip()
                            if 'Manufacturer:' in line:
                                motherboard_info['manufacturer'] = line.split(':', 1)[1].strip()
                            elif 'Product Name:' in line:
                                motherboard_info['product'] = line.split(':', 1)[1].strip()
                            elif 'Version:' in line:
                                motherboard_info['version'] = line.split(':', 1)[1].strip()
                except:
                    pass
        except:
            pass
        
        return motherboard_info
    
    def get_memory_capabilities(self, current_ram_gb, cpu_vendor):
        """Estimate memory capabilities based on system"""
        capabilities = {
            'max_capacity_gb': 'Unknown',
            'memory_type': 'Unknown',
            'max_speed': 'Unknown',
            'slots_estimated': 'Unknown'
        }
        
        try:
            # Estimate based on current RAM and architecture
            if current_ram_gb <= 4:
                capabilities['max_capacity_gb'] = '32 GB'
                capabilities['memory_type'] = 'DDR4'
                capabilities['max_speed'] = 'DDR4-3200'
                capabilities['slots_estimated'] = '2-4 slots'
            elif current_ram_gb <= 8:
                capabilities['max_capacity_gb'] = '64 GB'
                capabilities['memory_type'] = 'DDR4'
                capabilities['max_speed'] = 'DDR4-3200'
                capabilities['slots_estimated'] = '2-4 slots'
            elif current_ram_gb <= 16:
                capabilities['max_capacity_gb'] = '128 GB'
                capabilities['memory_type'] = 'DDR4/DDR5'
                capabilities['max_speed'] = 'DDR4-3600/DDR5-4800'
                capabilities['slots_estimated'] = '4 slots'
            elif current_ram_gb <= 32:
                capabilities['max_capacity_gb'] = '256 GB'
                capabilities['memory_type'] = 'DDR4/DDR5'
                capabilities['max_speed'] = 'DDR5-5600'
                capabilities['slots_estimated'] = '4-8 slots'
            else:
                capabilities['max_capacity_gb'] = '512+ GB'
                capabilities['memory_type'] = 'DDR5/ECC'
                capabilities['max_speed'] = 'DDR5-6400+'
                capabilities['slots_estimated'] = '8+ slots'
            
            # Adjust based on CPU vendor
            if 'intel' in cpu_vendor.lower():
                if current_ram_gb >= 16:
                    capabilities['memory_type'] = 'DDR4/DDR5 (Intel)'
            elif 'amd' in cpu_vendor.lower():
                if current_ram_gb >= 16:
                    capabilities['memory_type'] = 'DDR4/DDR5 (AMD)'
        except:
            pass
        
        return capabilities
    
    def get_storage_capabilities(self, current_storage_gb):
        """Estimate storage capabilities"""
        capabilities = {
            'max_capacity': 'Unknown',
            'interface_types': [],
            'max_drives': 'Unknown'
        }
        
        try:
            # Estimate based on current storage
            if current_storage_gb <= 500:
                capabilities['max_capacity'] = '8-16 TB'
                capabilities['interface_types'] = ['SATA III', 'M.2 NVMe']
                capabilities['max_drives'] = '2-4 drives'
            elif current_storage_gb <= 1000:
                capabilities['max_capacity'] = '16-32 TB'
                capabilities['interface_types'] = ['SATA III', 'M.2 NVMe', 'PCIe 4.0']
                capabilities['max_drives'] = '4-6 drives'
            elif current_storage_gb <= 2000:
                capabilities['max_capacity'] = '32-64 TB'
                capabilities['interface_types'] = ['SATA III', 'M.2 NVMe', 'PCIe 4.0', 'U.2']
                capabilities['max_drives'] = '6-8 drives'
            else:
                capabilities['max_capacity'] = '64+ TB'
                capabilities['interface_types'] = ['SATA III', 'M.2 NVMe', 'PCIe 5.0', 'U.2', 'Enterprise SAS']
                capabilities['max_drives'] = '8+ drives'
        except:
            pass
        
        return capabilities
    
    def get_gpu_info(self):
        """Get GPU information using system commands"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and line != 'Name' and 'Microsoft' not in line:
                            return line
            
            elif platform.system() == "Linux":
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'VGA' in line or 'Display' in line:
                            parts = line.split(': ')
                            if len(parts) > 1:
                                return parts[1].split(' (')[0]
        except:
            pass
        
        return None

class LoadingWidget(QWidget):
    """Loading screen with animated progress"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Animation properties
        self.dots_count = 0
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.update_dots)
        self.dots_timer.start(500)  # Update every 500ms
    
    def setup_ui(self):
        """Setup loading screen UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # Main loading icon/text
        loading_label = QLabel("🔍")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                color: #0066cc;
                font-size: 48px;
                border: none;
            }
        """)
        layout.addWidget(loading_label)
        
        # Loading title
        self.title_label = QLabel("Gathering Information")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: 600;
                border: none;
            }
        """)
        layout.addWidget(self.title_label)
        
        # Status message
        self.status_label = QLabel("Initializing system scan...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                border: none;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #444;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                           stop:0 #0066cc, stop:1 #0052a3);
                border-radius: 3px;
            }
        """)
        
        progress_container = QWidget()
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch()
        progress_container.setLayout(progress_layout)
        layout.addWidget(progress_container)
        
        # Percentage label
        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignCenter)
        self.percentage_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                border: none;
            }
        """)
        layout.addWidget(self.percentage_label)
        
        self.setLayout(layout)
    
    def update_dots(self):
        """Animate the loading dots"""
        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        self.title_label.setText(f"Gathering Information{dots}")
    
    def update_progress(self, status, percentage):
        """Update loading progress"""
        self.status_label.setText(status)
        self.progress_bar.setValue(percentage)
        self.percentage_label.setText(f"{percentage}%")

class MiniGraph(QWidget):
    """Mini graph widget for displaying usage data with hover effect"""
    
    def __init__(self, data, color="#0066cc", max_value=100):
        super().__init__()
        self.data = data if isinstance(data, list) else [data]
        self.color = QColor(color)
        self.hover_color = QColor(color).lighter(120)
        self.max_value = max_value
        self.setFixedHeight(30)
        self.setMinimumWidth(60)
        self.is_hovered = False
        
        # Enable hover tracking
        self.setMouseTracking(True)
        
        # Graph has hover effect
        self.setStyleSheet("""
            QWidget:hover {
                background-color: #333;
                border-radius: 4px;
            }
        """)
    
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
    
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        if not self.data or len(self.data) == 0:
            return
        
        # Draw background
        bg_color = QColor(42, 42, 42)
        if self.is_hovered:
            bg_color = QColor(51, 51, 51)
        painter.fillRect(rect, bg_color)
        
        # Draw graph
        graph_color = self.hover_color if self.is_hovered else self.color
        
        if len(self.data) == 1:
            # Single bar
            height = (self.data[0] / self.max_value) * rect.height()
            bar_rect = QRect(0, rect.height() - int(height), rect.width(), int(height))
            painter.fillRect(bar_rect, graph_color)
        else:
            # Multiple bars or line
            bar_width = rect.width() / len(self.data)
            for i, value in enumerate(self.data):
                height = (value / self.max_value) * rect.height()
                bar_rect = QRect(int(i * bar_width), rect.height() - int(height), 
                               int(bar_width), int(height))
                painter.fillRect(bar_rect, graph_color)

class CleanCard(QFrame):
    """Clean card with no hover effects and selectable text"""
    
    def __init__(self, title, value, subtitle="", progress=None, details=None, graph_data=None, wide=False):
        super().__init__()
        
        # No hover effects - static styling
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)
        
        if wide:
            self.setMinimumHeight(140)
        else:
            self.setMinimumHeight(100)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Header with title and graph
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title - selectable text
        title_label = QLabel(title)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setStyleSheet("""
            color: #888;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
        """)
        header_layout.addWidget(title_label)
        
        # Add graph if provided
        if graph_data:
            graph = MiniGraph(graph_data)
            header_layout.addWidget(graph)
        
        layout.addLayout(header_layout)
        
        # Value - selectable text
        value_label = QLabel(value)
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        value_label.setStyleSheet("""
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
            border: none;
        """)
        layout.addWidget(value_label)
        
        # Subtitle - selectable text
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setWordWrap(True)
            subtitle_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            subtitle_label.setStyleSheet("""
                color: #b0b0b0;
                font-size: 12px;
                border: none;
            """)
            layout.addWidget(subtitle_label)
        
        # Progress bar - no hover effect
        if progress is not None:
            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)
            progress_bar.setValue(int(progress))
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(4)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 2px;
                    background-color: #444;
                }
                QProgressBar::chunk {
                    background-color: #0066cc;
                    border-radius: 2px;
                    border: none;
                }
            """)
            layout.addWidget(progress_bar)
        
        # Details list - selectable text
        if details:
            for detail in details[:3]:  # Limit to 3 items
                detail_label = QLabel(detail)
                detail_label.setWordWrap(True)
                detail_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                detail_label.setStyleSheet("""
                    color: #888;
                    font-size: 10px;
                    padding: 2px 0;
                    border: none;
                """)
                layout.addWidget(detail_label)
        
        self.setLayout(layout)

class DetailCard(QFrame):
    """Detailed card with selectable text and no hover effects"""
    
    def __init__(self, title, items):
        super().__init__()
        
        # No hover effects
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)
        
        self.setMinimumHeight(120)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Title - selectable text
        title_label = QLabel(title)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setStyleSheet("""
            color: #888;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
        """)
        layout.addWidget(title_label)
        
        # Items
        for item in items[:4]:  # Limit to 4 items
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            
            # Name - selectable text
            name_label = QLabel(item.get('name', ''))
            name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            name_label.setStyleSheet("""
                color: #ffffff;
                font-size: 12px;
                font-weight: 500;
                border: none;
            """)
            item_layout.addWidget(name_label)
            
            # Details - selectable text
            if 'details' in item:
                details_label = QLabel(item['details'])
                details_label.setAlignment(Qt.AlignRight)
                details_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                details_label.setStyleSheet("""
                    color: #b0b0b0;
                    font-size: 11px;
                    border: none;
                """)
                item_layout.addWidget(details_label)
            
            layout.addLayout(item_layout)
            
            # Progress bar for items with progress - no hover effect
            if 'progress' in item:
                progress_bar = QProgressBar()
                progress_bar.setMaximum(100)
                progress_bar.setValue(int(item['progress']))
                progress_bar.setTextVisible(False)
                progress_bar.setFixedHeight(3)
                progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        border-radius: 1px;
                        background-color: #444;
                        margin: 2px 0;
                    }
                    QProgressBar::chunk {
                        background-color: #0066cc;
                        border-radius: 1px;
                        border: none;
                    }
                """)
                layout.addWidget(progress_bar)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Spec Analyzer")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f0f;
            }
        """)
        
        self.system_info = {}
        self.is_loading = True
        self.setup_ui()
        
        # Auto-refresh timer (only after initial load)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_specs)
        
        # Initial load with loading screen
        self.refresh_specs()
    
    def setup_ui(self):
        """Setup responsive UI without window controls"""
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 12px;
            }
        """)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar without window controls
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-bottom: 1px solid #2a2a2a;
                border-radius: 0;
            }
        """)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # Title only - no window controls
        # title_label = QLabel("System Spec Analyzer")
        # title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # title_label.setStyleSheet("""
        #     QLabel {
        #         color: #ffffff;
        #         font-size: 14px;
        #         font-weight: 500;
        #         border: none;
        #     }
        # """)
        # title_layout.addWidget(title_label)
        # title_layout.addStretch()
        
        # title_bar.setLayout(title_layout)
        # main_layout.addWidget(title_bar)
        
        # Content area - will switch between loading and main content
        self.content_stack = QWidget()
        self.content_stack_layout = QVBoxLayout()
        self.content_stack_layout.setContentsMargins(0, 0, 0, 0)
        self.content_stack.setLayout(self.content_stack_layout)
        
        # Loading widget
        self.loading_widget = LoadingWidget()
        self.content_stack_layout.addWidget(self.loading_widget)
        
        # Main content area (initially hidden)
        self.main_content = QScrollArea()
        self.main_content.setWidgetResizable(True)
        self.main_content.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 8px;
                border-radius: 4px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #0066cc;
                border-radius: 4px;
                min-height: 20px;
                border: none;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(24)
        
        content_widget.setLayout(self.content_layout)
        self.main_content.setWidget(content_widget)
        self.main_content.hide()  # Initially hidden
        
        self.content_stack_layout.addWidget(self.main_content)
        main_layout.addWidget(self.content_stack)
        
        central_widget.setLayout(main_layout)
    
    def show_loading(self):
        """Show loading screen"""
        self.loading_widget.show()
        self.main_content.hide()
        self.is_loading = True
    
    def show_main_content(self):
        """Show main content and hide loading"""
        self.loading_widget.hide()
        self.main_content.show()
        self.is_loading = False
        
        # Start auto-refresh timer after first load
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_specs(self):
        """Refresh system specifications"""
        if not self.is_loading:
            self.show_loading()
        
        self.worker = SystemInfoWorker()
        self.worker.info_ready.connect(self.update_specs)
        self.worker.progress_update.connect(self.loading_widget.update_progress)
        self.worker.start()
    
    def update_specs(self, info):
        """Update UI with comprehensive system information"""
        self.system_info = info
        
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # System Overview
        self.add_section("System Overview")
        overview_grid = QGridLayout()
        overview_grid.setSpacing(12)
        
        # OS Card
        os_details = [
            f"Build: {info.get('os_build', 'Unknown')[:20]}...",
            f"Architecture: {info.get('os_architecture', 'Unknown')}",
            f"Machine: {info.get('machine_type', 'Unknown')}"
        ]
        
        os_card = CleanCard(
            "Operating System",
            info.get('os_full', 'Unknown OS'),
            f"Uptime: {info.get('uptime', 'Unknown')}",
            details=os_details
        )
        overview_grid.addWidget(os_card, 0, 0)
        
        # System Identity
        identity_card = CleanCard(
            "System Identity",
            info.get('hostname', 'Unknown'),
            f"User: {info.get('username', 'Unknown')}",
            details=[f"Boot Time: {info.get('boot_time', 'Unknown')}"]
        )
        overview_grid.addWidget(identity_card, 0, 1)
        
        # Motherboard Card
        motherboard = info.get('motherboard', {})
        motherboard_name = motherboard.get('product', 'Unknown')
        if motherboard_name == 'Unknown' and motherboard.get('manufacturer', 'Unknown') != 'Unknown':
            motherboard_name = motherboard.get('manufacturer', 'Unknown')
        
        motherboard_details = [
            f"Manufacturer: {motherboard.get('manufacturer', 'Unknown')}",
            f"Version: {motherboard.get('version', 'Unknown')}"
        ]
        
        motherboard_card = CleanCard(
            "Motherboard",
            motherboard_name,
            f"Chipset: {motherboard.get('manufacturer', 'Unknown')}",
            details=motherboard_details
        )
        overview_grid.addWidget(motherboard_card, 0, 2)
        
        self.add_layout(overview_grid)
        
        # Processing & Performance
        self.add_section("Processing & Performance")
        performance_grid = QGridLayout()
        performance_grid.setSpacing(12)
        
        # CPU Card with per-core graph
        processor = info.get('processor', 'Unknown Processor')
        if len(processor) > 30:
            processor = processor[:27] + "..."
        
        cpu_cores = f"{info.get('cpu_cores_physical', 0)} cores"
        if info.get('cpu_cores_logical', 0) != info.get('cpu_cores_physical', 0):
            cpu_cores += f" ({info.get('cpu_cores_logical', 0)} threads)"
        
        cpu_freq = ""
        if info.get('cpu_freq_current', 0) > 0:
            cpu_freq = f" • {info.get('cpu_freq_current', 0):.1f} GHz"
            if info.get('cpu_freq_max', 0) > info.get('cpu_freq_current', 0):
                cpu_freq += f" (max {info.get('cpu_freq_max', 0):.1f} GHz)"
        
        cpu_details = [
            f"Vendor: {info.get('cpu_vendor', 'Unknown')}",
            f"Family: {info.get('cpu_family', 'Unknown')} Model: {info.get('cpu_model', 'Unknown')}"
        ]
        
        # Add cache information if available
        if info.get('cpu_cache_l3') != 'Unknown':
            cpu_details.append(f"L3 Cache: {info.get('cpu_cache_l3', 'Unknown')}")
        
        cpu_card = CleanCard(
            "Processor",
            processor,
            cpu_cores + cpu_freq,
            progress=info.get('cpu_usage', 0),
            details=cpu_details,
            graph_data=info.get('cpu_usage_per_core', [])
        )
        performance_grid.addWidget(cpu_card, 0, 0)
        
        # Memory Card with capabilities
        ram_total = info.get('ram_total_gb', 0)
        ram_used = info.get('ram_used_gb', 0)
        ram_percent = info.get('ram_percent', 0)
        
        memory_capabilities = info.get('memory_capabilities', {})
        
        memory_details = [
            f"Available: {info.get('ram_available_gb', 0):.1f} GB",
            f"Max Capacity: {memory_capabilities.get('max_capacity_gb', 'Unknown')}",
            f"Type: {memory_capabilities.get('memory_type', 'Unknown')}"
        ]
        
        if info.get('swap_total_gb', 0) > 0:
            memory_details.append(f"Swap: {info.get('swap_used_gb', 0):.1f}/{info.get('swap_total_gb', 0):.1f} GB")
        
        memory_card = CleanCard(
            "Memory",
            f"{ram_total:.0f} GB RAM",
            f"Used: {ram_used:.1f} GB ({ram_percent:.0f}%)",
            progress=ram_percent,
            details=memory_details
        )
        performance_grid.addWidget(memory_card, 0, 1)
        
        # GPU Card with detailed information
        gpu_devices = info.get('gpu_devices', [])
        if gpu_devices:
            gpu = gpu_devices[0]
            gpu_name = gpu['name']
            if len(gpu_name) > 25:
                gpu_name = gpu_name[:22] + "..."
            
            gpu_subtitle = ""
            gpu_progress = None
            gpu_details = []
            
            if 'memory_total' in gpu:
                gpu_subtitle = f"{gpu['memory_total']} MB VRAM"
                if 'load' in gpu:
                    gpu_progress = gpu['load']
                    gpu_subtitle += f" • {gpu['load']:.0f}% load"
                
                gpu_details.append(f"Memory Used: {gpu.get('memory_used', 0)} MB")
                gpu_details.append(f"Memory Free: {gpu.get('memory_free', 0)} MB")
                
                if gpu.get('temperature'):
                    gpu_details.append(f"Temperature: {gpu['temperature']:.0f}°C")
            
            gpu_card = CleanCard(
                "Graphics",
                gpu_name,
                gpu_subtitle,
                progress=gpu_progress,
                details=gpu_details
            )
        else:
            gpu_card = CleanCard(
                "Graphics",
                "Integrated Graphics",
                "No dedicated GPU detected"
            )
        
        performance_grid.addWidget(gpu_card, 0, 2)
        
        self.add_layout(performance_grid)
        
        # Storage & Network with Capabilities
        self.add_section("Storage & Network")
        
        # Storage Devices with capabilities
        storage_devices = info.get('storage_devices', [])
        storage_capabilities = info.get('storage_capabilities', {})
        storage_items = []
        
        for device in storage_devices[:4]:
            device_name = device['device']
            if platform.system() == "Windows":
                device_name = f"Drive {device['device']}"
            
            details = f"{device['used_gb']:.0f} GB used • {device['fstype']}"
            if device.get('io_stats'):
                io = device['io_stats']
                details += f" • R: {io['read_bytes']:.1f} GB W: {io['write_bytes']:.1f} GB"
            
            storage_items.append({
                'name': f"{device_name} ({device['total_gb']:.0f} GB)",
                'details': details,
                'progress': device['percent']
            })
        
        # Add capabilities info
        if storage_capabilities:
            storage_items.append({
                'name': f"Max Capacity: {storage_capabilities.get('max_capacity', 'Unknown')}",
                'details': f"Interfaces: {', '.join(storage_capabilities.get('interface_types', [])[:2])}"
            })
        
        if storage_items:
            storage_card = DetailCard("Storage Devices & Capabilities", storage_items)
            self.content_layout.addWidget(storage_card)
        
        # Network Interfaces
        network_interfaces = info.get('network_interfaces', [])
        network_items = []
        
        for interface in network_interfaces[:4]:
            status = "🟢 Connected" if interface['is_up'] else "🔴 Disconnected"
            ip_addr = interface['addresses'][0]['address'] if interface['addresses'] else "No IP"
            
            details = f"{status} • {ip_addr}"
            
            if interface['speed'] > 0:
                if interface['speed'] >= 1000:
                    details += f" • {interface['speed']//1000} Gbps"
                else:
                    details += f" • {interface['speed']} Mbps"
            
            if interface.get('io_stats'):
                io = interface['io_stats']
                details += f" • ↑{io['bytes_sent']:.0f} MB ↓{io['bytes_recv']:.0f} MB"
            
            network_items.append({
                'name': interface['name'],
                'details': details
            })
        
        if network_items:
            network_card = DetailCard("Network Interfaces", network_items)
            self.content_layout.addWidget(network_card)
        
        # Power & Sensors
        self.add_section("Power & Sensors")
        sensors_grid = QGridLayout()
        sensors_grid.setSpacing(12)
        
        # Battery Card
        battery = info.get('battery')
        if battery:
            battery_status = "🔌 Charging" if battery['plugged'] else "🔋 On Battery"
            battery_subtitle = f"{battery_status}"
            if battery['time_left']:
                battery_subtitle += f" • {battery['time_left']} remaining"
            
            battery_card = CleanCard(
                "Battery",
                f"{battery['percent']:.0f}%",
                battery_subtitle,
                progress=battery['percent']
            )
        else:
            battery_card = CleanCard(
                "Power",
                "AC Power",
                "Desktop system • No battery"
            )
        
        sensors_grid.addWidget(battery_card, 0, 0)
        
        # Temperature Card with multiple sensors
        temperatures = info.get('temperatures', {})
        temp_details = []
        cpu_temp = None
        
        for sensor_name, sensor_list in temperatures.items():
            if sensor_list:
                temp = sensor_list[0]['current']
                if 'cpu' in sensor_name.lower() or 'core' in sensor_name.lower():
                    cpu_temp = temp
                
                sensor_display = sensor_name.replace('_', ' ').title()
                temp_details.append(f"{sensor_display}: {temp:.0f}°C")
        
        if cpu_temp:
            temp_card = CleanCard(
                "Temperature",
                f"{cpu_temp:.0f}°C",
                "CPU temperature",
                details=temp_details[:3]
            )
        else:
            temp_card = CleanCard(
                "Temperature",
                "N/A",
                "No sensors detected"
            )
        
        sensors_grid.addWidget(temp_card, 0, 1)
        
        # System Load Card with process information
        process_count = info.get('process_count', 0)
        process_running = info.get('process_running', 0)
        process_sleeping = info.get('process_sleeping', 0)
        
        load_details = [
            f"Running: {process_running}",
            f"Sleeping: {process_sleeping}"
        ]
        
        # Add load average if available
        load_avg = info.get('load_average')
        if load_avg:
            load_details.append(f"Load Avg: {load_avg['1min']}")
        
        load_card = CleanCard(
            "System Load",
            f"{process_count} processes",
            f"CPU: {info.get('cpu_usage', 0):.0f}% • RAM: {info.get('ram_percent', 0):.0f}%",
            details=load_details
        )
        sensors_grid.addWidget(load_card, 0, 2)
        
        self.add_layout(sensors_grid)
        
        # Advanced Details
        self.add_section("Advanced Details")
        advanced_grid = QGridLayout()
        advanced_grid.setSpacing(12)
        
        # CPU Features Card
        cpu_flags = info.get('cpu_flags', [])
        cpu_features = []
        
        # Check for important CPU features
        important_features = ['avx2', 'sse4_2', 'aes', 'vmx', 'svm', 'rdrand', 'rdseed']
        for feature in important_features:
            if any(feature in flag.lower() for flag in cpu_flags):
                cpu_features.append(feature.upper())
        
        cpu_features_card = CleanCard(
            "CPU Features",
            f"{len(cpu_flags)} instruction sets",
            f"Key features: {', '.join(cpu_features[:4])}",
            details=[f"Total flags: {len(cpu_flags)}", f"Architecture: {info.get('cpu_vendor', 'Unknown')}"]
        )
        advanced_grid.addWidget(cpu_features_card, 0, 0)
        
        # Network Statistics Card
        net_stats = info.get('network_stats', {})
        if net_stats:
            net_card = CleanCard(
                "Network Statistics",
                f"{net_stats.get('total_bytes_recv', 0):.1f} GB received",
                f"{net_stats.get('total_bytes_sent', 0):.1f} GB sent",
                details=[
                    f"Packets RX: {net_stats.get('total_packets_recv', 0):,}",
                    f"Packets TX: {net_stats.get('total_packets_sent', 0):,}"
                ]
            )
        else:
            net_card = CleanCard(
                "Network Statistics",
                "No data available",
                "Network statistics not accessible"
            )
        
        advanced_grid.addWidget(net_card, 0, 1)
        
        # Fan Information Card
        fans = info.get('fans', {})
        fan_details = []
        fan_count = 0
        
        for fan_name, fan_list in fans.items():
            for fan in fan_list:
                fan_details.append(f"{fan['label']}: {fan['current']} RPM")
                fan_count += 1
        
        if fan_count > 0:
            fan_card = CleanCard(
                "System Fans",
                f"{fan_count} fans detected",
                "Fan speeds monitored",
                details=fan_details[:3]
            )
        else:
            fan_card = CleanCard(
                "System Fans",
                "No fans detected",
                "Fan monitoring not available"
            )
        
        advanced_grid.addWidget(fan_card, 0, 2)
        
        self.add_layout(advanced_grid)
        
        # Add stretch at the end
        self.content_layout.addStretch()
        
        # Show main content after loading is complete
        self.show_main_content()
    
    def add_section(self, title):
        """Add a section title"""
        section_label = QLabel(title)
        section_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        section_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: 600;
                margin: 8px 0;
                border: none;
            }
        """)
        self.content_layout.addWidget(section_label)
    
    def add_layout(self, layout):
        """Add a layout to content"""
        widget = QWidget()
        widget.setLayout(layout)
        self.content_layout.addWidget(widget)

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("System Spec Analyzer")
    app.setApplicationVersion("1.0")
    app.setStyle('Fusion')
    
    # Set clean font
    font = QFont("Segoe UI", 9)
    if not font.exactMatch():
        font = QFont("Arial", 9)
    app.setFont(font)
    
    # Set minimal dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 15, 15))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(26, 26, 26))
    palette.setColor(QPalette.AlternateBase, QColor(42, 42, 42))
    palette.setColor(QPalette.ToolTipBase, QColor(42, 42, 42))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(42, 42, 42))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, QColor(0, 102, 204))
    palette.setColor(QPalette.Highlight, QColor(0, 102, 204))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()