# System Spec Analyzer

A comprehensive, modern desktop application for analyzing and displaying detailed system specifications with a beautiful dark-themed interface.

![System Spec Analyzer](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🖥️ **Comprehensive System Information**
- **Operating System**: Version, build, architecture, uptime
- **Processor**: Brand, cores, frequency, cache, instruction sets
- **Memory**: RAM usage, swap, estimated maximum capacity
- **Storage**: All drives with usage, I/O statistics, capabilities
- **Graphics**: GPU details, VRAM, temperature, load
- **Network**: All interfaces with speeds, IP addresses, statistics
- **Motherboard**: Manufacturer, model, version information
- **Sensors**: Temperature monitoring, fan speeds, battery status

### 🎨 **Modern Interface**
- **Dark Theme**: Professional dark UI with blue accents
- **Responsive Design**: Optimized for 1280x720 and larger screens
- **Clean Cards**: Organized information in elegant cards
- **Mini Graphs**: Real-time CPU core usage visualization
- **Progress Bars**: Visual representation of usage percentages
- **Selectable Text**: All text can be selected and copied

### ⚡ **Advanced Features**
- **Loading Screen**: Beautiful animated loading with progress tracking
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Hover Effects**: Interactive graphs with hover animations
- **System Capabilities**: Estimated maximum memory and storage capacity
- **Cross-platform**: Works on Windows, Linux, and macOS
- **No External Dependencies**: Uses only standard Python libraries

## 📸 Screenshots

### Loading Screen
```
🔍
Gathering Information...
Analyzing processor specifications...
[████████████████████████████████████████] 30%
```

### Main Interface
```
┌─────────────────────────────────────────────────────────────┐
│ System Spec Analyzer                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ System Overview                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ OS          │ │ Identity    │ │ Motherboard │            │
│ │ Windows 11  │ │ DESKTOP-PC  │ │ ASUS Z690   │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
│                                                             │
│ Processing & Performance                                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ Processor   │ │ Memory      │ │ Graphics    │            │
│ │ Intel i7    │ │ 32 GB RAM   │ │ RTX 4080    │            │
│ │ ████████    │ │ ████░░░░    │ │ ██████░░    │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- PyQt5

### Quick Install
```bash
# Clone the repository
git clone https://github.com/narmesh/System_Spec_Analyzer.git
cd System_Spec_Analyzer

# Install required packages
pip install PyQt5 psutil

# Optional: Install additional packages for enhanced features
pip install py-cpuinfo GPUtil
```

### Run the Application
```bash
python system_spec_analyzer.py
```

## 📦 Dependencies

### Required
- **PyQt5**: GUI framework
- **psutil**: System and process utilities

### Optional (for enhanced features)
- **py-cpuinfo**: Detailed CPU information
- **GPUtil**: GPU monitoring and statistics

### Installation Commands
```bash
# Required dependencies
pip install PyQt5 psutil

# Optional dependencies
pip install py-cpuinfo GPUtil
```

## 🔧 Usage

### Basic Usage
1. **Launch**: Run the Python script
2. **Wait**: Loading screen shows system analysis progress
3. **Explore**: Browse through different system information sections
4. **Copy**: Select and copy any text for external use
5. **Refresh**: Data automatically refreshes every 30 seconds

### Sections Overview

#### 📊 **System Overview**
- Operating system details and uptime
- System identity and user information
- Motherboard manufacturer and model

#### ⚡ **Processing & Performance**
- CPU specifications with real-time usage graphs
- Memory usage with capacity estimates
- GPU information and performance metrics

#### 💾 **Storage & Network**
- All storage devices with usage statistics
- Network interfaces with connection status
- I/O statistics and capabilities

#### 🔋 **Power & Sensors**
- Battery status and remaining time
- Temperature sensors and readings
- System load and process information

#### 🔬 **Advanced Details**
- CPU instruction sets and features
- Network traffic statistics
- Fan speeds and system monitoring

## 🛠️ Technical Details

### Architecture
- **Multi-threaded**: System scanning runs in background thread
- **Event-driven**: PyQt5 event system for responsive UI
- **Modular design**: Separate classes for different components
- **Cross-platform**: Platform-specific optimizations

### Performance
- **Fast startup**: Optimized system scanning
- **Low resource usage**: Minimal CPU and memory footprint
- **Efficient updates**: Only refreshes changed data
- **Responsive UI**: Non-blocking interface during scans

### Compatibility
- **Windows**: Full feature support with WMI integration
- **Linux**: Complete functionality with DMI and lspci
- **macOS**: Core features with system_profiler integration

## 🎨 Customization

### Color Scheme
The application uses a modern dark theme with customizable colors:
- **Background**: `#1a1a1a` (Dark gray)
- **Cards**: `#2a2a2a` (Medium gray)
- **Accent**: `#0066cc` (Blue)
- **Text**: `#ffffff` (White)

### Modifying Refresh Rate
```python
# Change auto-refresh interval (in milliseconds)
self.refresh_timer.start(30000)  # 30 seconds (default)
self.refresh_timer.start(60000)  # 1 minute
self.refresh_timer.start(10000)  # 10 seconds
```

### Adding Custom Information
```python
# Add custom system information in gather_system_info()
info['custom_field'] = get_custom_data()

# Display in UI
custom_card = CleanCard(
    "Custom Info",
    info.get('custom_field', 'Unknown'),
    "Custom subtitle"
)
```

###Troubleshooting
#### **Import Errors**

```bash

# If PyQt5 is not found
pip install --upgrade PyQt5

# If psutil is not found
pip install --upgrade psutil
```

#### **Permission Errors (Linux/macOS)**
```bash
# Run with appropriate permissions for hardware access
sudo python system_spec_analyzer.py
```

#### **Missing GPU Information**

```bash
# Install GPUtil for detailed GPU stats
pip install GPUtil
```

#### **No Temperature Sensors**
- **Windows**: Install hardware monitoring drivers
- **Linux**: Ensure `lm-sensors` is installed and configured
- **macOS**: Temperature monitoring may be limited

### Performance Issues
- **Slow startup**: Check antivirus software interference
- **High CPU usage**: Increase refresh interval
- **Memory leaks**: Restart application periodically

## 🤝 Contributing

I welcome contributions! Here's how you can help:

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/narmesh/System_Spec_Analyzer.git
cd System_Spec_Analyzer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request


### Areas for Contribution

- 🌐 **Internationalization**: Multi-language support
- 📱 **Mobile**: Responsive design improvements
- 🔌 **Plugins**: Extensible plugin system
- 📊 **Charts**: Advanced data visualization
- 🎨 **Themes**: Additional color schemes
- 🔧 **Features**: New system information categories
