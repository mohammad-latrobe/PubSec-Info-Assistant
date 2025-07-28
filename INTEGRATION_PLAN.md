# 🎯 LaTrobe API + Microsoft PubSec-IA Integration Plan
## **MINIMAL CHANGES - STEP BY STEP TESTING**

## ✅ What We've Done (Zero Changes to Microsoft Code)

### Step 1: ✅ API Connection Verified
- **File**: `tests/step1_test_api.py`
- **Result**: LaTrobe API accessible, requires `name` parameter
- **Status**: ✅ Ready

### Step 2: ✅ Minimal Integration Created  
- **File**: `functions/LatrobeKBFetcher/__init__.py` (NEW - only addition)
- **Strategy**: Feed into existing Microsoft pipeline via upload container
- **Changes**: 
  - ✅ Added 1 new function (LatrobeKBFetcher)
  - ✅ Added required environment variables to deployment script
  - ❌ **ZERO changes** to existing Microsoft functions
- **Status**: ✅ Ready for deployment

## 🚀 Next Steps (Step by Step Testing)

### Step 3: Deploy Infrastructure
```powershell
# Run the deployment script (contains LaTrobe API settings)
.\infrastructure\scripts\deploy-simplified.ps1 -ResourceGroupName "rg-pubsec-test" -Location "eastus"
```

### Step 4: Deploy Functions
```powershell
# Deploy all functions (including our new LatrobeKBFetcher)
func azure functionapp publish <function-app-name>
```

### Step 5: Test Integration
```powershell
# Test our new function
curl -X POST "https://<function-app-name>.azurewebsites.net/api/LatrobeKBFetcher"

# Verify Microsoft pipeline processes the uploaded files
# Check upload container and content container in Azure Storage
```

### Step 6: Monitor Microsoft Pipeline
- Our LatrobeKBFetcher uploads files to `upload` container
- Microsoft's FileUploadedFunc (unchanged) automatically processes them
- Content flows through existing Microsoft pipeline:
  1. FileUploadedFunc → 
  2. FileLayoutParsingOther → 
  3. TextEnrichment → 
  4. Search Index

## 🎯 Integration Architecture

```
LaTrobe API
     ↓
LatrobeKBFetcher (NEW)
     ↓
Upload Container
     ↓
Microsoft PubSec-IA Pipeline (UNCHANGED)
     ↓
Search Index
```

## 🔧 Files Changed (Minimal)

### New Files Added:
1. `functions/LatrobeKBFetcher/__init__.py` - New integration function
2. `functions/LatrobeKBFetcher/function.json` - Function configuration
3. `tests/step1_test_api.py` - API testing
4. `tests/step2_test_integration.py` - Integration testing

### Modified Files:
1. `infrastructure/scripts/deploy-simplified.ps1` - Added missing environment variables

### Microsoft Files: **ZERO CHANGES** ✅
- FileUploadedFunc - unchanged
- FileLayoutParsingOther - unchanged  
- TextEnrichment - unchanged
- All other Microsoft functions - unchanged

## 🧪 Testing Strategy

1. **Unit Test**: Test LaTrobe API connection ✅
2. **Integration Test**: Test data conversion ✅  
3. **Pipeline Test**: Deploy and test full flow
4. **End-to-End Test**: Verify search results contain LaTrobe data

## 🎯 Benefits of This Approach

✅ **Minimal Risk**: No changes to proven Microsoft code
✅ **Easy Rollback**: Can remove LatrobeKBFetcher without affecting Microsoft pipeline
✅ **Step-by-Step**: Each step is independently testable
✅ **Future-Proof**: Can enhance integration without touching Microsoft code
✅ **Maintainable**: Clear separation between LaTrobe integration and Microsoft pipeline

## 🔄 How It Works

1. **LatrobeKBFetcher** fetches articles from LaTrobe API
2. **Converts** LaTrobe format to text format Microsoft expects
3. **Uploads** to Microsoft's `upload` container
4. **Microsoft FileUploadedFunc** automatically detects new files
5. **Existing Microsoft pipeline** processes files normally
6. **Search index** contains LaTrobe articles alongside other documents

**Result**: LaTrobe KB articles searchable through Microsoft PubSec-IA interface!
