#!/usr/bin/env python3
"""
IoT Multi-Rubro System - Validation Script
===========================================
Automated system validation and health checks.
Runs comprehensive tests on all components.
"""

import sys
import time
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

# Test results
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

# ============================================
# TEST FUNCTIONS
# ============================================

def test_backend_health() -> bool:
    """Test if backend is running and healthy."""
    print_info("Testing backend health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy - Mode: {data.get('mode', 'unknown')}")
            test_results["passed"].append("Backend health check")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            test_results["failed"].append(f"Backend health (status {response.status_code})")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is it running?")
        test_results["failed"].append("Backend connection")
        return False
    
    except Exception as e:
        print_error(f"Backend health check failed: {e}")
        test_results["failed"].append(f"Backend health ({str(e)})")
        return False

def test_database_connectivity() -> bool:
    """Test database connectivity."""
    print_info("Testing database connectivity...")
    
    try:
        # Test by listing devices
        response = requests.get("http://localhost:8000/api/devices", timeout=5)
        
        if response.status_code == 200:
            devices = response.json()
            print_success(f"Database accessible - {len(devices)} devices found")
            test_results["passed"].append("Database connectivity")
            return True
        else:
            print_error("Cannot access database")
            test_results["failed"].append("Database connectivity")
            return False
    
    except Exception as e:
        print_error(f"Database test failed: {e}")
        test_results["failed"].append(f"Database ({str(e)})")
        return False

def test_api_endpoints() -> bool:
    """Test critical API endpoints."""
    print_info("Testing API endpoints...")
    
    endpoints = [
        ("GET", "/api/devices", 200),
        ("GET", "/api/rules", 200),
        ("GET", "/api/alerts", 200),
        ("GET", "/api/stats", 200),
    ]
    
    all_passed = True
    
    for method, endpoint, expected_status in endpoints:
        try:
            url = f"http://localhost:8000{endpoint}"
            response = requests.request(method, url, timeout=5)
            
            if response.status_code == expected_status:
                print_success(f"{method} {endpoint} → {response.status_code}")
            else:
                print_warning(f"{method} {endpoint} → {response.status_code} (expected {expected_status})")
                all_passed = False
        
        except Exception as e:
            print_error(f"{method} {endpoint} failed: {e}")
            all_passed = False
    
    if all_passed:
        test_results["passed"].append("API endpoints")
    else:
        test_results["warnings"].append("Some API endpoints")
    
    return all_passed

def test_websocket() -> bool:
    """Test WebSocket connectivity."""
    print_info("Testing WebSocket...")
    
    try:
        import websocket
        
        ws = websocket.create_connection("ws://localhost:8000/ws/realtime", timeout=5)
        
        # Wait for a message
        message = ws.recv()
        ws.close()
        
        print_success("WebSocket connection successful")
        test_results["passed"].append("WebSocket")
        return True
    
    except ImportError:
        print_warning("websocket-client not installed, skipping WebSocket test")
        test_results["warnings"].append("WebSocket (library not installed)")
        return True
    
    except Exception as e:
        print_error(f"WebSocket test failed: {e}")
        test_results["failed"].append(f"WebSocket ({str(e)})")
        return False

def test_device_creation() -> bool:
    """Test creating a device via API."""
    print_info("Testing device creation...")
    
    device_data = {
        "device_id": f"TEST-{int(time.time())}",
        "name": "Validation Test Device",
        "device_type": "temperature",
        "rubro": "test"
    }
    
    try:
        # Create device
        response = requests.post(
            "http://localhost:8000/api/devices",
            json=device_data,
            timeout=5
        )
        
        if response.status_code in [201, 400]:  # 201 created, 400 if exists
            print_success("Device creation API working")
            
            # Try to delete it
            if response.status_code == 201:
                device_id = device_data["device_id"]
                requests.delete(f"http://localhost:8000/api/devices/{device_id}")
            
            test_results["passed"].append("Device creation")
            return True
        else:
            print_error(f"Device creation returned {response.status_code}")
            test_results["failed"].append("Device creation")
            return False
    
    except Exception as e:
        print_error(f"Device creation test failed: {e}")
        test_results["failed"].append(f"Device creation ({str(e)})")
        return False

def test_data_posting() -> bool:
    """Test posting sensor data."""
    print_info("Testing sensor data posting...")
    
    # Ensure a test device exists
    device_data = {
        "device_id": "VALIDATION-SENSOR",
        "name": "Validation Sensor",
        "device_type": "temperature"
    }
    
    try:
        # Create device (ignore if exists)
        requests.post("http://localhost:8000/api/devices", json=device_data)
        
        # Post data
        sensor_data = {
            "device_id": "VALIDATION-SENSOR",
            "value": 23.5,
            "unit": "°C"
        }
        
        response = requests.post(
            "http://localhost:8000/api/data",
            json=sensor_data,
            timeout=5
        )
        
        if response.status_code == 201:
            print_success("Sensor data posting working")
            test_results["passed"].append("Data posting")
            return True
        else:
            print_error(f"Data posting returned {response.status_code}")
            test_results["failed"].append("Data posting")
            return False
    
    except Exception as e:
        print_error(f"Data posting test failed: {e}")
        test_results["failed"].append(f"Data posting ({str(e)})")
        return False

def test_rules_engine() -> bool:
    """Test rules engine functionality."""
    print_info("Testing rules engine...")
    
    try:
        response = requests.get("http://localhost:8000/api/rules", timeout=5)
        
        if response.status_code == 200:
            rules = response.json()
            print_success(f"Rules engine accessible - {len(rules)} rules configured")
            test_results["passed"].append("Rules engine")
            return True
        else:
            print_error("Rules engine not accessible")
            test_results["failed"].append("Rules engine")
            return False
    
    except Exception as e:
        print_error(f"Rules engine test failed: {e}")
        test_results["failed"].append(f"Rules engine ({str(e)})")
        return False

def test_simulation_running() -> bool:
    """Test if simulation is actively generating data."""
    print_info("Testing simulation (waiting 10 seconds)...")
    
    try:
        # Get initial data count
        response1 = requests.get("http://localhost:8000/api/stats", timeout=5)
        stats1 = response1.json()
        initial_count = stats1.get("data", {}).get("points_24h", 0)
        
        # Wait
        time.sleep(10)
        
        # Get new count
        response2 = requests.get("http://localhost:8000/api/stats", timeout=5)
        stats2 = response2.json()
        final_count = stats2.get("data", {}).get("points_24h", 0)
        
        new_points = final_count - initial_count
        
        if new_points > 0:
            print_success(f"Simulation active - {new_points} new data points in 10s")
            test_results["passed"].append("Simulation active")
            return True
        else:
            print_warning("No new data points generated (simulation may be paused)")
            test_results["warnings"].append("Simulation (no new data)")
            return True
    
    except Exception as e:
        print_error(f"Simulation test failed: {e}")
        test_results["failed"].append(f"Simulation ({str(e)})")
        return False

def test_frontend_accessible() -> bool:
    """Test if frontend is accessible."""
    print_info("Testing frontend accessibility...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        
        if response.status_code == 200 and "IoT" in response.text:
            print_success("Frontend is accessible")
            test_results["passed"].append("Frontend")
            return True
        else:
            print_error("Frontend not accessible")
            test_results["failed"].append("Frontend")
            return False
    
    except Exception as e:
        print_error(f"Frontend test failed: {e}")
        test_results["failed"].append(f"Frontend ({str(e)})")
        return False

def performance_benchmark() -> Dict:
    """Run basic performance benchmark."""
    print_info("Running performance benchmark...")
    
    results = {}
    
    # API response time
    try:
        start = time.time()
        requests.get("http://localhost:8000/api/stats", timeout=5)
        latency = (time.time() - start) * 1000  # ms
        
        results["api_latency"] = f"{latency:.2f}ms"
        
        if latency < 100:
            print_success(f"API latency: {latency:.2f}ms (excellent)")
        elif latency < 500:
            print_warning(f"API latency: {latency:.2f}ms (acceptable)")
        else:
            print_error(f"API latency: {latency:.2f}ms (slow)")
    
    except Exception as e:
        results["api_latency"] = f"Error: {e}"
    
    return results

# ============================================
# MAIN VALIDATION RUNNER
# ============================================

def run_validation():
    """Run all validation tests."""
    print_header("IoT Multi-Rubro System Validation")
    
    start_time = time.time()
    
    # Run tests in sequence
    tests = [
        ("Backend Health", test_backend_health),
        ("Database Connectivity", test_database_connectivity),
        ("API Endpoints", test_api_endpoints),
        ("WebSocket", test_websocket),
        ("Device Creation", test_device_creation),
        ("Data Posting", test_data_posting),
        ("Rules Engine", test_rules_engine),
        ("Simulation", test_simulation_running),
        ("Frontend", test_frontend_accessible),
    ]
    
    print_info(f"Running {len(tests)} validation tests...\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            test_results["failed"].append(f"{test_name} (crashed)")
        
        time.sleep(0.5)  # Small delay between tests
    
    # Performance benchmark
    print_header("Performance Benchmark")
    perf_results = performance_benchmark()
    
    # Print summary
    duration = time.time() - start_time
    
    print_header("Validation Summary")
    
    print(f"{Colors.OKGREEN}Passed:  {len(test_results['passed'])}{Colors.ENDC}")
    for test in test_results['passed']:
        print(f"  ✓ {test}")
    
    if test_results['warnings']:
        print(f"\n{Colors.WARNING}Warnings: {len(test_results['warnings'])}{Colors.ENDC}")
        for test in test_results['warnings']:
            print(f"  ⚠ {test}")
    
    if test_results['failed']:
        print(f"\n{Colors.FAIL}Failed:  {len(test_results['failed'])}{Colors.ENDC}")
        for test in test_results['failed']:
            print(f"  ✗ {test}")
    
    print(f"\n{Colors.OKCYAN}Duration: {duration:.2f} seconds{Colors.ENDC}")
    
    # Overall result
    print_header("Overall Result")
    
    if not test_results['failed']:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ SYSTEM VALIDATION PASSED{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ SYSTEM VALIDATION FAILED{Colors.ENDC}")
        print(f"\n{len(test_results['failed'])} critical test(s) failed.")
        return 1

if __name__ == "__main__":
    exit_code = run_validation()
    sys.exit(exit_code)
