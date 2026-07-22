#!/usr/bin/env python3
"""
Backend API Test Suite for Juan Operating System Dashboard
Tests all dashboard endpoints for proper functionality and data structure
"""

import requests
import json
import sys
from typing import Dict, Any

# Base URL from environment
BASE_URL = "https://neon-dashboard-54.preview.emergentagent.com/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def test_dashboard_stats():
    """Test GET /api/dashboard/stats endpoint"""
    print("\n" + "="*70)
    print("Testing: GET /api/dashboard/stats")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats", timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Expected status 200, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
        
        data = response.json()
        print_info(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate required fields
        required_fields = ['agentsOnline', 'workflowsRunning', 'signalsToday', 'successRate', 'systemHealth']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print_error(f"Missing required fields: {missing_fields}")
            return False
        
        # Validate data types
        if not isinstance(data['agentsOnline'], int):
            print_error(f"agentsOnline should be int, got {type(data['agentsOnline'])}")
            return False
        
        if not isinstance(data['workflowsRunning'], int):
            print_error(f"workflowsRunning should be int, got {type(data['workflowsRunning'])}")
            return False
        
        if not isinstance(data['signalsToday'], int):
            print_error(f"signalsToday should be int, got {type(data['signalsToday'])}")
            return False
        
        if not isinstance(data['successRate'], (int, float)):
            print_error(f"successRate should be number, got {type(data['successRate'])}")
            return False
        
        if data['systemHealth'] not in ['Excellent', 'Degraded']:
            print_error(f"systemHealth should be 'Excellent' or 'Degraded', got {data['systemHealth']}")
            return False
        
        print_success("All fields present and valid")
        print_success(f"Stats: {data['agentsOnline']} agents, {data['workflowsRunning']} workflows, {data['signalsToday']} signals, {data['successRate']}% success, {data['systemHealth']} health")
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def test_dashboard_workflows():
    """Test GET /api/dashboard/workflows endpoint"""
    print("\n" + "="*70)
    print("Testing: GET /api/dashboard/workflows")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/workflows", timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Expected status 200, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
        
        data = response.json()
        print_info(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate structure
        if 'workflows' not in data:
            print_error("Missing 'workflows' field in response")
            return False
        
        if not isinstance(data['workflows'], list):
            print_error(f"workflows should be array, got {type(data['workflows'])}")
            return False
        
        print_success(f"Received {len(data['workflows'])} workflows")
        
        # Validate workflow structure if any workflows exist
        if len(data['workflows']) > 0:
            workflow = data['workflows'][0]
            required_fields = ['id', 'name', 'type', 'status', 'progress']
            missing_fields = [field for field in required_fields if field not in workflow]
            
            if missing_fields:
                print_error(f"Workflow missing required fields: {missing_fields}")
                return False
            
            print_success(f"Sample workflow: {workflow['name']} - {workflow['status']} ({workflow['progress']}%)")
        else:
            print_warning("No workflows in database (this is OK if database is empty)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def test_dashboard_signals():
    """Test GET /api/dashboard/signals endpoint"""
    print("\n" + "="*70)
    print("Testing: GET /api/dashboard/signals")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/signals", timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Expected status 200, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
        
        data = response.json()
        print_info(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate structure
        if 'signals' not in data:
            print_error("Missing 'signals' field in response")
            return False
        
        if not isinstance(data['signals'], list):
            print_error(f"signals should be array, got {type(data['signals'])}")
            return False
        
        print_success(f"Received {len(data['signals'])} signals")
        
        # Validate signal structure if any signals exist
        if len(data['signals']) > 0:
            signal = data['signals'][0]
            required_fields = ['id', 'type', 'title', 'campaign', 'timeAgo', 'score']
            missing_fields = [field for field in required_fields if field not in signal]
            
            if missing_fields:
                print_error(f"Signal missing required fields: {missing_fields}")
                return False
            
            print_success(f"Sample signal: {signal['title']} - {signal['score']} ({signal['timeAgo']})")
        else:
            print_warning("No signals in database (this is OK if database is empty)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def test_dashboard_analytics():
    """Test GET /api/dashboard/analytics endpoint"""
    print("\n" + "="*70)
    print("Testing: GET /api/dashboard/analytics")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/analytics", timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Expected status 200, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
        
        data = response.json()
        print_info(f"Response: {json.dumps(data, indent=2)}")
        
        # Validate required fields
        required_fields = ['signalsByCampaign', 'signalClassification', 'leadsPipeline', 'dailyTrend']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print_error(f"Missing required fields: {missing_fields}")
            return False
        
        # Validate data types
        if not isinstance(data['signalsByCampaign'], list):
            print_error(f"signalsByCampaign should be array, got {type(data['signalsByCampaign'])}")
            return False
        
        if not isinstance(data['signalClassification'], list):
            print_error(f"signalClassification should be array, got {type(data['signalClassification'])}")
            return False
        
        if not isinstance(data['leadsPipeline'], dict):
            print_error(f"leadsPipeline should be object, got {type(data['leadsPipeline'])}")
            return False
        
        if not isinstance(data['dailyTrend'], list):
            print_error(f"dailyTrend should be array, got {type(data['dailyTrend'])}")
            return False
        
        print_success("All fields present and valid")
        print_success(f"Analytics: {len(data['signalsByCampaign'])} campaigns, {len(data['signalClassification'])} classifications, {len(data['dailyTrend'])} trend points")
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def main():
    """Run all dashboard API tests"""
    print("\n" + "="*70)
    print("JUAN OPERATING SYSTEM - DASHBOARD API TEST SUITE")
    print("="*70)
    
    results = {
        'stats': test_dashboard_stats(),
        'workflows': test_dashboard_workflows(),
        'signals': test_dashboard_signals(),
        'analytics': test_dashboard_analytics(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for endpoint, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - /api/dashboard/{endpoint}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All dashboard endpoints are working correctly!")
        return 0
    else:
        print_error(f"{total - passed} endpoint(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
