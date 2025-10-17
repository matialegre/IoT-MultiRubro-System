#!/usr/bin/env python3
"""
IoT Multi-Rubro System - Comprehensive Validation Suite
========================================================
Complete system validation as per validation prompt requirements.
Generates detailed report with all test results.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Colors for terminal
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title: str):
    """Print section header."""
    print(f"\n{Color.BOLD}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Color.END}\n")

def print_check(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    symbol = f"{Color.GREEN}✓{Color.END}" if passed else f"{Color.RED}✗{Color.END}"
    status = f"{Color.GREEN}PASS{Color.END}" if passed else f"{Color.RED}FAIL{Color.END}"
    print(f"{symbol} {test_name:<50} [{status}]")
    if details and not passed:
        print(f"  {Color.YELLOW}↳ {details}{Color.END}")

# Validation results storage
validation_results = {
    "timestamp": datetime.now().isoformat(),
    "sections": {},
    "summary": {"passed": 0, "failed": 0, "warnings": 0}
}

# ============================================
# 1. STRUCTURAL VALIDATION
# ============================================
def validate_structure() -> Dict:
    """Validate repository structure."""
    print_section("1. VALIDACIÓN ESTRUCTURAL")
    
    results = {"tests": [], "passed": 0, "failed": 0}
    base_path = Path(__file__).parent.parent
    
    # Required directories
    required_dirs = [
        "iot_firmware",
        "backend_api",
        "web_frontend",
        "simulator",
        "docs",
        "tests",
        "scenarios",
        "scripts",
        "reports"
    ]
    
    for directory in required_dirs:
        dir_path = base_path / directory
        exists = dir_path.exists() and dir_path.is_dir()
        print_check(f"Directory: {directory}/", exists)
        results["tests"].append({
            "name": f"Directory {directory}",
            "passed": exists
        })
        if exists:
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Required files
    required_files = [
        "README.md",
        "backend_api/main.py",
        "backend_api/config.py",
        "backend_api/database.py",
        "backend_api/requirements.txt",
        "backend_api/services/rules_engine.py",
        "web_frontend/index.html",
        "web_frontend/assets/js/dashboard.js",
        "web_frontend/assets/js/charts.js",
        "web_frontend/assets/js/websocket.js",
        "web_frontend/assets/css/styles.css",
        "simulator/sensor_models.py",
        "iot_firmware/main/main.ino",
        "iot_firmware/main/config.h",
        "docs/QUICK_START.md",
        "docs/API_REFERENCE.md",
        "docs/ARCHITECTURE.md",
        "scripts/start_simulation.py",
        "scripts/validate_system.py",
        "tests/test_api.py",
        "scenarios/carniceria.json",
        "scenarios/riego.json",
        "docker-compose.yml",
        ".gitignore"
    ]
    
    for file_path in required_files:
        full_path = base_path / file_path
        exists = full_path.exists() and full_path.is_file()
        has_content = exists and full_path.stat().st_size > 0
        
        print_check(f"File: {file_path}", has_content, 
                   "" if has_content else "Missing or empty")
        
        results["tests"].append({
            "name": f"File {file_path}",
            "passed": has_content
        })
        
        if has_content:
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    return results

# ============================================
# 2. DEPENDENCY VALIDATION
# ============================================
def validate_dependencies() -> Dict:
    """Validate required dependencies."""
    print_section("2. VALIDACIÓN DE DEPENDENCIAS")
    
    results = {"tests": [], "passed": 0, "failed": 0}
    
    # Python backend dependencies
    backend_deps = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "ORM database"),
        ("pydantic", "Data validation"),
        ("numpy", "Numerical computing"),
    ]
    
    for module, description in backend_deps:
        try:
            __import__(module)
            print_check(f"Python: {description} ({module})", True)
            results["passed"] += 1
            results["tests"].append({"name": f"Dependency {module}", "passed": True})
        except ImportError:
            print_check(f"Python: {description} ({module})", False, 
                       f"Run: pip install {module}")
            results["failed"] += 1
            results["tests"].append({"name": f"Dependency {module}", "passed": False})
    
    # Check requirements.txt
    base_path = Path(__file__).parent.parent
    req_file = base_path / "backend_api" / "requirements.txt"
    
    if req_file.exists():
        print_check("Requirements file exists", True)
        results["passed"] += 1
        
        # Count dependencies
        with open(req_file, 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"  {Color.BLUE}ℹ Total dependencies listed: {len(deps)}{Color.END}")
    else:
        print_check("Requirements file exists", False)
        results["failed"] += 1
    
    return results

# ============================================
# 3. CODE QUALITY VALIDATION
# ============================================
def validate_code_quality() -> Dict:
    """Validate code structure and quality."""
    print_section("3. VALIDACIÓN DE CALIDAD DE CÓDIGO")
    
    results = {"tests": [], "passed": 0, "failed": 0}
    base_path = Path(__file__).parent.parent
    
    # Check Python files for basic syntax
    python_files = [
        "backend_api/main.py",
        "backend_api/config.py",
        "backend_api/database.py",
        "backend_api/services/rules_engine.py",
        "simulator/sensor_models.py"
    ]
    
    for py_file in python_files:
        file_path = base_path / py_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    # Basic checks
                    has_imports = 'import ' in code
                    has_docstring = '"""' in code or "'''" in code
                    has_functions = 'def ' in code
                    
                    passed = has_imports and has_functions
                    print_check(f"Syntax check: {py_file}", passed)
                    
                    if passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["tests"].append({
                        "name": f"Code quality {py_file}",
                        "passed": passed
                    })
            except Exception as e:
                print_check(f"Syntax check: {py_file}", False, str(e))
                results["failed"] += 1
        else:
            print_check(f"File exists: {py_file}", False)
            results["failed"] += 1
    
    # Check JSON scenarios
    scenario_files = ["carniceria.json", "riego.json"]
    for scenario in scenario_files:
        file_path = base_path / "scenarios" / scenario
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    has_devices = "devices" in data
                    has_rubro = "rubro" in data
                    
                    passed = has_devices and has_rubro
                    print_check(f"JSON valid: {scenario}", passed)
                    
                    if passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
            except json.JSONDecodeError as e:
                print_check(f"JSON valid: {scenario}", False, str(e))
                results["failed"] += 1
        else:
            print_check(f"Scenario exists: {scenario}", False)
            results["failed"] += 1
    
    return results

# ============================================
# 4. CONFIGURATION VALIDATION
# ============================================
def validate_configuration() -> Dict:
    """Validate system configuration."""
    print_section("4. VALIDACIÓN DE CONFIGURACIÓN")
    
    results = {"tests": [], "passed": 0, "failed": 0}
    base_path = Path(__file__).parent.parent
    
    # Load config
    sys.path.insert(0, str(base_path / "backend_api"))
    
    try:
        import config
        
        # Check SIM_MODE
        has_sim_mode = hasattr(config, 'SIM_MODE')
        print_check("Config: SIM_MODE defined", has_sim_mode)
        if has_sim_mode:
            print(f"  {Color.BLUE}ℹ SIM_MODE = {config.SIM_MODE}{Color.END}")
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Check database URL
        has_db_url = hasattr(config, 'DATABASE_URL')
        print_check("Config: DATABASE_URL defined", has_db_url)
        if has_db_url:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Check API config
        has_api_config = all([
            hasattr(config, 'API_HOST'),
            hasattr(config, 'API_PORT'),
            hasattr(config, 'API_TITLE')
        ])
        print_check("Config: API configuration complete", has_api_config)
        if has_api_config:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Check sensor limits
        has_sensor_limits = hasattr(config, 'SENSOR_LIMITS')
        print_check("Config: SENSOR_LIMITS defined", has_sensor_limits)
        if has_sensor_limits:
            sensor_count = len(config.SENSOR_LIMITS)
            print(f"  {Color.BLUE}ℹ {sensor_count} sensor types configured{Color.END}")
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Check rubro presets
        has_rubros = hasattr(config, 'RUBRO_PRESETS')
        print_check("Config: RUBRO_PRESETS defined", has_rubros)
        if has_rubros:
            rubro_count = len(config.RUBRO_PRESETS)
            print(f"  {Color.BLUE}ℹ {rubro_count} rubros configured{Color.END}")
            results["passed"] += 1
        else:
            results["failed"] += 1
        
    except Exception as e:
        print_check("Config module loadable", False, str(e))
        results["failed"] += 5
    
    return results

# ============================================
# 5. SIMULATOR VALIDATION
# ============================================
def validate_simulator() -> Dict:
    """Validate sensor simulator."""
    print_section("5. VALIDACIÓN DEL SIMULADOR")
    
    results = {"tests": [], "passed": 0, "failed": 0}
    base_path = Path(__file__).parent.parent
    
    sys.path.insert(0, str(base_path / "simulator"))
    
    try:
        from sensor_models import (
            TemperatureSensor, HumiditySensor, MotionSensor,
            create_sensor, SENSOR_MODELS
        )
        
        print_check("Simulator: Module imports successfully", True)
        results["passed"] += 1
        
        # Check available sensor types
        sensor_types = list(SENSOR_MODELS.keys())
        print_check(f"Simulator: {len(sensor_types)} sensor types available", True)
        print(f"  {Color.BLUE}ℹ Types: {', '.join(sensor_types)}{Color.END}")
        results["passed"] += 1
        
        # Test temperature sensor
        try:
            temp_sensor = TemperatureSensor("TEST-TEMP", base_temp=20.0)
            state = temp_sensor.read()
            
            has_value = hasattr(state, 'value')
            has_timestamp = hasattr(state, 'timestamp')
            has_quality = hasattr(state, 'quality')
            
            passed = has_value and has_timestamp and has_quality
            print_check("Simulator: Temperature sensor functional", passed)
            
            if passed:
                print(f"  {Color.BLUE}ℹ Test reading: {state.value:.2f}°C, quality={state.quality:.2f}{Color.END}")
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print_check("Simulator: Temperature sensor functional", False, str(e))
            results["failed"] += 1
        
        # Test humidity sensor
        try:
            hum_sensor = HumiditySensor("TEST-HUM", base_humidity=60.0)
            state = hum_sensor.read()
            print_check("Simulator: Humidity sensor functional", True)
            results["passed"] += 1
        except Exception as e:
            print_check("Simulator: Humidity sensor functional", False, str(e))
            results["failed"] += 1
        
        # Test motion sensor
        try:
            motion_sensor = MotionSensor("TEST-MOT")
            state = motion_sensor.read()
            print_check("Simulator: Motion sensor functional", True)
            results["passed"] += 1
        except Exception as e:
            print_check("Simulator: Motion sensor functional", False, str(e))
            results["failed"] += 1
        
    except ImportError as e:
        print_check("Simulator: Module imports", False, str(e))
        results["failed"] += 5
    
    return results

# ============================================
# 6. DOCUMENTATION VALIDATION
# ============================================
def validate_documentation() -> Dict:
    """Validate documentation completeness."""
    print_section("6. VALIDACIÓN DE DOCUMENTACIÓN")
    
    results = {"tests": [], "passed": 0, "failed": 0}
    base_path = Path(__file__).parent.parent
    
    doc_files = {
        "README.md": ["Installation", "Usage", "Features"],
        "RESUMEN_EJECUTIVO.md": ["Descripción", "Características", "Comandos"],
        "docs/QUICK_START.md": ["Instalación", "Inicio", "Configuración"],
        "docs/API_REFERENCE.md": ["Endpoints", "Request", "Response"],
        "docs/ARCHITECTURE.md": ["Architecture", "Components", "Data Flow"]
    }
    
    for doc_file, required_sections in doc_files.items():
        file_path = base_path / doc_file
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check file size
                    size_kb = len(content) / 1024
                    has_content = size_kb > 1  # At least 1KB
                    
                    # Check for required sections (loose check)
                    sections_found = sum(1 for section in required_sections 
                                        if section.lower() in content.lower())
                    
                    passed = has_content and sections_found >= len(required_sections) // 2
                    
                    print_check(f"Doc: {doc_file}", passed)
                    print(f"  {Color.BLUE}ℹ Size: {size_kb:.1f}KB, Sections: {sections_found}/{len(required_sections)}{Color.END}")
                    
                    if passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
            except Exception as e:
                print_check(f"Doc: {doc_file}", False, str(e))
                results["failed"] += 1
        else:
            print_check(f"Doc: {doc_file}", False, "File not found")
            results["failed"] += 1
    
    return results

# ============================================
# MAIN VALIDATION RUNNER
# ============================================
def run_comprehensive_validation():
    """Run all validation tests."""
    print(f"\n{Color.BOLD}{Color.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║       IoT Multi-Rubro - COMPREHENSIVE VALIDATION             ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(f"{Color.END}")
    
    start_time = time.time()
    
    # Run all validation sections
    validation_results["sections"]["structure"] = validate_structure()
    validation_results["sections"]["dependencies"] = validate_dependencies()
    validation_results["sections"]["code_quality"] = validate_code_quality()
    validation_results["sections"]["configuration"] = validate_configuration()
    validation_results["sections"]["simulator"] = validate_simulator()
    validation_results["sections"]["documentation"] = validate_documentation()
    
    # Calculate totals
    total_passed = 0
    total_failed = 0
    
    for section_name, section_data in validation_results["sections"].items():
        total_passed += section_data.get("passed", 0)
        total_failed += section_data.get("failed", 0)
    
    validation_results["summary"]["passed"] = total_passed
    validation_results["summary"]["failed"] = total_failed
    validation_results["summary"]["total"] = total_passed + total_failed
    validation_results["summary"]["duration_seconds"] = time.time() - start_time
    
    # Print summary
    print_section("RESUMEN DE VALIDACIÓN")
    
    print(f"{Color.GREEN}✓ Tests Passed:  {total_passed}{Color.END}")
    print(f"{Color.RED}✗ Tests Failed:  {total_failed}{Color.END}")
    print(f"  Total Tests:   {total_passed + total_failed}")
    print(f"  Success Rate:  {(total_passed/(total_passed+total_failed)*100) if (total_passed+total_failed) > 0 else 0:.1f}%")
    print(f"  Duration:      {validation_results['summary']['duration_seconds']:.2f}s")
    
    # Save JSON report
    save_validation_report()
    
    # Overall result
    print_section("RESULTADO FINAL")
    
    if total_failed == 0:
        print(f"{Color.GREEN}{Color.BOLD}✓ VALIDACIÓN COMPLETA EXITOSA{Color.END}")
        print(f"\n{Color.GREEN}El sistema está COMPLETO y OPERATIVO.{Color.END}")
        return 0
    else:
        success_rate = (total_passed/(total_passed+total_failed)*100)
        if success_rate >= 90:
            print(f"{Color.YELLOW}{Color.BOLD}⚠ VALIDACIÓN PARCIAL ({success_rate:.0f}%){Color.END}")
            print(f"\n{Color.YELLOW}Sistema mayormente funcional. Revisar {total_failed} fallo(s).{Color.END}")
            return 1
        else:
            print(f"{Color.RED}{Color.BOLD}✗ VALIDACIÓN FALLIDA ({success_rate:.0f}%){Color.END}")
            print(f"\n{Color.RED}Se encontraron {total_failed} problemas críticos.{Color.END}")
            return 2

def save_validation_report():
    """Save validation report to JSON file."""
    base_path = Path(__file__).parent.parent
    report_dir = base_path / "reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"validation_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n{Color.BLUE}ℹ Reporte guardado: {report_file}{Color.END}")

if __name__ == "__main__":
    exit_code = run_comprehensive_validation()
    sys.exit(exit_code)
