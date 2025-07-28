# Test script for PubSec Information Assistant Functions
# This script tests the KB article processing and indexing functions

import json
import requests
import time
from datetime import datetime

# Configuration - Update these with your actual function URLs
PROCESS_KB_FUNCTION_URL = "https://your-function-app.azurewebsites.net/api/ProcessKBArticles"
INDEX_KB_FUNCTION_URL = "https://your-function-app.azurewebsites.net/api/IndexKBChunks"
FUNCTION_KEY = "your-function-key"  # Get from Azure portal

# Sample KB articles for testing
sample_articles = [
    {
        "title": "Employee Handbook - Getting Started",
        "content": """Welcome to the company! This handbook provides essential information for new employees.

Getting Started:
Your first day is important. Please arrive at 9:00 AM and report to the front desk. You will receive your employee ID badge and access cards.

Office Hours:
Our standard office hours are Monday through Friday, 9:00 AM to 5:00 PM. Flexible working arrangements are available with manager approval.

Benefits Overview:
All full-time employees are eligible for health insurance, dental coverage, and retirement plans. Benefits enrollment begins after 30 days of employment.

IT Setup:
Your computer and phone will be set up by the IT department. You will receive login credentials and access to necessary systems within the first week.

Training Program:
New employees participate in a comprehensive training program covering company policies, procedures, and job-specific skills. Training typically lasts 2-3 weeks.

Contact Information:
For questions about your benefits, contact HR at hr@company.com. For IT support, email it-support@company.com.""",
        "url": "https://intranet.company.com/handbook/getting-started",
        "filename": "employee-handbook-getting-started",
        "metadata": {
            "author": "HR Department",
            "category": "Employee Resources",
            "tags": ["onboarding", "benefits", "training"],
            "department": "human_resources",
            "last_updated": "2024-01-15T10:00:00Z",
            "security": {
                "access_level": "internal",
                "security_groups": ["employees", "contractors"],
                "department": "all_departments",
                "classification": "internal"
            }
        }
    },
    {
        "title": "IT Security Policy",
        "content": """Information Technology Security Policy

Password Requirements:
All user passwords must be at least 12 characters long and include uppercase letters, lowercase letters, numbers, and special characters. Passwords must be changed every 90 days.

Data Classification:
Company data is classified into four categories:
1. Public - Can be shared freely
2. Internal - For company use only
3. Confidential - Restricted access required
4. Secret - Highest security clearance needed

Access Controls:
User access to systems and data must follow the principle of least privilege. Access requests must be approved by the data owner and system administrator.

Incident Reporting:
All security incidents must be reported immediately to the IT security team at security@company.com. This includes suspected malware, data breaches, and unauthorized access attempts.

Remote Work Security:
Employees working remotely must use company-approved VPN connections. Personal devices used for work must comply with company security standards.

Training Requirements:
All employees must complete annual cybersecurity awareness training. New employees must complete training within 30 days of hire.

Compliance:
This policy ensures compliance with industry standards including ISO 27001 and SOC 2 Type II requirements.""",
        "url": "https://intranet.company.com/policies/it-security",
        "filename": "it-security-policy",
        "metadata": {
            "author": "IT Security Team",
            "category": "Security Policies",
            "tags": ["security", "compliance", "passwords", "data-protection"],
            "department": "information_technology",
            "last_updated": "2024-01-10T14:30:00Z",
            "security": {
                "access_level": "confidential",
                "security_groups": ["employees", "security_team"],
                "department": "all_departments",
                "classification": "confidential"
            }
        }
    },
    {
        "title": "Travel and Expense Policy - Public Information",
        "content": """Travel and Expense Reimbursement Policy

Approval Process:
All business travel must be pre-approved by your direct supervisor. Travel requests should be submitted at least 2 weeks in advance.

Booking Procedures:
Use the company's preferred travel agency or online booking tool. Choose economy class for flights under 4 hours and business class for international flights over 8 hours.

Accommodation Guidelines:
Stay at business-class hotels with rates not exceeding $200 per night in major cities and $150 per night in other locations. Extended stay discounts should be negotiated for trips longer than 7 days.

Meal Allowances:
Daily meal allowances are $75 for domestic travel and $100 for international travel. Receipts are required for all meals over $25.

Transportation:
Use ground transportation when practical. Rental cars are approved for trips where public transportation is not available or cost-effective. Uber and taxi receipts under $50 do not require pre-approval.

Expense Reporting:
Submit expense reports within 30 days of travel completion. Include all receipts and provide business justification for each expense.

Reimbursement Timeline:
Approved expenses will be reimbursed within 2 weeks of submission. Direct deposit is the preferred payment method.""",
        "url": "https://company.com/policies/travel-expense",
        "filename": "travel-expense-policy-public",
        "metadata": {
            "author": "Finance Department",
            "category": "Financial Policies",
            "tags": ["travel", "expenses", "reimbursement", "policy"],
            "department": "finance",
            "last_updated": "2024-01-20T09:00:00Z",
            "security": {
                "access_level": "public",
                "security_groups": ["everyone"],
                "department": "general",
                "classification": "unclassified"
            }
        }
    }
]

def test_process_kb_articles():
    """Test the ProcessKBArticles function"""
    print("=" * 60)
    print("Testing ProcessKBArticles Function")
    print("=" * 60)
    
    headers = {
        "Content-Type": "application/json",
        "x-functions-key": FUNCTION_KEY
    }
    
    payload = {
        "articles": sample_articles
    }
    
    try:
        print(f"Sending {len(sample_articles)} articles to process...")
        response = requests.post(PROCESS_KB_FUNCTION_URL, headers=headers, json=payload, timeout=120)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ProcessKBArticles succeeded!")
            print(f"Articles processed: {result.get('articles_processed', 0)}")
            print(f"Total chunks created: {result.get('total_chunks_created', 0)}")
            
            # Show details for each article
            for detail in result.get('details', []):
                print(f"  - {detail['title']}: {detail['chunks_created']} chunks, {detail['chunks_uploaded']} uploaded")
            
            return True
        else:
            print(f"❌ ProcessKBArticles failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ProcessKBArticles: {str(e)}")
        return False

def test_index_kb_chunks():
    """Test the IndexKBChunks function"""
    print("\n" + "=" * 60)
    print("Testing IndexKBChunks Function")
    print("=" * 60)
    
    headers = {
        "Content-Type": "application/json",
        "x-functions-key": FUNCTION_KEY
    }
    
    # Test with default parameters
    try:
        print("Indexing KB article chunks...")
        response = requests.post(INDEX_KB_FUNCTION_URL, headers=headers, timeout=180)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ IndexKBChunks succeeded!")
            print(f"Total processed: {result.get('total_processed', 0)}")
            print(f"Successfully indexed: {result.get('indexed_count', 0)}")
            print(f"Failed: {result.get('failed_count', 0)}")
            
            # Show details for each processed file
            processed_files = result.get('processed_files', [])
            if processed_files:
                print("\nProcessed files:")
                for file_info in processed_files[:10]:  # Show first 10
                    status = file_info.get('status', 'unknown')
                    blob_name = file_info.get('blob_name', 'unknown')
                    print(f"  - {blob_name}: {status}")
                
                if len(processed_files) > 10:
                    print(f"  ... and {len(processed_files) - 10} more files")
            
            return True
        else:
            print(f"❌ IndexKBChunks failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing IndexKBChunks: {str(e)}")
        return False

def test_search_functionality():
    """Test basic search functionality (if you have a search function)"""
    print("\n" + "=" * 60)
    print("Search Functionality Test")
    print("=" * 60)
    print("ℹ️  This would test search queries against the indexed data")
    print("ℹ️  Implement this after creating a search function")

def main():
    """Run all tests"""
    print("🚀 Starting PubSec Information Assistant Function Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Update URLs with actual function app name
    print(f"\nFunction URLs:")
    print(f"  ProcessKBArticles: {PROCESS_KB_FUNCTION_URL}")
    print(f"  IndexKBChunks: {INDEX_KB_FUNCTION_URL}")
    
    if "your-function-app" in PROCESS_KB_FUNCTION_URL:
        print("\n⚠️  WARNING: Please update the function URLs and keys in this script!")
        print("⚠️  Replace 'your-function-app' with your actual function app name")
        print("⚠️  Replace 'your-function-key' with your actual function key")
        return
    
    # Test 1: Process KB Articles
    success1 = test_process_kb_articles()
    
    if success1:
        # Wait a bit for blob processing
        print("\n⏳ Waiting 10 seconds for blob processing...")
        time.sleep(10)
        
        # Test 2: Index chunks
        success2 = test_index_kb_chunks()
        
        if success2:
            print("\n🎉 All tests completed successfully!")
            print("\nNext steps:")
            print("1. Check Azure AI Search index for the indexed documents")
            print("2. Test search queries in Azure portal")
            print("3. Implement additional functions as needed")
        else:
            print("\n❌ Indexing test failed. Check function logs for details.")
    else:
        print("\n❌ Article processing test failed. Fix this before proceeding.")
    
    # Test 3: Search functionality placeholder
    test_search_functionality()

if __name__ == "__main__":
    main()
