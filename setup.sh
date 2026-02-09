#!/bin/bash

# EdgePulse-Pi5 Setup Script
# Automates installation and configuration

set -e  # Exit on error

echo "=================================="
echo "EdgePulse-Pi5 Setup Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root for system operations
if [ "$EUID" -ne 0 ] && [ "$1" == "install" ]; then
    print_error "Please run with sudo for installation: sudo ./setup.sh install"
    exit 1
fi

# Function to install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    apt update
    apt install -y \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        i2c-tools \
        build-essential \
        libssl-dev \
        libffi-dev
    
    print_status "System dependencies installed"
}

# Function to enable I2C
enable_i2c() {
    print_status "Enabling I2C interface..."
    
    # Check if I2C is already enabled
    if grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
        print_status "I2C already enabled"
    else
        echo "dtparam=i2c_arm=on" >> /boot/config.txt
        print_status "I2C enabled (reboot required)"
    fi
    
    # Load I2C modules
    if ! grep -q "i2c-dev" /etc/modules; then
        echo "i2c-dev" >> /etc/modules
    fi
    
    modprobe i2c-dev 2>/dev/null || true
}

# Function to enable 1-Wire for DS18B20
enable_1wire() {
    print_status "Enabling 1-Wire interface..."
    
    if grep -q "^dtoverlay=w1-gpio" /boot/config.txt; then
        print_status "1-Wire already enabled"
    else
        echo "dtoverlay=w1-gpio" >> /boot/config.txt
        print_status "1-Wire enabled (reboot required)"
    fi
    
    # Load 1-Wire modules
    if ! grep -q "w1-gpio" /etc/modules; then
        echo "w1-gpio" >> /etc/modules
    fi
    if ! grep -q "w1-therm" /etc/modules; then
        echo "w1-therm" >> /etc/modules
    fi
    
    modprobe w1-gpio 2>/dev/null || true
    modprobe w1-therm 2>/dev/null || true
}

# Function to setup Python environment
setup_python() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python packages..."
    pip install -r requirements.txt
    
    print_status "Python environment ready"
}

# Function to create directories
create_directories() {
    print_status "Creating directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p data/exports
    
    print_status "Directories created"
}

# Function to install systemd service
install_service() {
    print_status "Installing systemd service..."
    
    # Get current directory
    INSTALL_DIR=$(pwd)
    
    # Create service file
    cat > edgepulse.service << EOF
[Unit]
Description=EdgePulse-Pi5 Health Monitoring System
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Copy service file
    cp edgepulse.service /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    print_status "Systemd service installed"
    print_status "Enable with: sudo systemctl enable edgepulse"
    print_status "Start with: sudo systemctl start edgepulse"
}

# Function to test sensors
test_sensors() {
    print_status "Testing sensors..."
    
    # Test I2C devices
    echo ""
    echo "I2C Devices detected:"
    i2cdetect -y 1 || print_warning "I2C detection failed"
    echo ""
    
    # Test 1-Wire devices
    echo "1-Wire Devices:"
    if [ -d "/sys/bus/w1/devices" ]; then
        ls /sys/bus/w1/devices/ | grep -v w1_bus_master || echo "No 1-Wire devices found"
    else
        print_warning "1-Wire not available"
    fi
    echo ""
    
    # Test Python sensor module
    print_status "Testing Python sensor module..."
    source venv/bin/activate
    python3 -m src.sensors --test || print_warning "Sensor test failed"
}

# Main installation function
install() {
    echo "Starting full installation..."
    echo ""
    
    install_system_deps
    enable_i2c
    enable_1wire
    create_directories
    setup_python
    install_service
    
    echo ""
    print_status "Installation complete!"
    echo ""
    print_warning "IMPORTANT: Reboot required for I2C and 1-Wire changes to take effect"
    print_warning "After reboot, test sensors with: ./setup.sh test"
    echo ""
}

# Command line interface
case "$1" in
    install)
        install
        ;;
    
    service)
        install_service
        ;;
    
    python)
        setup_python
        ;;
    
    test)
        test_sensors
        ;;
    
    *)
        echo "Usage: $0 {install|service|python|test}"
        echo ""
        echo "Commands:"
        echo "  install  - Full system installation (requires sudo)"
        echo "  service  - Install systemd service only (requires sudo)"
        echo "  python   - Setup Python environment only"
        echo "  test     - Test sensor connectivity"
        echo ""
        exit 1
        ;;
esac

exit 0
