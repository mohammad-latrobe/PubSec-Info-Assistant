# 🚀 Postman Testing Guide for LaTrobe University Information Assistant

## 📋 Overview
This guide provides step-by-step instructions for testing the LatrobeKBFetcher Azure Function using Postman.

## 🎯 Function Endpoints to Test

### 1. LatrobeKBFetcher Function (Azure Function App)
- **URL**: `https://ltu-troby-func-dev-3964.azurewebsites.net/api/LatrobeKBFetcher`
- **Method**: `GET`
- **Purpose**: Fetches knowledge base articles from LaTrobe API and processes them

### 2. Direct LaTrobe API (Reference Test)
- **URL**: `https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase`
- **Method**: `GET`
- **Purpose**: Direct test of the LaTrobe API to compare responses

---

## 🔧 Postman Setup Instructions

### Test 1: Direct LaTrobe API Test
This tests the original LaTrobe API directly.

**Request Configuration:**
```
Method: GET
URL: https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase
```

**Headers:**
```
Ocp-Apim-Subscription-Key: d1d001e93d6c4698bc954ec2426da2ad
Content-Type: application/json
```

**Query Parameters:**
```
Name: ICT
Active: true
Status_IN: published
```

**Expected Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body: JSON with Collection object containing Items array with knowledge base articles

---

### Test 2: Azure Function LatrobeKBFetcher Test
This tests our Azure Function that processes the LaTrobe API data.

**Request Configuration:**
```
Method: GET
URL: https://ltu-troby-func-dev-3964.azurewebsites.net/api/LatrobeKBFetcher
```

**Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
None required (function uses internal configuration)

**Expected Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body: JSON with processed articles array

---

## 📊 Expected Response Formats

### Direct LaTrobe API Response Structure:
```json
{
  "Collection": {
    "ID": "2da471d76f680200d965da55eb3ee404",
    "Name": "ISS",
    "Description": "IS client facing knowledge base.",
    "Items": {
      "Item": [
        {
          "ID": "b9ce181087c26e109a37c9570cbb3563",
          "Number": "KB0024305",
          "Name": "KB0024305",
          "Type": "text",
          "Active": true,
          "Status": "published",
          "Content": "<html content>",
          "Sample_Questions": "question1#question2#question3",
          "Short_Answer": "Brief description",
          "Authors": {...},
          "Location": {...}
        }
      ]
    }
  }
}
```

### Azure Function Response Structure:
```json
{
  "success": true,
  "articles": [
    {
      "id": "b9ce181087c26e109a37c9570cbb3563",
      "title": "KB0024305",
      "content": "Processed content...",
      "url": "https://latrobe...",
      "metadata": {
        "source": "latrobe_kb",
        "category": "ICT",
        "status": "published"
      }
    }
  ],
  "total_articles": 9,
  "timestamp": "2025-07-28T14:46:09Z"
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Basic Functionality Test
1. Test Direct LaTrobe API first
2. Verify Azure Function processes the data correctly
3. Compare response structures

### Scenario 2: Error Handling Test
1. Test with invalid subscription key (expect 401/403)
2. Test with malformed parameters (expect 400)
3. Test Azure Function when LaTrobe API is unreachable

### Scenario 3: Performance Test
1. Measure response times
2. Test multiple concurrent requests
3. Monitor cold start vs warm function performance

---

## 🔍 Troubleshooting Common Issues

### Issue 1: 503 Service Unavailable (Azure Function)
**Symptoms:** Function returns 503 error
**Causes:** 
- Function app is stopped
- Cold start taking too long
- Configuration issues

**Solutions:**
1. Wait 30-60 seconds and retry (cold start)
2. Check Azure Portal for function app status
3. Verify function app settings are configured

### Issue 2: 401/403 Unauthorized (LaTrobe API)
**Symptoms:** API returns authentication error
**Causes:**
- Invalid subscription key
- Expired credentials
- Wrong header format

**Solutions:**
1. Verify subscription key: `d1d001e93d6c4698bc954ec2426da2ad`
2. Check header name: `Ocp-Apim-Subscription-Key`
3. Ensure no extra spaces in key

### Issue 3: 404 Not Found
**Symptoms:** Endpoint not found
**Causes:**
- Wrong URL
- Function not deployed
- Typo in function name

**Solutions:**
1. Verify URL spelling
2. Check function deployment status
3. Try browser test first

---

## 📱 Postman Collection Export

### Quick Setup Collection
You can import this collection into Postman:

```json
{
  "info": {
    "name": "LaTrobe Information Assistant API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Direct LaTrobe API Test",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Ocp-Apim-Subscription-Key",
            "value": "d1d001e93d6c4698bc954ec2426da2ad"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": {
          "raw": "https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase?Name=ICT&Active=true&Status_IN=published",
          "protocol": "https",
          "host": ["ltu-api-test-apim", "azure-api", "net"],
          "path": ["collection", "v1", "KnowledgeBase"],
          "query": [
            {"key": "Name", "value": "ICT"},
            {"key": "Active", "value": "true"},
            {"key": "Status_IN", "value": "published"}
          ]
        }
      }
    },
    {
      "name": "2. Azure Function LatrobeKBFetcher",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": {
          "raw": "https://ltu-troby-func-dev-3964.azurewebsites.net/api/LatrobeKBFetcher",
          "protocol": "https",
          "host": ["ltu-troby-func-dev-3964", "azurewebsites", "net"],
          "path": ["api", "LatrobeKBFetcher"]
        }
      }
    }
  ]
}
```

---

## 🎯 Quick Test Steps

### Step 1: Test Direct API
1. Open Postman
2. Create new GET request
3. URL: `https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase`
4. Add header: `Ocp-Apim-Subscription-Key: d1d001e93d6c4698bc954ec2426da2ad`
5. Add params: `Name=ICT`, `Active=true`, `Status_IN=published`
6. Send request
7. Verify 200 response with knowledge base data

### Step 2: Test Azure Function
1. Create new GET request
2. URL: `https://ltu-troby-func-dev-3964.azurewebsites.net/api/LatrobeKBFetcher`
3. Send request
4. If 503 error, wait 60 seconds and retry (cold start)
5. Verify 200 response with processed articles

### Step 3: Compare Results
1. Check that Azure Function returns processed version of LaTrobe data
2. Verify article count matches
3. Confirm data structure is suitable for Microsoft PubSec-IA pipeline

---

## 📞 Support Information

If you encounter issues:
1. Check the terminal output for detailed error messages
2. Verify Azure Function App is running in Azure Portal
3. Test the direct LaTrobe API first to isolate issues
4. Review the function logs in Application Insights

**Test Results Expected:**
- Direct LaTrobe API: ✅ Working (confirmed)
- Azure Function: ⚠️ May need cold start time or configuration updates
